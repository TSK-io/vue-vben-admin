from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ChatConversation(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_conversations"

    conversation_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="direct", server_default="direct"
    )
    pair_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    last_message_preview: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_message_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    members: Mapped[list["ChatConversationMember"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class ChatConversationMember(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_conversation_members"
    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "user_id",
            name="uq_chat_conversation_members_conversation_user",
        ),
    )

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    joined_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    last_read_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    last_read_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    unread_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_muted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    conversation: Mapped["ChatConversation"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class ChatMessage(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text", server_default="text")
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="sent", server_default="sent")
    delivered_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    read_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    client_message_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    read_by_all_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low", server_default="low")
    risk_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)

    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()


class ChatInstancePresence(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_instance_presence"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    connection_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="online", server_default="online")
    last_seen_at: Mapped[str] = mapped_column(String(40), nullable=False)
    client_type: Mapped[str] = mapped_column(String(20), nullable=False, default="web", server_default="web")

    user: Mapped["User"] = relationship()


class ChatUserRelation(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_user_relations"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "target_user_id", name="uq_chat_user_relations_owner_target"),
    )

    owner_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_reported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    report_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    blocked_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reported_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_user_id])
    target: Mapped["User"] = relationship(foreign_keys=[target_user_id])


class ChatAuditLog(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_audit_logs"

    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    conversation_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    message_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    detail_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    actor: Mapped["User"] = relationship(foreign_keys=[actor_user_id])
    target: Mapped["User"] = relationship(foreign_keys=[target_user_id])


class CallSession(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "call_sessions"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    initiator_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    call_type: Mapped[str] = mapped_column(String(20), nullable=False, default="audio", server_default="audio")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="initiated", server_default="initiated")
    started_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    answered_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ended_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ended_reason: Mapped[str | None] = mapped_column(String(40), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    offer_sdp: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_sdp: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_ice_candidate: Mapped[str | None] = mapped_column(Text, nullable=True)

    conversation: Mapped["ChatConversation"] = relationship()
    initiator: Mapped["User"] = relationship(foreign_keys=[initiator_user_id])
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_user_id])
    participants: Mapped[list["CallParticipant"]] = relationship(
        back_populates="call_session", cascade="all, delete-orphan"
    )
    events: Mapped[list["CallEvent"]] = relationship(
        back_populates="call_session", cascade="all, delete-orphan"
    )


class CallParticipant(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "call_participants"
    __table_args__ = (UniqueConstraint("call_session_id", "user_id", name="uq_call_participants_call_user"),)

    call_session_id: Mapped[str] = mapped_column(
        ForeignKey("call_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="participant", server_default="participant")
    join_state: Mapped[str] = mapped_column(String(20), nullable=False, default="invited", server_default="invited")
    joined_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    left_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    call_session: Mapped["CallSession"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()


class CallEvent(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "call_events"

    call_session_id: Mapped[str] = mapped_column(
        ForeignKey("call_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    call_session: Mapped["CallSession"] = relationship(back_populates="events")
    actor: Mapped["User"] = relationship(foreign_keys=[actor_user_id])


if TYPE_CHECKING:
    from app.models.user import User
