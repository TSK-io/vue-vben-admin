from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PrivacyConsentRecord(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "privacy_consents"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="granted", server_default="granted")
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    granted_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    revoked_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    user: Mapped["User"] = relationship(back_populates="privacy_consents")


class PrivacyRequestRecord(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "privacy_requests"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="submitted", server_default="submitted")
    field_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    encrypted_payload: Mapped[str] = mapped_column(Text, nullable=False)
    review_comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    submitted_at: Mapped[str] = mapped_column(String(40), nullable=False)
    completed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    user: Mapped["User"] = relationship(back_populates="privacy_requests")


class AuditLog(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success", server_default="success")
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_ms: Mapped[str | None] = mapped_column(String(20), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="audit_logs")


if TYPE_CHECKING:
    from app.models.user import User
