from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.constants.roles import UserRole
from app.schemas.business import (
    AdminUserItem,
    BindingCreateRequest,
    BindingItem,
    BindingUpdateRequest,
    CommunityElderItem,
    ContentItem,
    NotificationItem,
    PaginationMeta,
    PagedResult,
    RiskAlertDetail,
    RiskAlertItem,
    RiskRuleItem,
    RoleInfo,
    SystemConfigItem,
    WorkorderActionItem,
    WorkorderDetail,
    WorkorderItem,
    WorkorderTransitionRequest,
)
from app.schemas.user import UserProfile
from app.services.auth import DEMO_USERS

ROLE_DETAILS = {
    UserRole.ELDER: {
        "name": "老年用户",
        "description": "接收风险提醒、求助和亲属绑定。",
        "permissions": ["elder:read", "sos:create", "binding:manage"],
    },
    UserRole.FAMILY: {
        "name": "子女用户",
        "description": "查看老人风险、接收通知和监护设置。",
        "permissions": ["family:read", "alerts:read", "notifications:read", "bindings:read"],
    },
    UserRole.COMMUNITY: {
        "name": "社区工作人员",
        "description": "查看重点老人、处理工单和回访协同。",
        "permissions": ["community:read", "workorder:read", "workorder:update", "elder-focus:read"],
    },
    UserRole.ADMIN: {
        "name": "系统管理员",
        "description": "管理用户、角色、规则、内容和系统配置。",
        "permissions": ["*"],
    },
}

USERS = {
    "u-elder-001": {
        "user_id": "u-elder-001",
        "username": "elder_demo",
        "display_name": "李阿姨",
        "phone": "138****1001",
        "status": "active",
        "roles": [UserRole.ELDER],
        "permissions": ["elder:read", "sos:create", "binding:manage"],
        "last_login_at": "2026-04-14T08:30:00Z",
        "age": 72,
        "gender": "女",
    },
    "u-elder-002": {
        "user_id": "u-elder-002",
        "username": "elder_demo_2",
        "display_name": "周叔叔",
        "phone": "138****1002",
        "status": "active",
        "roles": [UserRole.ELDER],
        "permissions": ["elder:read", "sos:create", "binding:manage"],
        "last_login_at": "2026-04-13T17:20:00Z",
        "age": 68,
        "gender": "男",
    },
    "u-family-001": {
        "user_id": "u-family-001",
        "username": "family_demo",
        "display_name": "王女士",
        "phone": "139****2001",
        "status": "active",
        "roles": [UserRole.FAMILY],
        "permissions": ["family:read", "alerts:read", "notifications:read", "bindings:read"],
        "last_login_at": "2026-04-14T09:00:00Z",
    },
    "u-family-002": {
        "user_id": "u-family-002",
        "username": "family_demo_2",
        "display_name": "李先生",
        "phone": "139****2002",
        "status": "active",
        "roles": [UserRole.FAMILY],
        "permissions": ["family:read", "alerts:read", "notifications:read", "bindings:read"],
        "last_login_at": "2026-04-13T19:45:00Z",
    },
    "u-community-001": {
        "user_id": "u-community-001",
        "username": "community_demo",
        "display_name": "社区网格员张强",
        "phone": "137****3001",
        "status": "active",
        "roles": [UserRole.COMMUNITY],
        "permissions": ["community:read", "workorder:read", "workorder:update", "elder-focus:read"],
        "last_login_at": "2026-04-14T07:50:00Z",
    },
    "u-community-002": {
        "user_id": "u-community-002",
        "username": "community_demo_2",
        "display_name": "社区社工陈敏",
        "phone": "137****3002",
        "status": "active",
        "roles": [UserRole.COMMUNITY],
        "permissions": ["community:read", "workorder:read", "workorder:update", "elder-focus:read"],
        "last_login_at": "2026-04-13T18:10:00Z",
    },
    "u-admin-001": {
        "user_id": "u-admin-001",
        "username": "admin_demo",
        "display_name": "系统管理员",
        "phone": "136****4001",
        "status": "active",
        "roles": [UserRole.ADMIN],
        "permissions": ["*"],
        "last_login_at": "2026-04-14T08:10:00Z",
    },
}

