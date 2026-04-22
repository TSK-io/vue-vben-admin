"""chat guardrails and audit tables

Revision ID: 20260421_0003
Revises: 20260420_0002
Create Date: 2026-04-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260421_0003"
down_revision = "20260420_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_user_relations",
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("target_user_id", sa.String(length=36), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_reported", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("report_reason", sa.Text(), nullable=True),
        sa.Column("blocked_at", sa.String(length=40), nullable=True),
        sa.Column("reported_at", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_user_id", "target_user_id", name="uq_chat_user_relations_owner_target"),
    )
    op.create_index(op.f("ix_chat_user_relations_owner_user_id"), "chat_user_relations", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_chat_user_relations_target_user_id"), "chat_user_relations", ["target_user_id"], unique=False)

    op.create_table(
        "chat_audit_logs",
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("target_user_id", sa.String(length=36), nullable=True),
        sa.Column("conversation_id", sa.String(length=36), nullable=True),
        sa.Column("message_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("detail_json", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_audit_logs_action"), "chat_audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_chat_audit_logs_actor_user_id"), "chat_audit_logs", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_chat_audit_logs_conversation_id"), "chat_audit_logs", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_chat_audit_logs_message_id"), "chat_audit_logs", ["message_id"], unique=False)
    op.create_index(op.f("ix_chat_audit_logs_target_user_id"), "chat_audit_logs", ["target_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_audit_logs_target_user_id"), table_name="chat_audit_logs")
    op.drop_index(op.f("ix_chat_audit_logs_message_id"), table_name="chat_audit_logs")
    op.drop_index(op.f("ix_chat_audit_logs_conversation_id"), table_name="chat_audit_logs")
    op.drop_index(op.f("ix_chat_audit_logs_actor_user_id"), table_name="chat_audit_logs")
    op.drop_index(op.f("ix_chat_audit_logs_action"), table_name="chat_audit_logs")
    op.drop_table("chat_audit_logs")

    op.drop_index(op.f("ix_chat_user_relations_target_user_id"), table_name="chat_user_relations")
    op.drop_index(op.f("ix_chat_user_relations_owner_user_id"), table_name="chat_user_relations")
    op.drop_table("chat_user_relations")
