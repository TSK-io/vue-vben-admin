from __future__ import annotations

import json
from datetime import UTC, datetime
from urllib.parse import quote, unquote

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import aliased, selectinload

from app.constants.roles import UserRole
from app.db.session import session_scope
from app.models import (
    AuditLog,
    CallRecognitionRecord,
    EducationContent,
    ElderFamilyBinding,
    NotificationRecord,
    PromptTemplate,
    Role,
    RiskAlert,
    RiskLexiconTerm,
    RiskRule,
    SystemConfig,
    User,
    UserRoleLink,
    Workorder,
    WorkorderAction,
    SmsRecognitionRecord,
)
from app.schemas.business import (
    AdminUserItem,
    AdminUserDetail,
    AdminUserPasswordResetRequest,
    AdminUserPhoneUpdateRequest,
    AdminUserUpsertRequest,
    AdminRiskAlertItem,
    AdminRiskAlertDetail,
    AccessibilitySettings,
    AccessibilitySettingsUpdateRequest,
    BindingCreateRequest,
    BindingItem,
    BindingUpdateRequest,
    CommunityReportData,
    ContentUpsertRequest,
    CommunityElderItem,
    CommunityElderFollowupRequest,
    ContentItem,
    EducationContentItem,
    FamilyReminderCreateRequest,
    FamilyReminderResult,
    FamilyReminderReceiptItem,
    FamilyReminderTemplateItem,
    FamilyReminderTemplateUpsertRequest,
    HelpRequestCreate,
    HelpRequestResult,
    NotificationItem,
    NotificationActionRequest,
    NotificationActionResult,
    NotificationReadResult,
    PaginationMeta,
    PagedResult,
    RiskAlertDetail,
    RiskAlertItem,
    RiskLexiconItem,
    RiskLexiconUpsertRequest,
    RiskRuleItem,
    RoleUpsertRequest,
    RiskRuleUpsertRequest,
    RoleInfo,
    SystemConfigItem,
    SystemConfigUpdateRequest,
    WorkorderActionItem,
    WorkorderDetail,
    WorkorderItem,
    WorkorderTransitionRequest,
)
from app.schemas.user import UserProfile
from app.services.db_init import ROLE_DETAILS


def _paginate[T](items: list[T], page: int, page_size: int) -> PagedResult:
    start = (page - 1) * page_size
    end = start + page_size
    return PagedResult(
        items=items[start:end],
        pagination=PaginationMeta(page=page, page_size=page_size, total=len(items)),
    )