BINDINGS = [
    {
        "id": "bind-001",
        "elder_user_id": "u-elder-001",
        "family_user_id": "u-family-001",
        "relationship_type": "daughter",
        "status": "active",
        "is_emergency_contact": True,
        "authorized_at": "2026-04-10T10:00:00Z",
    },
    {
        "id": "bind-002",
        "elder_user_id": "u-elder-002",
        "family_user_id": "u-family-002",
        "relationship_type": "son",
        "status": "active",
        "is_emergency_contact": True,
        "authorized_at": "2026-04-09T15:20:00Z",
    },
]

RISK_ALERTS = [
    {
        "id": "alert-001",
        "elder_user_id": "u-elder-001",
        "source_type": "sms",
        "risk_level": "high",
        "risk_score": 92,
        "title": "疑似冒充客服退款短信",
        "summary": "短信包含退款链接与验证码索取内容，存在诱导转账风险。",
        "reason_detail": "命中“退款链接”“验证码”“客服补偿”多条高危规则，且短信中包含短链。",
        "suggestion_action": "不要点击链接，不要透露验证码，建议联系子女核实并保留短信截图。",
        "status": "pending_follow_up",
        "occurred_at": "2026-04-14T08:22:00Z",
        "hit_rule_codes": ["SMS_REFUND_LINK", "SMS_VERIFY_CODE"],
        "related_notification_ids": ["notify-001", "notify-002"],
        "related_workorder_ids": ["wo-001"],
    },
    {
        "id": "alert-002",
        "elder_user_id": "u-elder-002",
        "source_type": "call",
        "risk_level": "medium",
        "risk_score": 71,
        "title": "疑似冒充公检法来电",
        "summary": "通话中出现“安全账户”“配合调查”等敏感话术。",
        "reason_detail": "命中公检法冒充与转账诱导话术，语义强度中等。",
        "suggestion_action": "先挂断电话，通过官方渠道回拨核实，不要转账。",
        "status": "new",
        "occurred_at": "2026-04-13T19:10:00Z",
        "hit_rule_codes": ["CALL_POLICE_IMPERSONATION"],
        "related_notification_ids": ["notify-003"],
        "related_workorder_ids": [],
    },
]

NOTIFICATIONS = [
    {
        "id": "notify-001",
        "receiver_user_id": "u-family-001",
        "alert_id": "alert-001",
        "channel": "app",
        "notification_type": "risk_alert",
        "title": "老人收到高风险诈骗短信",
        "content": "李阿姨于 08:22 收到疑似退款诈骗短信，请尽快联系提醒。",
        "status": "sent",
        "is_read": False,
        "sent_at": "2026-04-14T08:23:00Z",
    },
    {
        "id": "notify-002",
        "receiver_user_id": "u-community-001",
        "alert_id": "alert-001",
        "channel": "workbench",
        "notification_type": "community_dispatch",
        "title": "辖区出现高风险老人告警",
        "content": "李阿姨命中高风险诈骗规则，建议安排电话回访。",
        "status": "sent",
        "is_read": True,
        "sent_at": "2026-04-14T08:25:00Z",
    },
    {
        "id": "notify-003",
        "receiver_user_id": "u-family-002",
        "alert_id": "alert-002",
        "channel": "sms",
        "notification_type": "risk_alert",
        "title": "老人疑似接到冒充公检法电话",
        "content": "周叔叔昨日晚间接到疑似诈骗电话，建议尽快回访。",
        "status": "sent",
        "is_read": False,
        "sent_at": "2026-04-13T19:15:00Z",
    },
]

COMMUNITY_ELDERS = [
    {
        "elder_user_id": "u-elder-001",
        "tags": ["高风险", "需回访", "独居"],
        "follow_up_status": "pending_visit",
        "assigned_grid_member": "社区网格员张强",
        "alert_count_7d": 3,
    },
    {
        "elder_user_id": "u-elder-002",
        "tags": ["电话回访中"],
        "follow_up_status": "phone_following",
        "assigned_grid_member": "社区社工陈敏",
        "alert_count_7d": 1,
    },
]

WORKORDERS = [
    {
        "id": "wo-001",
        "workorder_no": "GD202604140001",
        "alert_id": "alert-001",
        "elder_user_id": "u-elder-001",
        "title": "李阿姨高风险短信回访工单",
        "priority": "high",
        "status": "processing",
        "assigned_to_user_id": "u-community-001",
        "dispose_method": "phone_visit",
        "dispose_result": None,
        "closed_at": None,
        "updated_at": "2026-04-14T09:05:00Z",
    }
]

