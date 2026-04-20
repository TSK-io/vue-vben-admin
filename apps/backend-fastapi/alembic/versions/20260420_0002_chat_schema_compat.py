"""chat schema compatibility upgrade

Revision ID: 20260420_0002
Revises: 20260414_0001
Create Date: 2026-04-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260420_0002"
down_revision = "20260414_0001"
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    if not _has_table(inspector, table_name):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(
    inspector: sa.Inspector,
    table_name: str,
    column: sa.Column,
) -> None:
    if column.name not in _column_names(inspector, table_name):
        op.add_column(table_name, column)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "chat_conversations"):
        _add_column_if_missing(inspector, "chat_conversations", sa.Column("title", sa.String(length=100), nullable=True))
        _add_column_if_missing(
            inspector,
            "chat_conversations",
            sa.Column("last_message_preview", sa.String(length=255), nullable=True),
        )
        _add_column_if_missing(
            inspector,
            "chat_conversations",
            sa.Column("last_message_at", sa.String(length=40), nullable=True),
        )

    inspector = sa.inspect(bind)
    if _has_table(inspector, "chat_conversation_members"):
        _add_column_if_missing(
            inspector,
            "chat_conversation_members",
            sa.Column("joined_at", sa.String(length=40), nullable=True),
        )
        _add_column_if_missing(
            inspector,
            "chat_conversation_members",
            sa.Column("last_read_at", sa.String(length=40), nullable=True),
        )
        _add_column_if_missing(
            inspector,
            "chat_conversation_members",
            sa.Column(
                "is_muted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

    inspector = sa.inspect(bind)
    if _has_table(inspector, "chat_messages"):
        columns = _column_names(inspector, "chat_messages")
        if "content_text" not in columns:
            op.add_column("chat_messages", sa.Column("content_text", sa.Text(), nullable=True))
            if "content" in columns:
                op.execute("UPDATE chat_messages SET content_text = content WHERE content_text IS NULL")
            op.alter_column("chat_messages", "content_text", nullable=False)
        _add_column_if_missing(inspector, "chat_messages", sa.Column("content_json", sa.Text(), nullable=True))
        _add_column_if_missing(inspector, "chat_messages", sa.Column("read_by_all_at", sa.String(length=40), nullable=True))
        _add_column_if_missing(
            inspector,
            "chat_messages",
            sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="low"),
        )
        _add_column_if_missing(inspector, "chat_messages", sa.Column("risk_category", sa.String(length=50), nullable=True))
        _add_column_if_missing(inspector, "chat_messages", sa.Column("risk_reason", sa.Text(), nullable=True))
        _add_column_if_missing(inspector, "chat_messages", sa.Column("risk_suggestion", sa.Text(), nullable=True))

        columns = _column_names(sa.inspect(bind), "chat_messages")
        if "read_by_all_at" in columns and "read_at" in columns:
            op.execute("UPDATE chat_messages SET read_by_all_at = read_at WHERE read_by_all_at IS NULL AND read_at IS NOT NULL")


def downgrade() -> None:
    pass