def _to_str(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return value


def _parse_notes(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    result: dict[str, str] = {}
    for pair in raw.split(";"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        result[key] = value
    return result


def _dump_notes(values: dict[str, str]) -> str:
    return ";".join(f"{key}={value}" for key, value in values.items())


def _load_note_json(notes: dict[str, str], key: str, default):
    raw = notes.get(key)
    if not raw:
        return default
    try:
        return json.loads(unquote(raw))
    except (TypeError, ValueError):
        return default


def _dump_note_json(value) -> str:
    return quote(json.dumps(value, ensure_ascii=False), safe="")


def _load_action_note(note: str | None) -> tuple[str | None, list[str], str | None]:
    if not note:
        return None, [], None
    if not note.startswith("__json__:"):
        return note, [], None
    try:
        payload = json.loads(note.removeprefix("__json__:"))
    except ValueError:
        return note, [], None
    return (
        payload.get("note"),
        [str(item) for item in payload.get("attachments", [])],
        payload.get("collaboration_note"),
    )


def _dump_action_note(
    note: str | None,
    attachments: list[str] | None = None,
    collaboration_note: str | None = None,
) -> str | None:
    attachments = [item for item in (attachments or []) if item]
    if not attachments and not collaboration_note:
        return note
    return "__json__:" + json.dumps(
        {
            "note": note,
            "attachments": attachments,
            "collaboration_note": collaboration_note,
        },
        ensure_ascii=False,
    )


def _parse_version_history(raw: str | None) -> list[dict[str, str | int]]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    if not isinstance(data, list):
        return []
    result: list[dict[str, str | int]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        version = item.get("version")
        status = item.get("status")
        updated_at = item.get("updated_at")
        operator = item.get("operator")
        if not isinstance(version, int):
            continue
        result.append(
            {
                "version": version,
                "status": str(status or ""),
                "updated_at": str(updated_at or ""),
                "operator": str(operator or ""),
            }
        )
    return result


def _load_rule_version_history(session, rule_id: str) -> list[dict[str, str | int]]:
    item = session.scalar(select(SystemConfig).where(SystemConfig.key == f"rule.{rule_id}.versions"))
    if not item:
        return []
    return _parse_version_history(item.value)


def _save_rule_version_history(
    session,
    *,
    rule_id: str,
    history: list[dict[str, str | int]],
) -> None:
    key = f"rule.{rule_id}.versions"
    value = json.dumps(history, ensure_ascii=False)
    item = session.scalar(select(SystemConfig).where(SystemConfig.key == key))
    if item:
        item.value = value
        item.name = f"规则 {rule_id} 版本记录"
        item.group = "risk-rule"
        item.description = "风险规则版本快照记录。"
        return
    session.add(
        SystemConfig(
            key=key,
            name=f"规则 {rule_id} 版本记录",
            value=value,
            group="risk-rule",
            description="风险规则版本快照记录。",
        )
    )


def _append_rule_version(
    session,
    *,
    rule_id: str,
    status: str,
    operator: str,
    updated_at: str,
) -> list[dict[str, str | int]]:
    history = _load_rule_version_history(session, rule_id)
    next_version = max((int(item["version"]) for item in history), default=0) + 1
    history.append(
        {
            "version": next_version,
            "status": status,
            "updated_at": updated_at,
            "operator": operator,
        }
    )
    _save_rule_version_history(session, rule_id=rule_id, history=history)
    return history


ROLE_MENU_DEFAULTS: dict[str, list[str]] = {
    "admin": ["用户管理", "角色权限", "风险规则", "内容管理", "系统配置", "告警记录"],
    "community": ["辖区总览", "重点老人", "风险工单", "宣教管理", "统计报表"],
    "elder": ["首页", "风险提醒", "一键求助", "亲属绑定", "防骗知识", "适老设置"],
    "family": ["监护总览", "老人列表", "风险详情", "通知记录", "监护设置"],
}


def get_paged_payload(items: list, page: int, page_size: int) -> PagedResult:
    return _paginate(items, page, page_size)


def _get_role_config(session, role_code: str) -> dict[str, object]:
    item = session.scalar(select(SystemConfig).where(SystemConfig.key == f"role.{role_code}.config"))
    if not item or not item.value:
        return {}
    try:
        return json.loads(item.value)
    except ValueError:
        return {}


def _upsert_role_config(session, role_code: str, payload: RoleUpsertRequest) -> None:
    value = json.dumps(
        {
            "menus": payload.menus,
            "button_permissions": payload.button_permissions,
            "api_permissions": payload.api_permissions,
            "data_scope": payload.data_scope,
            "permissions": payload.permissions,
        },
        ensure_ascii=False,
    )
    item = session.scalar(select(SystemConfig).where(SystemConfig.key == f"role.{role_code}.config"))
    if item:
        item.value = value
        item.name = f"{payload.name}权限配置"
        item.description = "角色菜单、按钮、接口和数据范围配置。"
        return
    session.add(
        SystemConfig(
            key=f"role.{role_code}.config",
            name=f"{payload.name}权限配置",
            value=value,
            group="role",
            description="角色菜单、按钮、接口和数据范围配置。",
        )
    )


def list_roles() -> list[RoleInfo]:
    with session_scope() as session:
        rows = session.execute(
            select(UserRoleLink.role_id, func.count(UserRoleLink.user_id)).group_by(UserRoleLink.role_id)
        ).all()
        counts = {role_id: count for role_id, count in rows}

        role_rows = session.execute(select(UserRoleLink).options(selectinload(UserRoleLink.role))).scalars().all()
        role_id_to_code = {link.role_id: UserRole(link.role.code) for link in role_rows}
        role_counts = {role: 0 for role in ROLE_DETAILS}
        for role_id, count in counts.items():
            role = role_id_to_code.get(role_id)
            if role:
                role_counts[role] = count

        results: list[RoleInfo] = []
        role_rows = session.execute(select(Role).order_by(Role.created_at.asc())).scalars().all()
        for role_row in role_rows:
            config = _get_role_config(session, role_row.code)
            detail = ROLE_DETAILS.get(
                UserRole(role_row.code),
                {
                    "name": role_row.name,
                    "description": role_row.description or "",
                    "permissions": config.get("permissions", []),
                },
            )
            permissions = [str(item) for item in config.get("permissions", detail["permissions"])]
            button_permissions = [str(item) for item in config.get("button_permissions", [])]
            api_permissions = [str(item) for item in config.get("api_permissions", permissions)]
            menus = [str(item) for item in config.get("menus", ROLE_MENU_DEFAULTS.get(role_row.code, []))]
            role_code = UserRole(role_row.code)
            results.append(
                RoleInfo(
                    code=role_code,
                    name=role_row.name or str(detail["name"]),
                    description=role_row.description or str(detail["description"]),
                    permissions=permissions,
                    user_count=role_counts.get(role_code, 0),
                    menus=menus,
                    button_permissions=button_permissions,
                    api_permissions=api_permissions,
                    data_scope=str(config.get("data_scope", "self")),
                    is_system=role_row.is_system,
                )
            )
        return results


def list_admin_users(keyword: str | None = None, role: UserRole | None = None) -> list[AdminUserItem]:
    with session_scope() as session:
        query = select(User).options(selectinload(User.roles).selectinload(UserRoleLink.role))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(or_(User.username.ilike(pattern), User.display_name.ilike(pattern)))
        users = session.execute(query.order_by(User.created_at.asc())).scalars().all()

        result: list[AdminUserItem] = []
        for user in users:
            roles = [UserRole(link.role.code) for link in user.roles]
            if role and role not in roles:
                continue
            permissions: list[str] = []
            for role_item in roles:
                permissions.extend(str(item) for item in ROLE_DETAILS[role_item]["permissions"])
            latest_alert = session.scalar(
                select(RiskAlert).where(RiskAlert.elder_user_id == user.id).order_by(RiskAlert.occurred_at.desc())
            )
            bind_count = session.scalar(
                select(func.count(ElderFamilyBinding.id)).where(
                    or_(
                        ElderFamilyBinding.elder_user_id == user.id,
                        ElderFamilyBinding.family_user_id == user.id,
                    )
                )
            )
            result.append(
                AdminUserItem(
                    user_id=user.id,
                    username=user.username,
                    display_name=user.display_name,
                    phone=user.phone,
                    status=user.status,
                    roles=roles,
                    permissions=list(dict.fromkeys(permissions)),
                    last_login_at=user.last_login_at,
                    bind_count=bind_count or 0,
                    latest_alert_at=latest_alert.occurred_at if latest_alert else None,
                    latest_risk_level=latest_alert.risk_level if latest_alert else "low",
                    notes=_parse_notes(user.notes),
                )
            )
        return result


def get_admin_user_detail(user_id: str) -> AdminUserDetail:
    base_item = next((item for item in list_admin_users() if item.user_id == user_id), None)
    if not base_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    with session_scope() as session:
        user = session.execute(
            select(User).options(selectinload(User.roles).selectinload(UserRoleLink.role)).where(User.id == user_id)
        ).scalar_one()
        binding_ids = session.scalars(
            select(ElderFamilyBinding.id).where(
                or_(
                    ElderFamilyBinding.elder_user_id == user.id,
                    ElderFamilyBinding.family_user_id == user.id,
                )
            )
        ).all()
        latest_alert = session.scalar(
            select(RiskAlert).where(RiskAlert.elder_user_id == user.id).order_by(RiskAlert.occurred_at.desc())
        )
        roles = [UserRole(link.role.code) for link in user.roles]
        return AdminUserDetail(
            **base_item.model_dump(),
            role_descriptions=[str(ROLE_DETAILS[role]["description"]) for role in roles],
            binding_ids=list(binding_ids),
            latest_alert_title=latest_alert.title if latest_alert else None,
        )


def create_admin_user(payload: AdminUserUpsertRequest) -> AdminUserDetail:
    with session_scope() as session:
        if session.scalar(select(User.id).where(User.username == payload.username)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
        if session.scalar(select(User.id).where(User.phone == payload.phone)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="手机号已存在")
        user = User(
            username=payload.username,
            password_hash=payload.password or "111",
            display_name=payload.display_name,
            phone=payload.phone,
            status=payload.status,
            notes=_dump_notes(payload.notes),
        )
        session.add(user)
        session.flush()
        roles = session.execute(select(Role).where(Role.code.in_([item.value for item in payload.roles]))).scalars().all()
        for role_item in roles:
            session.add(UserRoleLink(user_id=user.id, role_id=role_item.id))
        session.flush()
        created_id = user.id
    return get_admin_user_detail(created_id)


def update_admin_user(user_id: str, payload: AdminUserUpsertRequest) -> AdminUserDetail:
    with session_scope() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.username = payload.username
        user.display_name = payload.display_name
        user.phone = payload.phone
        user.status = payload.status
        user.notes = _dump_notes(payload.notes)
        if payload.password:
            user.password_hash = payload.password
        session.query(UserRoleLink).where(UserRoleLink.user_id == user_id).delete()
        roles = session.execute(select(Role).where(Role.code.in_([item.value for item in payload.roles]))).scalars().all()
        for role_item in roles:
            session.add(UserRoleLink(user_id=user.id, role_id=role_item.id))
        session.flush()
    return get_admin_user_detail(user_id)


def reset_admin_user_password(user_id: str, payload: AdminUserPasswordResetRequest) -> dict[str, str]:
    with session_scope() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.password_hash = payload.password
        return {"status": "password_reset", "user_id": user.id}


def update_admin_user_phone(user_id: str, payload: AdminUserPhoneUpdateRequest) -> dict[str, str]:
    with session_scope() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.phone = payload.phone
        return {"status": "phone_updated", "user_id": user.id, "phone": user.phone}


def create_role(payload: RoleUpsertRequest) -> RoleInfo:
    role_code = payload.code.strip()
    try:
        user_role = UserRole(role_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="角色编码不受支持") from exc
    with session_scope() as session:
        if session.scalar(select(Role.id).where(Role.code == role_code)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="角色已存在")
        role = Role(code=role_code, name=payload.name, description=payload.description, is_system=False)
        session.add(role)
        session.flush()
        _upsert_role_config(session, role_code, payload)
    return next(item for item in list_roles() if item.code == user_role)


def update_role(role_code: str, payload: RoleUpsertRequest) -> RoleInfo:
    with session_scope() as session:
        role = session.scalar(select(Role).where(Role.code == role_code))
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
        role.name = payload.name
        role.description = payload.description
        _upsert_role_config(session, role_code, payload)
    return next(item for item in list_roles() if item.code == UserRole(role_code))


def list_bindings(user: UserProfile) -> list[BindingItem]:
    ElderUser = aliased(User)
    FamilyUser = aliased(User)
    with session_scope() as session:
        query = (
            select(ElderFamilyBinding, ElderUser.display_name, FamilyUser.display_name)
            .join(ElderUser, ElderFamilyBinding.elder_user_id == ElderUser.id)
            .join(FamilyUser, ElderFamilyBinding.family_user_id == FamilyUser.id)
        )
        if UserRole.FAMILY in user.roles:
            query = query.where(ElderFamilyBinding.family_user_id == user.user_id)
        elif UserRole.ELDER in user.roles:
            query = query.where(ElderFamilyBinding.elder_user_id == user.user_id)

        rows = session.execute(query.order_by(ElderFamilyBinding.created_at.desc())).all()
        return [
            BindingItem(
                id=binding.id,
                elder_user_id=binding.elder_user_id,
                elder_name=elder_name,
                family_user_id=binding.family_user_id,
                family_name=family_name,
                relationship_type=binding.relationship_type,
                status=binding.status,
                is_emergency_contact=binding.is_emergency_contact,
                authorized_at=binding.authorized_at or "",
            )
            for binding, elder_name, family_name in rows
        ]


def create_binding(payload: BindingCreateRequest) -> BindingItem:
    with session_scope() as session:
        existing = session.scalar(
            select(ElderFamilyBinding).where(
                ElderFamilyBinding.elder_user_id == payload.elder_user_id,
                ElderFamilyBinding.family_user_id == payload.family_user_id,
            )
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="绑定关系已存在")

        elder = session.get(User, payload.elder_user_id)
        family = session.get(User, payload.family_user_id)
        if not elder or not family:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定用户不存在")

        binding = ElderFamilyBinding(
            elder_user_id=payload.elder_user_id,
            family_user_id=payload.family_user_id,
            relationship_type=payload.relationship_type,
            is_emergency_contact=payload.is_emergency_contact,
            status="active",
            authorized_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
        session.add(binding)
        session.flush()
        return BindingItem(
            id=binding.id,
            elder_user_id=binding.elder_user_id,
            elder_name=elder.display_name,
            family_user_id=binding.family_user_id,
            family_name=family.display_name,
            relationship_type=binding.relationship_type,
            status=binding.status,
            is_emergency_contact=binding.is_emergency_contact,
            authorized_at=binding.authorized_at or "",
        )


def update_binding(binding_id: str, payload: BindingUpdateRequest) -> BindingItem:
    with session_scope() as session:
        binding = session.get(ElderFamilyBinding, binding_id)
        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定关系不存在")
        if payload.relationship_type is not None:
            binding.relationship_type = payload.relationship_type
        if payload.status is not None:
            binding.status = payload.status
        if payload.is_emergency_contact is not None:
            binding.is_emergency_contact = payload.is_emergency_contact
        elder = session.get(User, binding.elder_user_id)
        family = session.get(User, binding.family_user_id)
        return BindingItem(
            id=binding.id,
            elder_user_id=binding.elder_user_id,
            elder_name=elder.display_name if elder else "",
            family_user_id=binding.family_user_id,
            family_name=family.display_name if family else "",
            relationship_type=binding.relationship_type,
            status=binding.status,
            is_emergency_contact=binding.is_emergency_contact,
            authorized_at=binding.authorized_at or "",
        )


def delete_binding(binding_id: str) -> None:
    with session_scope() as session:
        binding = session.get(ElderFamilyBinding, binding_id)
        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定关系不存在")
        session.delete(binding)


def list_risk_alerts(user: UserProfile, risk_level: str | None = None) -> list[RiskAlertItem]:
    ElderUser = aliased(User)
    with session_scope() as session:
        query = select(RiskAlert, ElderUser.display_name).join(ElderUser, RiskAlert.elder_user_id == ElderUser.id)
        if risk_level:
            query = query.where(RiskAlert.risk_level == risk_level)
        if UserRole.FAMILY in user.roles:
            binding_subquery = select(ElderFamilyBinding.elder_user_id).where(ElderFamilyBinding.family_user_id == user.user_id)
            query = query.where(RiskAlert.elder_user_id.in_(binding_subquery))
        elif UserRole.ELDER in user.roles:
            query = query.where(RiskAlert.elder_user_id == user.user_id)
        rows = session.execute(query.order_by(RiskAlert.occurred_at.desc())).all()
        return [
            RiskAlertItem(
                id=alert.id,
                elder_user_id=alert.elder_user_id,
                elder_name=elder_name,
                source_type=alert.source_type,
                risk_level=alert.risk_level,
                risk_score=alert.risk_score,
                title=alert.title,
                summary=alert.summary,
                status=alert.status,
                occurred_at=alert.occurred_at,
            )
            for alert, elder_name in rows
        ]


def get_risk_alert_detail(alert_id: str) -> RiskAlertDetail:
    ElderUser = aliased(User)
    with session_scope() as session:
        row = session.execute(
            select(RiskAlert, ElderUser.display_name)
            .join(ElderUser, RiskAlert.elder_user_id == ElderUser.id)
            .where(RiskAlert.id == alert_id)
        ).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="风险告警不存在")
        alert, elder_name = row
        notification_ids = session.scalars(
            select(NotificationRecord.id).where(NotificationRecord.alert_id == alert.id)
        ).all()
        workorder_ids = session.scalars(select(Workorder.id).where(Workorder.alert_id == alert.id)).all()
        hit_rule_codes: list[str] = []
        if alert.source_type == "sms" and alert.source_record_id:
            record = session.get(SmsRecognitionRecord, alert.source_record_id)
            if record and record.hit_rule_codes:
                hit_rule_codes = [item for item in record.hit_rule_codes.split(",") if item]
        if alert.source_type == "call" and alert.source_record_id:
            record = session.get(CallRecognitionRecord, alert.source_record_id)
            if record and record.hit_rule_codes:
                hit_rule_codes = [item for item in record.hit_rule_codes.split(",") if item]
        return RiskAlertDetail(
            id=alert.id,
            elder_user_id=alert.elder_user_id,
            elder_name=elder_name,
            source_type=alert.source_type,
            risk_level=alert.risk_level,
            risk_score=alert.risk_score,
            title=alert.title,
            summary=alert.summary,
            status=alert.status,
            occurred_at=alert.occurred_at,
            reason_detail=alert.reason_detail or "",
            suggestion_action=alert.suggestion_action or "",
            hit_rule_codes=hit_rule_codes,
            related_notification_ids=list(notification_ids),
            related_workorder_ids=list(workorder_ids),
        )


def list_notifications(user: UserProfile, is_read: bool | None = None) -> list[NotificationItem]:
    ReceiverUser = aliased(User)
    with session_scope() as session:
        query = (
            select(NotificationRecord, ReceiverUser.display_name, RiskAlert.title)
            .join(ReceiverUser, NotificationRecord.receiver_user_id == ReceiverUser.id)
            .join(RiskAlert, NotificationRecord.alert_id == RiskAlert.id)
            .where(NotificationRecord.receiver_user_id == user.user_id)
        )
        if is_read is not None:
            query = query.where(NotificationRecord.is_read == is_read)
        rows = session.execute(query.order_by(NotificationRecord.sent_at.desc())).all()
        return [
            NotificationItem(
                id=item.id,
                receiver_user_id=item.receiver_user_id,
                receiver_name=receiver_name,
                alert_id=item.alert_id,
                alert_title=alert_title,
                channel=item.channel,
                notification_type=item.notification_type,
                title=item.title,
                content=item.content,
                status=item.status,
                is_read=item.is_read,
                sent_at=item.sent_at or "",
            )
            for item, receiver_name, alert_title in rows
        ]


def mark_notification_read(notification_id: str, user: UserProfile) -> NotificationReadResult:
    with session_scope() as session:
        item = session.get(NotificationRecord, notification_id)
        if not item or item.receiver_user_id != user.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
        item.is_read = True
        item.read_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        return NotificationReadResult(id=item.id, is_read=item.is_read, read_at=item.read_at)


def update_notification_action(
    notification_id: str,
    payload: NotificationActionRequest,
    user: UserProfile,
) -> NotificationActionResult:
    with session_scope() as session:
        item = session.get(NotificationRecord, notification_id)
        if not item or item.receiver_user_id != user.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
        item.status = payload.status
        if payload.note:
            item.content = f"{item.content}\n跟进备注：{payload.note}"
        if not item.is_read:
            item.is_read = True
            item.read_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        return NotificationActionResult(
            id=item.id,
            is_read=item.is_read,
            read_at=item.read_at,
            status=item.status,
            note=payload.note,
        )


def create_help_request(user: UserProfile, payload: HelpRequestCreate) -> HelpRequestResult:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    notification_ids: list[str] = []
    with session_scope() as session:
        current_user = session.get(User, user.user_id)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        latest_alert = session.scalar(
            select(RiskAlert)
            .where(RiskAlert.elder_user_id == user.user_id)
            .order_by(RiskAlert.occurred_at.desc())
        )
        if payload.notify_family:
            family_bindings = session.execute(
                select(ElderFamilyBinding).where(ElderFamilyBinding.elder_user_id == user.user_id)
            ).scalars().all()
            for binding in family_bindings:
                notification = NotificationRecord(
                    alert_id=(latest_alert.id if latest_alert else "alert-001"),
                    receiver_user_id=binding.family_user_id,
                    channel="app",
                    notification_type="help_request",
                    title=f"{current_user.display_name} 发起一键求助",
                    content=payload.note or "老人发起求助，请尽快回电确认。",
                    status="sent",
                    is_read=False,
                    sent_at=now,
                )
                session.add(notification)
                session.flush()
                notification_ids.append(notification.id)
        if payload.notify_community:
            community_users = session.execute(
                select(User)
                .join(User.roles)
                .join(UserRoleLink.role)
                .where(Role.code == UserRole.COMMUNITY.value)
            ).scalars().all()
            for community_user in community_users[:1]:
                notification = NotificationRecord(
                    alert_id=(latest_alert.id if latest_alert else "alert-001"),
                    receiver_user_id=community_user.id,
                    channel="workbench",
                    notification_type="help_request",
                    title=f"{current_user.display_name} 需要协助",
                    content=payload.note or "老人发起求助，请安排回访。",
                    status="sent",
                    is_read=False,
                    sent_at=now,
                )
                session.add(notification)
                session.flush()
                notification_ids.append(notification.id)
        return HelpRequestResult(
            help_id=f"help-{user.user_id}-{int(datetime.now(UTC).timestamp())}",
            action_type=payload.action_type,
            created_at=now,
            notification_ids=notification_ids,
            summary="已向家属/社区发送求助通知并记录留痕。",
        )


def send_family_reminder(user: UserProfile, payload: FamilyReminderCreateRequest) -> FamilyReminderResult:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    with session_scope() as session:
        elder = session.get(User, payload.elder_user_id)
        if not elder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="老人不存在")
        latest_alert = session.scalar(
            select(RiskAlert)
            .where(RiskAlert.elder_user_id == payload.elder_user_id)
            .order_by(RiskAlert.occurred_at.desc())
        )
        notification = NotificationRecord(
            alert_id=(latest_alert.id if latest_alert else "alert-001"),
            receiver_user_id=payload.elder_user_id,
            channel=payload.channel,
            notification_type="family_reminder",
            title=f"{user.display_name} 向您发送了提醒",
            content=payload.content,
            status="sent",
            is_read=False,
            sent_at=now,
        )
        session.add(notification)
        session.flush()
        return FamilyReminderResult(
            notification_id=notification.id,
            sent_at=now,
            receiver_name=elder.display_name,
            content=payload.content,
            receipt_status="delivered",
        )


def list_family_reminder_templates() -> list[FamilyReminderTemplateItem]:
    with session_scope() as session:
        rows = session.execute(
            select(PromptTemplate)
            .where(PromptTemplate.category == "family_reminder")
            .order_by(PromptTemplate.updated_at.desc())
        ).scalars().all()
        return [
            FamilyReminderTemplateItem(
                id=item.id,
                code=item.code,
                name=item.name,
                channel=item.channel,
                content=item.content,
                status=item.status,
                is_default=item.is_default,
                notes=item.notes,
            )
            for item in rows
        ]


def create_family_reminder_template(
    payload: FamilyReminderTemplateUpsertRequest,
) -> FamilyReminderTemplateItem:
    with session_scope() as session:
        item = PromptTemplate(
            code=payload.code,
            name=payload.name,
            category="family_reminder",
            channel=payload.channel,
            content=payload.content,
            status=payload.status,
            is_default=payload.is_default,
            notes=payload.notes,
        )
        session.add(item)
        session.flush()
        return FamilyReminderTemplateItem(
            id=item.id,
            code=item.code,
            name=item.name,
            channel=item.channel,
            content=item.content,
            status=item.status,
            is_default=item.is_default,
            notes=item.notes,
        )


def update_family_reminder_template(
    template_id: str,
    payload: FamilyReminderTemplateUpsertRequest,
) -> FamilyReminderTemplateItem:
    with session_scope() as session:
        item = session.get(PromptTemplate, template_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提醒模板不存在")
        item.code = payload.code
        item.name = payload.name
        item.channel = payload.channel
        item.content = payload.content
        item.status = payload.status
        item.is_default = payload.is_default
        item.notes = payload.notes
        return FamilyReminderTemplateItem(
            id=item.id,
            code=item.code,
            name=item.name,
            channel=item.channel,
            content=item.content,
            status=item.status,
            is_default=item.is_default,
            notes=item.notes,
        )


def list_family_reminder_receipts(user: UserProfile) -> list[FamilyReminderReceiptItem]:
    with session_scope() as session:
        elder_ids = session.scalars(
            select(ElderFamilyBinding.elder_user_id).where(ElderFamilyBinding.family_user_id == user.user_id)
        ).all()
        if not elder_ids:
            return []
        rows = session.execute(
            select(NotificationRecord, User.display_name)
            .join(User, NotificationRecord.receiver_user_id == User.id)
            .where(
                NotificationRecord.receiver_user_id.in_(elder_ids),
                NotificationRecord.notification_type == "family_reminder",
            )
            .order_by(NotificationRecord.sent_at.desc())
        ).all()
        return [
            FamilyReminderReceiptItem(
                notification_id=item.id,
                elder_user_id=item.receiver_user_id,
                elder_name=elder_name,
                channel=item.channel,
                content=item.content,
                sent_at=item.sent_at or "",
                receipt_status="read" if item.is_read else "delivered",
                read_at=item.read_at,
            )
            for item, elder_name in rows
        ]


def get_accessibility_settings(user: UserProfile) -> AccessibilitySettings:
    with session_scope() as session:
        current_user = session.get(User, user.user_id)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        notes = _parse_notes(current_user.notes)
        return AccessibilitySettings(
            font_scale=notes.get("font_scale", "large"),
            high_contrast=notes.get("high_contrast", "false") == "true",
            voice_assistant=notes.get("voice_assistant", "false") == "true",
            voice_speed=notes.get("voice_speed", "normal"),
            screen_reader_enabled=notes.get("screen_reader_enabled", "false") == "true",
            voice_prompt_enabled=notes.get("voice_prompt_enabled", "false") == "true",
        )


def update_accessibility_settings(
    user: UserProfile,
    payload: AccessibilitySettingsUpdateRequest,
) -> AccessibilitySettings:
    with session_scope() as session:
        current_user = session.get(User, user.user_id)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        notes = _parse_notes(current_user.notes)
        notes["font_scale"] = payload.font_scale
        notes["high_contrast"] = "true" if payload.high_contrast else "false"
        notes["voice_assistant"] = "true" if payload.voice_assistant else "false"
        notes["voice_speed"] = payload.voice_speed
        notes["screen_reader_enabled"] = "true" if payload.screen_reader_enabled else "false"
        notes["voice_prompt_enabled"] = "true" if payload.voice_prompt_enabled else "false"
        current_user.notes = _dump_notes(notes)
        return AccessibilitySettings(
            font_scale=payload.font_scale,
            high_contrast=payload.high_contrast,
            voice_assistant=payload.voice_assistant,
            voice_speed=payload.voice_speed,
            screen_reader_enabled=payload.screen_reader_enabled,
            voice_prompt_enabled=payload.voice_prompt_enabled,
        )


def list_community_elders(keyword: str | None = None, risk_level: str | None = None) -> list[CommunityElderItem]:
    with session_scope() as session:
        elder_ids = session.scalars(
            select(ElderFamilyBinding.elder_user_id).distinct()
        ).all()
        elders = session.execute(select(User).where(User.id.in_(elder_ids)).order_by(User.created_at.asc())).scalars().all()
        results: list[CommunityElderItem] = []
        for elder in elders:
            notes = _parse_notes(elder.notes)
            alerts = session.execute(
                select(RiskAlert).where(RiskAlert.elder_user_id == elder.id).order_by(RiskAlert.occurred_at.desc())
            ).scalars().all()
            latest_alert = alerts[0] if alerts else None
            if keyword and keyword not in elder.display_name and keyword not in elder.username:
                continue
            current_risk_level = latest_alert.risk_level if latest_alert else "low"
            if risk_level and current_risk_level != risk_level:
                continue
            results.append(
                CommunityElderItem(
                    elder_user_id=elder.id,
                    elder_name=elder.display_name,
                    age=int(notes.get("age", "0")),
                    gender=notes.get("gender", ""),
                    risk_level=current_risk_level,
                    latest_alert_at=latest_alert.occurred_at if latest_alert else None,
                    latest_alert_title=latest_alert.title if latest_alert else None,
                    tags=[tag for tag in notes.get("tags", "").split("|") if tag],
                    follow_up_status=notes.get("follow_up_status", "pending"),
                    assigned_grid_member=notes.get("assigned_grid_member", ""),
                    alert_count_7d=len(alerts),
                    manual_risk_tag=notes.get("manual_risk_tag"),
                    visit_records=_load_note_json(notes, "visit_records", []),
                )
            )
        return results


def update_community_elder_followup(elder_user_id: str, payload: CommunityElderFollowupRequest) -> CommunityElderItem:
    with session_scope() as session:
        elder = session.get(User, elder_user_id)
        if not elder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="老人不存在")
        notes = _parse_notes(elder.notes)
        visit_records = _load_note_json(notes, "visit_records", [])
        visit_records.insert(
            0,
            {
                "record_type": payload.record_type,
                "note": payload.note,
                "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            },
        )
        notes["follow_up_status"] = payload.follow_up_status
        if payload.manual_risk_tag:
            notes["manual_risk_tag"] = payload.manual_risk_tag
        notes["visit_records"] = _dump_note_json(visit_records[:10])
        elder.notes = _dump_notes(notes)
    return next(item for item in list_community_elders() if item.elder_user_id == elder_user_id)


def list_workorders(status_filter: str | None = None) -> list[WorkorderItem]:
    ElderUser = aliased(User)
    AssignedUser = aliased(User)
    with session_scope() as session:
        query = (
            select(Workorder, ElderUser.display_name, AssignedUser.display_name)
            .join(ElderUser, Workorder.elder_user_id == ElderUser.id)
            .outerjoin(AssignedUser, Workorder.assigned_to_user_id == AssignedUser.id)
        )
        if status_filter:
            query = query.where(Workorder.status == status_filter)
        rows = session.execute(query.order_by(Workorder.updated_at.desc())).all()
        return [
            WorkorderItem(
                id=item.id,
                workorder_no=item.workorder_no,
                alert_id=item.alert_id,
                elder_user_id=item.elder_user_id,
                elder_name=elder_name,
                title=item.title,
                priority=item.priority,
                status=item.status,
                assigned_to_user_id=item.assigned_to_user_id,
                assigned_to_name=assigned_name,
                dispose_method=item.dispose_method,
                updated_at=_to_str(item.updated_at) or "",
            )
            for item, elder_name, assigned_name in rows
        ]


def get_workorder_detail(workorder_id: str) -> WorkorderDetail:
    with session_scope() as session:
        workorder = session.scalar(
            select(Workorder)
            .options(selectinload(Workorder.actions).selectinload(WorkorderAction.operator_user))
            .where(Workorder.id == workorder_id)
        )
        if not workorder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
        elder = session.get(User, workorder.elder_user_id)
        assigned = session.get(User, workorder.assigned_to_user_id) if workorder.assigned_to_user_id else None
        alert = session.get(RiskAlert, workorder.alert_id)
        actions = [
            WorkorderActionItem(
                id=item.id,
                action_type=item.action_type,
                operator_user_id=item.operator_user_id or "",
                operator_name=item.operator_user.display_name if item.operator_user else "",
                from_status=item.from_status,
                to_status=item.to_status,
                note=_load_action_note(item.note)[0],
                created_at=_to_str(item.created_at) or "",
                attachments=_load_action_note(item.note)[1],
                collaboration_note=_load_action_note(item.note)[2],
            )
            for item in sorted(workorder.actions, key=lambda action: action.created_at)
        ]
        return WorkorderDetail(
            id=workorder.id,
            workorder_no=workorder.workorder_no,
            alert_id=workorder.alert_id,
            elder_user_id=workorder.elder_user_id,
            elder_name=elder.display_name if elder else "",
            title=workorder.title,
            priority=workorder.priority,
            status=workorder.status,
            assigned_to_user_id=workorder.assigned_to_user_id,
            assigned_to_name=assigned.display_name if assigned else None,
            dispose_method=workorder.dispose_method,
            updated_at=_to_str(workorder.updated_at) or "",
            dispose_result=workorder.dispose_result,
            closed_at=workorder.closed_at,
            latest_alert_summary=alert.summary if alert else "",
            actions=actions,
        )


def transition_workorder(
    workorder_id: str,
    payload: WorkorderTransitionRequest,
    user: UserProfile,
) -> WorkorderDetail:
    with session_scope() as session:
        workorder = session.get(Workorder, workorder_id)
        if not workorder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
        from_status = workorder.status
        workorder.status = payload.to_status
        workorder.assigned_to_user_id = payload.assigned_to_user_id or workorder.assigned_to_user_id
        workorder.dispose_method = payload.dispose_method or workorder.dispose_method
        workorder.dispose_result = payload.dispose_result or workorder.dispose_result
        if payload.to_status == "closed":
            workorder.closed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        session.add(
            WorkorderAction(
                workorder_id=workorder.id,
                operator_user_id=user.user_id,
                action_type=payload.action_type,
                from_status=from_status,
                to_status=payload.to_status,
                note=_dump_action_note(payload.note, payload.attachments, payload.collaboration_note),
            )
        )
        session.flush()
    return get_workorder_detail(workorder_id)


def list_risk_rules() -> list[RiskRuleItem]:
    with session_scope() as session:
        rules = session.execute(select(RiskRule).order_by(RiskRule.priority.asc())).scalars().all()
        items: list[RiskRuleItem] = []
        for item in rules:
            history = _load_rule_version_history(session, item.id)
            if not history:
                history = _append_rule_version(
                    session,
                    rule_id=item.id,
                    status=item.status,
                    operator="system",
                    updated_at=_to_str(item.updated_at) or _to_str(item.created_at) or "",
                )
            items.append(
                RiskRuleItem(
                    id=item.id,
                    code=item.code,
                    name=item.name,
                    scene=item.scene,
                    risk_level=item.risk_level,
                    priority=item.priority,
                    status=item.status,
                    trigger_expression=item.trigger_expression,
                    reason_template=item.reason_template or "",
                    suggestion_template=item.suggestion_template or "",
                    version=max(int(entry["version"]) for entry in history),
                    version_history=history,
                )
            )
        return items


def list_risk_lexicon(scene: str | None = None) -> list[RiskLexiconItem]:
    with session_scope() as session:
        query = select(RiskLexiconTerm).order_by(RiskLexiconTerm.scene.asc(), RiskLexiconTerm.term.asc())
        if scene:
            query = query.where(RiskLexiconTerm.scene == scene)
        rows = session.execute(query).scalars().all()
        return [
            RiskLexiconItem(
                id=item.id,
                term=item.term,
                category=item.category,
                scene=item.scene,
                risk_level=item.risk_level,
                status=item.status,
                source=item.source,
                notes=item.notes,
            )
            for item in rows
        ]


def create_risk_lexicon(payload: RiskLexiconUpsertRequest) -> RiskLexiconItem:
    with session_scope() as session:
        item = RiskLexiconTerm(**payload.model_dump())
        session.add(item)
        session.flush()
        return RiskLexiconItem(
            id=item.id,
            term=item.term,
            category=item.category,
            scene=item.scene,
            risk_level=item.risk_level,
            status=item.status,
            source=item.source,
            notes=item.notes,
        )


def update_risk_lexicon(term_id: str, payload: RiskLexiconUpsertRequest) -> RiskLexiconItem:
    with session_scope() as session:
        item = session.get(RiskLexiconTerm, term_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="风险词不存在")
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        return RiskLexiconItem(
            id=item.id,
            term=item.term,
            category=item.category,
            scene=item.scene,
            risk_level=item.risk_level,
            status=item.status,
            source=item.source,
            notes=item.notes,
        )


def create_risk_rule(payload: RiskRuleUpsertRequest) -> RiskRuleItem:
    with session_scope() as session:
        item = RiskRule(**payload.model_dump())
        session.add(item)
        session.flush()
        history = _append_rule_version(
            session,
            rule_id=item.id,
            status=item.status,
            operator="admin",
            updated_at=_to_str(item.updated_at) or _to_str(item.created_at) or "",
        )
        return RiskRuleItem(
            id=item.id,
            code=item.code,
            name=item.name,
            scene=item.scene,
            risk_level=item.risk_level,
            priority=item.priority,
            status=item.status,
            trigger_expression=item.trigger_expression,
            reason_template=item.reason_template or "",
            suggestion_template=item.suggestion_template or "",
            version=max(int(entry["version"]) for entry in history),
            version_history=history,
        )


def update_risk_rule(rule_id: str, payload: RiskRuleUpsertRequest) -> RiskRuleItem:
    with session_scope() as session:
        item = session.get(RiskRule, rule_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="规则不存在")
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        session.flush()
        history = _append_rule_version(
            session,
            rule_id=item.id,
            status=item.status,
            operator="admin",
            updated_at=_to_str(item.updated_at) or _to_str(item.created_at) or "",
        )
        return RiskRuleItem(
            id=item.id,
            code=item.code,
            name=item.name,
            scene=item.scene,
            risk_level=item.risk_level,
            priority=item.priority,
            status=item.status,
            trigger_expression=item.trigger_expression,
            reason_template=item.reason_template or "",
            suggestion_template=item.suggestion_template or "",
            version=max(int(entry["version"]) for entry in history),
            version_history=history,
        )


def list_contents() -> list[ContentItem]:
    with session_scope() as session:
        templates = session.execute(select(PromptTemplate)).scalars().all()
        educations = session.execute(select(EducationContent)).scalars().all()
        contents = [
            ContentItem(
                id=item.id,
                content_type="template",
                code=item.code,
                title=item.name,
                category=item.category,
                audience=None,
                channel=item.channel,
                status=item.status,
                summary=item.notes,
                updated_at=_to_str(item.updated_at) or "",
                audit_status="approved",
                asset_url=None,
            )
            for item in templates
        ]
        contents.extend(
            ContentItem(
                id=item.id,
                content_type="education",
                code=None,
                title=item.title,
                category=item.category,
                audience=item.audience,
                channel="article",
                status=item.publish_status,
                summary=item.summary,
                updated_at=_to_str(item.updated_at) or "",
                audit_status="approved",
                asset_url=item.cover_image_url,
            )
            for item in educations
        )
        return sorted(contents, key=lambda item: item.updated_at, reverse=True)


def list_education_contents(
    audience: str | None = None,
    category: str | None = None,
    keyword: str | None = None,
    publish_status: str | None = "published",
) -> list[EducationContentItem]:
    with session_scope() as session:
        query = select(EducationContent)
        if audience:
            query = query.where(EducationContent.audience == audience)
        if category:
            query = query.where(EducationContent.category == category)
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(
                or_(
                    EducationContent.title.ilike(pattern),
                    EducationContent.summary.ilike(pattern),
                    EducationContent.content_body.ilike(pattern),
                )
            )
        if publish_status:
            query = query.where(EducationContent.publish_status == publish_status)
        rows = session.execute(query.order_by(EducationContent.updated_at.desc())).scalars().all()
        return [
            EducationContentItem(
                id=item.id,
                title=item.title,
                category=item.category,
                audience=item.audience,
                summary=item.summary,
                content_body=item.content_body,
                publish_status=item.publish_status,
                published_at=item.published_at,
                cover_image_url=item.cover_image_url,
            )
            for item in rows
        ]


def get_education_content_detail(content_id: str) -> EducationContentItem:
    with session_scope() as session:
        item = session.get(EducationContent, content_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识内容不存在")
        return EducationContentItem(
            id=item.id,
            title=item.title,
            category=item.category,
            audience=item.audience,
            summary=item.summary,
            content_body=item.content_body,
            publish_status=item.publish_status,
            published_at=item.published_at,
            cover_image_url=item.cover_image_url,
        )


def create_content(payload: ContentUpsertRequest) -> ContentItem:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    with session_scope() as session:
        if payload.content_type == "template":
            item = PromptTemplate(
                code=payload.code or f"TPL-{int(datetime.now(UTC).timestamp())}",
                name=payload.title,
                category=payload.category,
                channel=payload.channel or "app",
                content=payload.content_body,
                status=payload.status,
                notes=payload.summary,
            )
            session.add(item)
            session.flush()
            return ContentItem(
                id=item.id,
                content_type="template",
                code=item.code,
                title=item.name,
                category=item.category,
                audience=None,
                channel=item.channel,
                status=item.status,
                summary=item.notes,
                updated_at=now,
                audit_status=payload.audit_status,
                asset_url=payload.asset_url,
            )
        item = EducationContent(
            title=payload.title,
            category=payload.category,
            audience=payload.audience or "elder",
            summary=payload.summary,
            cover_image_url=payload.asset_url,
            content_body=payload.content_body,
            publish_status=payload.status,
            published_at=now if payload.status == "published" else None,
        )
        session.add(item)
        session.flush()
        return ContentItem(
            id=item.id,
            content_type="education",
            code=None,
            title=item.title,
            category=item.category,
            audience=item.audience,
            channel="article",
            status=item.publish_status,
            summary=item.summary,
            updated_at=now,
            audit_status=payload.audit_status,
            asset_url=item.cover_image_url,
        )


def update_content(content_id: str, payload: ContentUpsertRequest) -> ContentItem:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    with session_scope() as session:
        if payload.content_type == "template":
            item = session.get(PromptTemplate, content_id)
            if not item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")
            item.code = payload.code or item.code
            item.name = payload.title
            item.category = payload.category
            item.channel = payload.channel or item.channel
            item.content = payload.content_body
            item.status = payload.status
            item.notes = payload.summary
            return ContentItem(
                id=item.id,
                content_type="template",
                code=item.code,
                title=item.name,
                category=item.category,
                audience=None,
                channel=item.channel,
                status=item.status,
                summary=item.notes,
                updated_at=now,
                audit_status=payload.audit_status,
                asset_url=payload.asset_url,
            )
        item = session.get(EducationContent, content_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")
        item.title = payload.title
        item.category = payload.category
        item.audience = payload.audience or item.audience
        item.summary = payload.summary
        item.cover_image_url = payload.asset_url
        item.content_body = payload.content_body
        item.publish_status = payload.status
        item.published_at = now if payload.status == "published" else item.published_at
        return ContentItem(
            id=item.id,
            content_type="education",
            code=None,
            title=item.title,
            category=item.category,
            audience=item.audience,
            channel="article",
            status=item.publish_status,
            summary=item.summary,
            updated_at=now,
            audit_status=payload.audit_status,
            asset_url=item.cover_image_url,
        )


def list_system_configs() -> list[SystemConfigItem]:
    with session_scope() as session:
        rows = session.execute(
            select(SystemConfig)
            .where(SystemConfig.group != "risk-rule")
            .order_by(SystemConfig.group.asc(), SystemConfig.key.asc())
        ).scalars().all()
        items: list[SystemConfigItem] = []
        for item in rows:
            latest_audit = session.execute(
                select(AuditLog)
                .where(AuditLog.path.like(f"%/admin/system-config/{item.key}%"))
                .order_by(AuditLog.created_at.desc())
            ).scalars().first()
            audit_count = session.scalar(
                select(func.count(AuditLog.id)).where(AuditLog.path.like(f"%/admin/system-config/{item.key}%"))
            ) or 0
            items.append(
                SystemConfigItem(
                    key=item.key,
                    name=item.name,
                    value=item.value,
                    effective_value=item.value,
                    group=item.group,
                    description=item.description or "",
                    last_updated_at=_to_str(item.updated_at),
                    last_updated_by=(latest_audit.user_id if latest_audit else None),
                    audit_count=audit_count,
                )
            )
        return items


def list_admin_risk_alerts() -> list[AdminRiskAlertItem]:
    with session_scope() as session:
        rows = session.execute(
            select(RiskAlert, User.display_name)
            .join(User, RiskAlert.elder_user_id == User.id)
            .order_by(RiskAlert.occurred_at.desc())
        ).all()
        results: list[AdminRiskAlertItem] = []
        for item, elder_name in rows:
            results.append(
                AdminRiskAlertItem(
                    id=item.id,
                    elder_user_id=item.elder_user_id,
                    elder_name=elder_name,
                    title=item.title,
                    risk_level=item.risk_level,
                    source_type=item.source_type,
                    status=item.status,
                    occurred_at=item.occurred_at,
                    related_notifications=session.scalar(
                        select(func.count(NotificationRecord.id)).where(NotificationRecord.alert_id == item.id)
                    )
                    or 0,
                    related_workorders=session.scalar(
                        select(func.count(Workorder.id)).where(Workorder.alert_id == item.id)
                    )
                    or 0,
                )
            )
        return results


def get_admin_risk_alert_detail(alert_id: str) -> AdminRiskAlertDetail:
    detail = get_risk_alert_detail(alert_id)
    summary = next((item for item in list_admin_risk_alerts() if item.id == alert_id), None)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="告警不存在")
    return AdminRiskAlertDetail(
        **summary.model_dump(),
        reason_detail=detail.reason_detail,
        suggestion_action=detail.suggestion_action,
        related_notification_ids=detail.related_notification_ids,
        related_workorder_ids=detail.related_workorder_ids,
    )


def update_system_config(config_key: str, payload: SystemConfigUpdateRequest, user: UserProfile | None = None) -> SystemConfigItem:
    with session_scope() as session:
        item = session.scalar(select(SystemConfig).where(SystemConfig.key == config_key))
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
        item.value = payload.value
        session.flush()
        if user:
            session.add(
                AuditLog(
                    user_id=user.user_id,
                    action="system_config_update",
                    module="admin",
                    target_type="system_config",
                    target_id=config_key,
                    status="success",
                    method="PUT",
                    path=f"/api/v1/admin/system-config/{config_key}",
                    duration_ms="0",
                    details=f"effective_value={payload.value}",
                )
            )
        return SystemConfigItem(
            key=item.key,
            name=item.name,
            value=item.value,
            effective_value=item.value,
            group=item.group,
            description=item.description or "",
            last_updated_at=_to_str(item.updated_at),
            last_updated_by=(user.user_id if user else None),
            audit_count=1,
        )


def get_community_report() -> CommunityReportData:
    with session_scope() as session:
        alerts = session.execute(select(RiskAlert)).scalars().all()
        workorders = session.execute(select(Workorder)).scalars().all()
        educations = session.execute(select(EducationContent)).scalars().all()
        risk_by_level = [
            {"label": level, "count": len([item for item in alerts if item.risk_level == level])}
            for level in ["high", "medium", "low"]
        ]
        workorder_status = [
            {"label": status_name, "count": len([item for item in workorders if item.status == status_name])}
            for status_name in ["pending", "processing", "closed"]
        ]
        education_summary = [
            {"label": status_name, "count": len([item for item in educations if item.publish_status == status_name])}
            for status_name in ["published", "draft"]
        ]
        closed_workorders = [item for item in workorders if item.closed_at]
        avg_minutes = 0
        if closed_workorders:
            total_minutes = 0
            for item in closed_workorders:
                created = item.created_at
                closed = datetime.fromisoformat(item.closed_at.replace("Z", "+00:00"))
                total_minutes += int((closed - created).total_seconds() / 60)
            avg_minutes = int(total_minutes / len(closed_workorders))
        return CommunityReportData(
            risk_by_level=risk_by_level,
            workorder_status=workorder_status,
            education_summary=education_summary,
            disposal_avg_minutes=avg_minutes,
        )