WORKORDER_ACTIONS = [
    {
        "id": "woa-001",
        "workorder_id": "wo-001",
        "action_type": "create",
        "operator_user_id": "u-admin-001",
        "from_status": None,
        "to_status": "pending",
        "note": "高风险短信自动转工单。",
        "created_at": "2026-04-14T08:25:00Z",
    },
    {
        "id": "woa-002",
        "workorder_id": "wo-001",
        "action_type": "assign",
        "operator_user_id": "u-admin-001",
        "from_status": "pending",
        "to_status": "processing",
        "note": "已指派社区网格员张强电话回访。",
        "created_at": "2026-04-14T08:30:00Z",
    },
]

RISK_RULES = [
    {
        "id": "rule-001",
        "code": "SMS_REFUND_LINK",
        "name": "短信退款链接识别",
        "scene": "sms",
        "risk_level": "high",
        "priority": 10,
        "status": "enabled",
        "trigger_expression": "contains(refund) && contains(short_link)",
        "reason_template": "短信涉及退款链接与身份核验，疑似引导跳转诈骗页面。",
        "suggestion_template": "不要点击链接，建议联系官方客服核实。",
    },
    {
        "id": "rule-002",
        "code": "CALL_POLICE_IMPERSONATION",
        "name": "冒充公检法来电",
        "scene": "call",
        "risk_level": "medium",
        "priority": 20,
        "status": "enabled",
        "trigger_expression": "contains(security_account) && contains(investigation)",
        "reason_template": "来电出现安全账户与配合调查话术。",
        "suggestion_template": "挂断后主动拨打官方电话核实。",
    },
]

CONTENTS = [
    {
        "id": "content-001",
        "content_type": "template",
        "code": "ALERT_HIGH_RISK_FAMILY",
        "title": "高风险通知模板",
        "category": "notification_template",
        "audience": "family",
        "channel": "app",
        "status": "enabled",
        "summary": "用于子女端高风险告警提醒。",
        "updated_at": "2026-04-14T08:00:00Z",
    },
    {
        "id": "content-002",
        "content_type": "education",
        "code": None,
        "title": "警惕冒充客服退款骗局",
        "category": "anti_fraud_article",
        "audience": "elder",
        "channel": "article",
        "status": "published",
        "summary": "讲解常见退款诈骗套路与识别要点。",
        "updated_at": "2026-04-13T16:00:00Z",
    },
]

SYSTEM_CONFIGS = [
    {
        "key": "risk.high_threshold",
        "name": "高风险分数阈值",
        "value": "85",
        "group": "risk",
        "description": "达到该分值时自动通知子女并生成社区工单。",
    },
    {
        "key": "notification.family_channels",
        "name": "子女通知渠道",
        "value": "app,sms",
        "group": "notification",
        "description": "高风险事件默认通知渠道。",
    },
    {
        "key": "workorder.auto_dispatch",
        "name": "自动派单开关",
        "value": "true",
        "group": "workorder",
        "description": "高风险告警是否自动生成社区工单。",
    },
]


def _paginate(items: list[dict], page: int, page_size: int) -> PagedResult:
    start = (page - 1) * page_size
    end = start + page_size
    return PagedResult(
        items=items[start:end],
        pagination=PaginationMeta(page=page, page_size=page_size, total=len(items)),
    )


def _get_user_name(user_id: str) -> str:
    return USERS[user_id]["display_name"]


def _get_alert(alert_id: str) -> dict:
    for alert in RISK_ALERTS:
        if alert["id"] == alert_id:
            return alert
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="风险告警不存在")


def _get_workorder(workorder_id: str) -> dict:
    for workorder in WORKORDERS:
        if workorder["id"] == workorder_id:
            return workorder
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")


def _resolve_binding_item(binding: dict) -> BindingItem:
    return BindingItem(
        **binding,
        elder_name=_get_user_name(binding["elder_user_id"]),
        family_name=_get_user_name(binding["family_user_id"]),
    )


def list_roles() -> list[RoleInfo]:
    role_counts = {role: 0 for role in ROLE_DETAILS}
    for user in USERS.values():
        for role in user["roles"]:
            role_counts[role] += 1

    return [
        RoleInfo(
            code=role,
            name=detail["name"],
            description=detail["description"],
            permissions=detail["permissions"],
            user_count=role_counts[role],
        )
        for role, detail in ROLE_DETAILS.items()
    ]


