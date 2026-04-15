from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.privacy import decrypt_text, encrypt_text, mask_phone
from app.db.session import session_scope
from app.models import AuditLog, NotificationRecord, PrivacyConsentRecord, PrivacyRequestRecord, User
from app.schemas.business import (
    AuditLogItem,
    PrivacyConsentGrantRequest,
    PrivacyConsentItem,
    PrivacyCorrectionRequest,
    PrivacyDeletionRequest,
    PrivacyExportResult,
    PrivacyPolicySummary,
    PrivacyRequestItem,
)
from app.schemas.user import UserProfile


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def get_policy_summary() -> PrivacyPolicySummary:
    return PrivacyPolicySummary(
        policy_version="2026.04",
        policy_url="/privacy/policy",
        privacy_url="/privacy/notice",
        consent_types=["privacy_policy", "risk_monitoring", "family_notification"],
        correction_supported_fields=["display_name", "phone"],
    )


def list_consents(user: UserProfile) -> list[PrivacyConsentItem]:
    with session_scope() as session:
        rows = session.scalars(
            select(PrivacyConsentRecord)
            .where(PrivacyConsentRecord.user_id == user.user_id)
            .order_by(PrivacyConsentRecord.created_at.desc())
        ).all()
        return [
            PrivacyConsentItem(
                id=item.id,
                consent_type=item.consent_type,
                policy_version=item.policy_version,
                status=item.status,
                granted_at=item.granted_at,
                revoked_at=item.revoked_at,
            )
            for item in rows
        ]


def grant_consent(user: UserProfile, payload: PrivacyConsentGrantRequest, ip_address: str | None, user_agent: str | None) -> PrivacyConsentItem:
    granted_at = _now_iso()
    with session_scope() as session:
        consent = PrivacyConsentRecord(
            user_id=user.user_id,
            consent_type=payload.consent_type,
            policy_version=payload.policy_version,
            status="granted",
            ip_address=ip_address,
            user_agent=user_agent,
            granted_at=granted_at,
        )
        session.add(consent)
        session.flush()
        session.add(
            AuditLog(
                user_id=user.user_id,
                action="grant_consent",
                module="compliance",
                target_type="privacy_consent",
                target_id=consent.id,
                status="success",
                ip_address=ip_address,
                details=json.dumps(
                    {"consent_type": payload.consent_type, "policy_version": payload.policy_version},
                    ensure_ascii=False,
                ),
            )
        )
        return PrivacyConsentItem(
            id=consent.id,
            consent_type=consent.consent_type,
            policy_version=consent.policy_version,
            status=consent.status,
            granted_at=consent.granted_at,
            revoked_at=consent.revoked_at,
        )


def export_user_data(user: UserProfile) -> PrivacyExportResult:
    generated_at = _now_iso()
    export_id = f"export-{uuid.uuid4().hex[:8]}"
    with session_scope() as session:
        db_user = session.get(User, user.user_id)
        notifications = session.scalars(
            select(NotificationRecord)
            .where(NotificationRecord.receiver_user_id == user.user_id)
            .order_by(NotificationRecord.sent_at.desc())
        ).all()

        accessibility_settings = {}
        notes = db_user.notes or ""
        for pair in notes.split(";"):
            if "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            if key in {"font_scale", "high_contrast", "voice_assistant", "voice_speed"}:
                accessibility_settings[key] = value

        session.add(
            AuditLog(
                user_id=user.user_id,
                action="export_user_data",
                module="compliance",
                target_type="user",
                target_id=user.user_id,
                status="success",
                details=json.dumps({"export_id": export_id}, ensure_ascii=False),
            )
        )
        return PrivacyExportResult(
            export_id=export_id,
            generated_at=generated_at,
            profile={
                "user_id": db_user.id,
                "username": db_user.username,
                "display_name": db_user.display_name,
                "phone": mask_phone(db_user.phone),
                "status": db_user.status,
                "roles": [role.code for role in {link.role for link in db_user.roles}],
            },
            bindings=[],
            notifications=[
                {
                    "id": item.id,
                    "title": item.title,
                    "channel": item.channel,
                    "status": item.status,
                    "is_read": item.is_read,
                    "sent_at": item.sent_at,
                }
                for item in notifications
            ],
            accessibility_settings=accessibility_settings,
        )


def submit_correction_request(user: UserProfile, payload: PrivacyCorrectionRequest) -> PrivacyRequestItem:
    submitted_at = _now_iso()
    body = json.dumps(payload.model_dump(), ensure_ascii=False)
    with session_scope() as session:
        request = PrivacyRequestRecord(
            user_id=user.user_id,
            request_type="correction",
            status="submitted",
            field_name=payload.field_name,
            encrypted_payload=encrypt_text(body),
            submitted_at=submitted_at,
        )
        session.add(request)
        session.flush()
        session.add(
            AuditLog(
                user_id=user.user_id,
                action="submit_correction_request",
                module="compliance",
                target_type="privacy_request",
                target_id=request.id,
                status="success",
                details=json.dumps({"field_name": payload.field_name}, ensure_ascii=False),
            )
        )
        return PrivacyRequestItem(
            id=request.id,
            request_type=request.request_type,
            status=request.status,
            field_name=request.field_name,
            payload=payload.model_dump(),
            review_comment=request.review_comment,
            submitted_at=request.submitted_at,
            completed_at=request.completed_at,
        )


def submit_deletion_request(user: UserProfile, payload: PrivacyDeletionRequest) -> PrivacyRequestItem:
    submitted_at = _now_iso()
    body = json.dumps(payload.model_dump(), ensure_ascii=False)
    with session_scope() as session:
        request = PrivacyRequestRecord(
            user_id=user.user_id,
            request_type="deletion",
            status="submitted",
            field_name=None,
            encrypted_payload=encrypt_text(body),
            submitted_at=submitted_at,
        )
        session.add(request)
        session.flush()
        session.add(
            AuditLog(
                user_id=user.user_id,
                action="submit_deletion_request",
                module="compliance",
                target_type="privacy_request",
                target_id=request.id,
                status="success",
                details=json.dumps({"reason": payload.reason}, ensure_ascii=False),
            )
        )
        return PrivacyRequestItem(
            id=request.id,
            request_type=request.request_type,
            status=request.status,
            field_name=request.field_name,
            payload=payload.model_dump(),
            review_comment=request.review_comment,
            submitted_at=request.submitted_at,
            completed_at=request.completed_at,
        )


def list_privacy_requests(user: UserProfile) -> list[PrivacyRequestItem]:
    with session_scope() as session:
        rows = session.scalars(
            select(PrivacyRequestRecord)
            .where(PrivacyRequestRecord.user_id == user.user_id)
            .order_by(PrivacyRequestRecord.created_at.desc())
        ).all()
        return [
            PrivacyRequestItem(
                id=item.id,
                request_type=item.request_type,
                status=item.status,
                field_name=item.field_name,
                payload=json.loads(decrypt_text(item.encrypted_payload)),
                review_comment=item.review_comment,
                submitted_at=item.submitted_at,
                completed_at=item.completed_at,
            )
            for item in rows
        ]


def list_audit_logs(user: UserProfile, limit: int = 20) -> list[AuditLogItem]:
    with session_scope() as session:
        rows = session.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user.user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        ).all()
        return [
            AuditLogItem(
                id=item.id,
                request_id=item.request_id,
                action=item.action,
                module=item.module,
                status=item.status,
                method=item.method,
                path=item.path,
                duration_ms=item.duration_ms,
                created_at=item.created_at.isoformat().replace("+00:00", "Z") if item.created_at else None,
            )
            for item in rows
        ]