def list_admin_users(keyword: str | None = None, role: UserRole | None = None) -> list[AdminUserItem]:
    result: list[AdminUserItem] = []
    for user in USERS.values():
        if keyword and keyword not in user["display_name"] and keyword not in user["username"]:
            continue
        if role and role not in user["roles"]:
            continue
        result.append(AdminUserItem(**{k: user[k] for k in AdminUserItem.model_fields}))
    return result


def list_bindings(current_user: UserProfile) -> list[BindingItem]:
    if UserRole.ADMIN in current_user.roles:
        selected = BINDINGS
    elif UserRole.ELDER in current_user.roles:
        selected = [item for item in BINDINGS if item["elder_user_id"] == current_user.user_id]
    elif UserRole.FAMILY in current_user.roles:
        selected = [item for item in BINDINGS if item["family_user_id"] == current_user.user_id]
    else:
        selected = []
    return [_resolve_binding_item(item) for item in selected]


def create_binding(payload: BindingCreateRequest) -> BindingItem:
    for item in BINDINGS:
        if item["elder_user_id"] == payload.elder_user_id and item["family_user_id"] == payload.family_user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="绑定关系已存在")

    binding = {
        "id": f"bind-{len(BINDINGS) + 1:03d}",
        "elder_user_id": payload.elder_user_id,
        "family_user_id": payload.family_user_id,
        "relationship_type": payload.relationship_type,
        "status": "active",
        "is_emergency_contact": payload.is_emergency_contact,
        "authorized_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    BINDINGS.append(binding)
    return _resolve_binding_item(binding)


def update_binding(binding_id: str, payload: BindingUpdateRequest) -> BindingItem:
    for item in BINDINGS:
        if item["id"] != binding_id:
            continue
        if payload.relationship_type is not None:
            item["relationship_type"] = payload.relationship_type
        if payload.status is not None:
            item["status"] = payload.status
        if payload.is_emergency_contact is not None:
            item["is_emergency_contact"] = payload.is_emergency_contact
        return _resolve_binding_item(item)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定关系不存在")


def delete_binding(binding_id: str) -> None:
    for index, item in enumerate(BINDINGS):
        if item["id"] == binding_id:
            BINDINGS.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定关系不存在")


def list_risk_alerts(current_user: UserProfile, risk_level: str | None = None) -> list[RiskAlertItem]:
    def visible(alert: dict) -> bool:
        if risk_level and alert["risk_level"] != risk_level:
            return False
        if UserRole.ADMIN in current_user.roles or UserRole.COMMUNITY in current_user.roles:
            return True
        if UserRole.ELDER in current_user.roles:
            return alert["elder_user_id"] == current_user.user_id
        if UserRole.FAMILY in current_user.roles:
            elder_ids = {
                item["elder_user_id"] for item in BINDINGS if item["family_user_id"] == current_user.user_id
            }
            return alert["elder_user_id"] in elder_ids
        return False

    return [
        RiskAlertItem(
            **{k: alert[k] for k in RiskAlertItem.model_fields if k not in {"elder_name"}},
            elder_name=_get_user_name(alert["elder_user_id"]),
        )
        for alert in RISK_ALERTS
        if visible(alert)
    ]


def get_risk_alert_detail(alert_id: str) -> RiskAlertDetail:
    alert = _get_alert(alert_id)
    return RiskAlertDetail(
        **{k: alert[k] for k in RiskAlertDetail.model_fields if k not in {"elder_name"}},
        elder_name=_get_user_name(alert["elder_user_id"]),
    )


def list_notifications(current_user: UserProfile, is_read: bool | None = None) -> list[NotificationItem]:
    items: list[NotificationItem] = []
    for notification in NOTIFICATIONS:
        if UserRole.ADMIN not in current_user.roles and notification["receiver_user_id"] != current_user.user_id:
            continue
        if is_read is not None and notification["is_read"] is not is_read:
            continue
        alert = _get_alert(notification["alert_id"])
        items.append(
            NotificationItem(
                **notification,
                receiver_name=_get_user_name(notification["receiver_user_id"]),
                alert_title=alert["title"],
            )
        )
    return items


def list_community_elders(keyword: str | None = None, risk_level: str | None = None) -> list[CommunityElderItem]:
    result: list[CommunityElderItem] = []
    for item in COMMUNITY_ELDERS:
        user = USERS[item["elder_user_id"]]
        latest_alert = next((alert for alert in RISK_ALERTS if alert["elder_user_id"] == user["user_id"]), None)
        level = latest_alert["risk_level"] if latest_alert else "low"
        if keyword and keyword not in user["display_name"]:
            continue
        if risk_level and risk_level != level:
            continue
        result.append(
            CommunityElderItem(
                elder_user_id=user["user_id"],
                elder_name=user["display_name"],
                age=user["age"],
                gender=user["gender"],
                risk_level=level,
                latest_alert_at=latest_alert["occurred_at"] if latest_alert else None,
                latest_alert_title=latest_alert["title"] if latest_alert else None,
                tags=item["tags"],
                follow_up_status=item["follow_up_status"],
                assigned_grid_member=item["assigned_grid_member"],
                alert_count_7d=item["alert_count_7d"],
            )
        )
    return result


def list_workorders(status_filter: str | None = None) -> list[WorkorderItem]:
    result: list[WorkorderItem] = []
    for item in WORKORDERS:
        if status_filter and item["status"] != status_filter:
            continue
        result.append(
            WorkorderItem(
                **{k: item[k] for k in WorkorderItem.model_fields if k not in {"elder_name", "assigned_to_name"}},
                elder_name=_get_user_name(item["elder_user_id"]),
                assigned_to_name=_get_user_name(item["assigned_to_user_id"]) if item["assigned_to_user_id"] else None,
            )
        )
    return result


def get_workorder_detail(workorder_id: str) -> WorkorderDetail:
    workorder = _get_workorder(workorder_id)
    alert = _get_alert(workorder["alert_id"])
    actions = [
        WorkorderActionItem(
            **action,
            operator_name=_get_user_name(action["operator_user_id"]),
        )
        for action in WORKORDER_ACTIONS
        if action["workorder_id"] == workorder_id
    ]
    return WorkorderDetail(
        **{k: workorder[k] for k in WorkorderDetail.model_fields if k not in {"elder_name", "assigned_to_name", "latest_alert_summary", "actions"}},
        elder_name=_get_user_name(workorder["elder_user_id"]),
        assigned_to_name=_get_user_name(workorder["assigned_to_user_id"]) if workorder["assigned_to_user_id"] else None,
        latest_alert_summary=alert["summary"],
        actions=actions,
    )


def transition_workorder(
    workorder_id: str,
    payload: WorkorderTransitionRequest,
    operator: UserProfile,
) -> WorkorderDetail:
    workorder = _get_workorder(workorder_id)
    from_status = workorder["status"]
    workorder["status"] = payload.to_status
    workorder["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if payload.assigned_to_user_id is not None:
        workorder["assigned_to_user_id"] = payload.assigned_to_user_id
    if payload.dispose_method is not None:
        workorder["dispose_method"] = payload.dispose_method
    if payload.dispose_result is not None:
        workorder["dispose_result"] = payload.dispose_result
    if payload.to_status == "closed":
        workorder["closed_at"] = workorder["updated_at"]

    WORKORDER_ACTIONS.append(
        {
            "id": f"woa-{len(WORKORDER_ACTIONS) + 1:03d}",
            "workorder_id": workorder_id,
            "action_type": payload.action_type,
            "operator_user_id": operator.user_id,
            "from_status": from_status,
            "to_status": payload.to_status,
            "note": payload.note,
            "created_at": workorder["updated_at"],
        }
    )
    return get_workorder_detail(workorder_id)


def list_risk_rules() -> list[RiskRuleItem]:
    return [RiskRuleItem(**deepcopy(item)) for item in RISK_RULES]


def list_contents() -> list[ContentItem]:
    return [ContentItem(**deepcopy(item)) for item in CONTENTS]


def list_system_configs() -> list[SystemConfigItem]:
    return [SystemConfigItem(**deepcopy(item)) for item in SYSTEM_CONFIGS]


def get_paged_payload(items: list, page: int, page_size: int) -> dict:
    raw_items = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]
    return _paginate(raw_items, page, page_size).model_dump()


def sync_demo_users_from_auth_service() -> None:
    for user in DEMO_USERS:
        if user.user_id in USERS:
            continue
        USERS[user.user_id] = {
            "user_id": user.user_id,
            "username": user.username,
            "display_name": user.display_name,
            "phone": user.phone,
            "status": "active",
            "roles": list(user.roles),
            "permissions": list(user.permissions),
            "last_login_at": None,
        }


sync_demo_users_from_auth_service()
