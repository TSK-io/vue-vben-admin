from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy import select

from app.constants.roles import UserRole
from app.db.base import Base
from app.db.session import get_engine, session_scope
from app.models import (
    EducationContent,
    ElderFamilyBinding,
    NotificationRecord,
    PromptTemplate,
    RiskAlert,
    RiskLexiconTerm,
    RiskRule,
    Role,
    SmsRecognitionRecord,
    SystemConfig,
    User,
    UserRoleLink,
    Workorder,
    WorkorderAction,
)

ROLE_DETAILS: dict[UserRole, dict[str, str | list[str]]] = {
    UserRole.ELDER: {
        "name": "老年用户",
        "description": "接收风险提醒、求助和亲属绑定。",
        "permissions": ["elder:read", "sos:create", "binding:manage"],
    },
    UserRole.INPUT: {
        "name": "输入端操作员",
        "description": "模拟外部电话号码发起电话和短信剧情。",
        "permissions": ["input:operate", "phone-directory:read", "risk-recognition:create"],
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

SEED_USERS = [
    {
        "id": "u-elder-001",
        "username": "elder_demo",
        "password_hash": "111",
        "display_name": "李阿姨",
        "phone": "13800001001",
        "status": "active",
        "last_login_at": "2026-04-14T08:30:00Z",
        "notes": "age=72;gender=女;tags=高风险|需回访|独居;follow_up_status=pending_visit;assigned_grid_member=社区网格员张强",
        "roles": [UserRole.ELDER],
    },
    {
        "id": "u-elder-002",
        "username": "elder_demo_2",
        "password_hash": "111",
        "display_name": "周叔叔",
        "phone": "13800001002",
        "status": "active",
        "last_login_at": "2026-04-13T17:20:00Z",
        "notes": "age=68;gender=男;tags=电话回访中;follow_up_status=phone_following;assigned_grid_member=社区社工陈敏",
        "roles": [UserRole.ELDER],
    },
    {
        "id": "u-family-001",
        "username": "family_demo",
        "password_hash": "111",
        "display_name": "王女士",
        "phone": "13900002001",
        "status": "active",
        "last_login_at": "2026-04-14T09:00:00Z",
        "roles": [UserRole.FAMILY],
    },
    {
        "id": "u-family-002",
        "username": "family_demo_2",
        "password_hash": "111",
        "display_name": "李先生",
        "phone": "13900002002",
        "status": "active",
        "last_login_at": "2026-04-13T19:45:00Z",
        "roles": [UserRole.FAMILY],
    },
    {
        "id": "u-input-001",
        "username": "input_demo",
        "password_hash": "111",
        "display_name": "剧情输入端",
        "phone": "17000005001",
        "status": "active",
        "last_login_at": "2026-04-14T08:40:00Z",
        "notes": "scenario_phone=17099990001|01012345678",
        "roles": [UserRole.INPUT],
    },
    {
        "id": "u-community-001",
        "username": "community_demo",
        "password_hash": "111",
        "display_name": "社区网格员张强",
        "phone": "13700003001",
        "status": "active",
        "last_login_at": "2026-04-14T07:50:00Z",
        "roles": [UserRole.COMMUNITY],
    },
    {
        "id": "u-community-002",
        "username": "community_demo_2",
        "password_hash": "111",
        "display_name": "社区社工陈敏",
        "phone": "13700003002",
        "status": "active",
        "last_login_at": "2026-04-13T18:10:00Z",
        "roles": [UserRole.COMMUNITY],
    },
    {
        "id": "u-admin-001",
        "username": "admin_demo",
        "password_hash": "111",
        "display_name": "系统管理员",
        "phone": "13600004001",
        "status": "active",
        "last_login_at": "2026-04-14T08:10:00Z",
        "roles": [UserRole.ADMIN],
    },
]


def ensure_chat_schema_compatibility() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "chat_conversations" not in table_names:
        return

    expected_columns: dict[str, list[tuple[str, str]]] = {
        "chat_conversations": [
            ("pair_key", "VARCHAR(120)"),
            ("title", "VARCHAR(100)"),
            ("last_message_preview", "VARCHAR(255)"),
            ("last_message_at", "VARCHAR(40)"),
        ],
        "chat_conversation_members": [
            ("role_code", "VARCHAR(20)"),
            ("joined_at", "VARCHAR(40)"),
            ("last_read_at", "VARCHAR(40)"),
            ("is_muted", "BOOLEAN DEFAULT false NOT NULL"),
        ],
        "chat_messages": [
            ("receiver_user_id", "VARCHAR(36)"),
            ("content", "TEXT"),
            ("content_text", "TEXT"),
            ("content_json", "TEXT"),
            ("read_at", "VARCHAR(40)"),
            ("client_message_id", "VARCHAR(64)"),
            ("read_by_all_at", "VARCHAR(40)"),
            ("risk_level", "VARCHAR(20) DEFAULT 'low' NOT NULL"),
            ("risk_category", "VARCHAR(50)"),
            ("risk_reason", "TEXT"),
            ("risk_suggestion", "TEXT"),
        ],
    }
    expected_tables: dict[str, str] = {
        "chat_user_relations": """
            CREATE TABLE chat_user_relations (
                owner_user_id VARCHAR(36) NOT NULL,
                target_user_id VARCHAR(36) NOT NULL,
                is_blocked BOOLEAN DEFAULT false NOT NULL,
                is_reported BOOLEAN DEFAULT false NOT NULL,
                report_reason TEXT,
                blocked_at VARCHAR(40),
                reported_at VARCHAR(40),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                FOREIGN KEY(owner_user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(target_user_id) REFERENCES users (id) ON DELETE CASCADE,
                CONSTRAINT uq_chat_user_relations_owner_target UNIQUE (owner_user_id, target_user_id)
            )
        """,
        "chat_audit_logs": """
            CREATE TABLE chat_audit_logs (
                actor_user_id VARCHAR(36),
                target_user_id VARCHAR(36),
                conversation_id VARCHAR(36),
                message_id VARCHAR(36),
                action VARCHAR(40) NOT NULL,
                detail_json TEXT,
                risk_level VARCHAR(20),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE SET NULL,
                FOREIGN KEY(target_user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        """,
        "call_sessions": """
            CREATE TABLE call_sessions (
                conversation_id VARCHAR(36) NOT NULL,
                initiator_user_id VARCHAR(36) NOT NULL,
                receiver_user_id VARCHAR(36) NOT NULL,
                call_type VARCHAR(20) DEFAULT 'audio' NOT NULL,
                status VARCHAR(20) DEFAULT 'initiated' NOT NULL,
                started_at VARCHAR(40),
                answered_at VARCHAR(40),
                ended_at VARCHAR(40),
                ended_reason VARCHAR(40),
                duration_seconds INTEGER DEFAULT 0 NOT NULL,
                offer_sdp TEXT,
                answer_sdp TEXT,
                last_ice_candidate TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                FOREIGN KEY(conversation_id) REFERENCES chat_conversations (id) ON DELETE CASCADE,
                FOREIGN KEY(initiator_user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(receiver_user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """,
        "call_participants": """
            CREATE TABLE call_participants (
                call_session_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                role VARCHAR(20) DEFAULT 'participant' NOT NULL,
                join_state VARCHAR(20) DEFAULT 'invited' NOT NULL,
                joined_at VARCHAR(40),
                left_at VARCHAR(40),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                FOREIGN KEY(call_session_id) REFERENCES call_sessions (id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                CONSTRAINT uq_call_participants_call_user UNIQUE (call_session_id, user_id)
            )
        """,
        "call_events": """
            CREATE TABLE call_events (
                call_session_id VARCHAR(36) NOT NULL,
                actor_user_id VARCHAR(36),
                event_type VARCHAR(40) NOT NULL,
                payload_json TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                FOREIGN KEY(call_session_id) REFERENCES call_sessions (id) ON DELETE CASCADE,
                FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        """,
    }

    with engine.begin() as connection:
        current_tables = set(inspect(connection).get_table_names())
        for table_name, ddl in expected_tables.items():
            if table_name not in current_tables:
                connection.execute(text(ddl))

        for table_name, columns in expected_columns.items():
            existing = {column["name"] for column in inspect(connection).get_columns(table_name)}
            for column_name, column_type in columns:
                if column_name not in existing:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))

        message_columns = {column["name"] for column in inspect(connection).get_columns("chat_messages")}
        if "content" in message_columns and "content_text" in message_columns:
            connection.execute(text("UPDATE chat_messages SET content_text = content WHERE content_text IS NULL"))
        if "read_at" in message_columns and "read_by_all_at" in message_columns:
            connection.execute(
                text("UPDATE chat_messages SET read_by_all_at = read_at WHERE read_by_all_at IS NULL AND read_at IS NOT NULL")
            )


def ensure_database_ready() -> None:
    Base.metadata.create_all(bind=get_engine())
    ensure_chat_schema_compatibility()
    with session_scope() as session:
        existing_user = session.scalar(select(User.id).limit(1))

        role_rows: dict[UserRole, Role] = {}
        for role_code, detail in ROLE_DETAILS.items():
            role = session.scalar(select(Role).where(Role.code == role_code.value))
            if role:
                role.name = str(detail["name"])
                role.description = str(detail["description"])
                role.is_system = True
            else:
                role = Role(
                    id=f"role-{role_code.value}",
                    code=role_code.value,
                    name=str(detail["name"]),
                    description=str(detail["description"]),
                    is_system=True,
                )
                session.add(role)
            role_rows[role_code] = role

        for item in SEED_USERS:
            existing = session.get(User, item["id"])
            if existing:
                continue
            payload = {key: value for key, value in item.items() if key != "roles"}
            roles = list(item["roles"])
            user = User(**payload)
            session.add(user)
            session.flush()
            for role in roles:
                session.add(
                    UserRoleLink(
                        id=f"url-{user.id}-{role.value}",
                        user_id=user.id,
                        role_id=role_rows[role].id,
                    )
                )

        if existing_user:
            return

        session.add_all(
            [
                ElderFamilyBinding(
                    id="bind-001",
                    elder_user_id="u-elder-001",
                    family_user_id="u-family-001",
                    relationship_type="daughter",
                    status="active",
                    is_emergency_contact=True,
                    authorized_at="2026-04-10T10:00:00Z",
                ),
                ElderFamilyBinding(
                    id="bind-002",
                    elder_user_id="u-elder-002",
                    family_user_id="u-family-002",
                    relationship_type="son",
                    status="active",
                    is_emergency_contact=True,
                    authorized_at="2026-04-09T15:20:00Z",
                ),
                SmsRecognitionRecord(
                    id="sms-001",
                    elder_user_id="u-elder-001",
                    sender="95533",
                    message_text="您有一笔退款待领取，请点击短链并提供验证码完成补偿。",
                    masked_message_text="您有一笔退款待领取，请点击短链并提供验证码完成补偿。",
                    risk_level="high",
                    risk_score=92,
                    hit_rule_codes="SMS_REFUND_LINK,SMS_VERIFY_CODE",
                    hit_terms="退款链接,验证码,客服补偿",
                    analysis_summary="命中短信退款链接与验证码索取规则，存在高风险诈骗特征。",
                    suggestion_action="不要点击链接，不要透露验证码，建议联系子女核实并保留短信截图。",
                    occurred_at="2026-04-14T08:22:00Z",
                ),
                RiskAlert(
                    id="alert-001",
                    elder_user_id="u-elder-001",
                    source_type="sms",
                    source_record_id="sms-001",
                    risk_level="high",
                    risk_score=92,
                    title="疑似冒充客服退款短信",
                    summary="短信包含退款链接与验证码索取内容，存在诱导转账风险。",
                    reason_detail="命中“退款链接”“验证码”“客服补偿”多条高危规则，且短信中包含短链。",
                    suggestion_action="不要点击链接，不要透露验证码，建议联系子女核实并保留短信截图。",
                    status="pending_follow_up",
                    occurred_at="2026-04-14T08:22:00Z",
                ),
                RiskAlert(
                    id="alert-002",
                    elder_user_id="u-elder-002",
                    source_type="call",
                    source_record_id=None,
                    risk_level="medium",
                    risk_score=71,
                    title="疑似冒充公检法来电",
                    summary="通话中出现“安全账户”“配合调查”等敏感话术。",
                    reason_detail="命中公检法冒充与转账诱导话术，语义强度中等。",
                    suggestion_action="先挂断电话，通过官方渠道回拨核实，不要转账。",
                    status="new",
                    occurred_at="2026-04-13T19:10:00Z",
                ),
                NotificationRecord(
                    id="notify-001",
                    receiver_user_id="u-family-001",
                    alert_id="alert-001",
                    channel="app",
                    notification_type="risk_alert",
                    title="老人收到高风险诈骗短信",
                    content="李阿姨于 08:22 收到疑似退款诈骗短信，请尽快联系提醒。",
                    status="sent",
                    is_read=False,
                    sent_at="2026-04-14T08:23:00Z",
                ),
                NotificationRecord(
                    id="notify-002",
                    receiver_user_id="u-community-001",
                    alert_id="alert-001",
                    channel="workbench",
                    notification_type="community_dispatch",
                    title="辖区出现高风险老人告警",
                    content="李阿姨命中高风险诈骗规则，建议安排电话回访。",
                    status="sent",
                    is_read=True,
                    sent_at="2026-04-14T08:25:00Z",
                ),
                NotificationRecord(
                    id="notify-003",
                    receiver_user_id="u-family-002",
                    alert_id="alert-002",
                    channel="sms",
                    notification_type="risk_alert",
                    title="老人疑似接到冒充公检法电话",
                    content="周叔叔昨日晚间接到疑似诈骗电话，建议尽快回访。",
                    status="sent",
                    is_read=False,
                    sent_at="2026-04-13T19:15:00Z",
                ),
                Workorder(
                    id="wo-001",
                    workorder_no="GD202604140001",
                    alert_id="alert-001",
                    elder_user_id="u-elder-001",
                    title="李阿姨高风险短信回访工单",
                    priority="high",
                    status="processing",
                    assigned_to_user_id="u-community-001",
                    dispose_method="phone_visit",
                    dispose_result=None,
                    closed_at=None,
                ),
                WorkorderAction(
                    id="woa-001",
                    workorder_id="wo-001",
                    operator_user_id="u-admin-001",
                    action_type="create",
                    from_status=None,
                    to_status="pending",
                    note="高风险短信自动转工单。",
                ),
                WorkorderAction(
                    id="woa-002",
                    workorder_id="wo-001",
                    operator_user_id="u-admin-001",
                    action_type="assign",
                    from_status="pending",
                    to_status="processing",
                    note="已指派社区网格员张强电话回访。",
                ),
                RiskRule(
                    id="rule-001",
                    code="SMS_REFUND_LINK",
                    name="短信退款链接识别",
                    scene="sms",
                    risk_level="high",
                    priority=10,
                    status="enabled",
                    trigger_expression="contains(refund) && contains(short_link)",
                    reason_template="短信涉及退款链接与身份核验，疑似引导跳转诈骗页面。",
                    suggestion_template="不要点击链接，建议联系官方客服核实。",
                ),
                RiskRule(
                    id="rule-002",
                    code="CALL_POLICE_IMPERSONATION",
                    name="冒充公检法来电",
                    scene="call",
                    risk_level="medium",
                    priority=20,
                    status="enabled",
                    trigger_expression="contains(security_account) && contains(investigation)",
                    reason_template="来电出现安全账户与配合调查话术。",
                    suggestion_template="挂断后主动拨打官方电话核实。",
                ),
                RiskLexiconTerm(
                    id="lex-001",
                    term="验证码",
                    category="sms_keyword",
                    scene="sms",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="短信验证码索取高危词",
                ),
                RiskLexiconTerm(
                    id="lex-002",
                    term="点击链接",
                    category="sms_keyword",
                    scene="sms",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="短信诱导点击链接",
                ),
                RiskLexiconTerm(
                    id="lex-003",
                    term="退款",
                    category="sms_keyword",
                    scene="sms",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="退款补偿诈骗高频词",
                ),
                RiskLexiconTerm(
                    id="lex-004",
                    term="中奖",
                    category="sms_keyword",
                    scene="sms",
                    risk_level="medium",
                    status="enabled",
                    source="seed",
                    notes="中奖领奖诱导词",
                ),
                RiskLexiconTerm(
                    id="lex-005",
                    term="安全账户",
                    category="call_phrase",
                    scene="call",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="冒充公检法话术",
                ),
                RiskLexiconTerm(
                    id="lex-006",
                    term="配合调查",
                    category="call_phrase",
                    scene="call",
                    risk_level="medium",
                    status="enabled",
                    source="seed",
                    notes="施压调查话术",
                ),
                RiskLexiconTerm(
                    id="lex-007",
                    term="不要告诉家人",
                    category="call_phrase",
                    scene="call",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="隔离受害者话术",
                ),
                RiskLexiconTerm(
                    id="lex-008",
                    term="转到指定账户",
                    category="call_phrase",
                    scene="call",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="诱导转账话术",
                ),
                RiskRule(
                    id="rule-003",
                    code="SMS_VERIFY_CODE",
                    name="短信验证码索取识别",
                    scene="sms",
                    risk_level="high",
                    priority=20,
                    status="enabled",
                    trigger_expression="contains(验证码)",
                    reason_template="短信要求提供验证码，存在账号和支付信息泄露风险。",
                    suggestion_template="不要向任何人提供验证码，建议联系家属协助核实。",
                ),
                RiskRule(
                    id="rule-004",
                    code="SMS_PRIZE_TRAP",
                    name="短信中奖诱导识别",
                    scene="sms",
                    risk_level="medium",
                    priority=30,
                    status="enabled",
                    trigger_expression="contains(中奖)",
                    reason_template="短信存在中奖领奖诱导，可能诱骗转账或填写个人信息。",
                    suggestion_template="不要轻信中奖信息，不要缴纳手续费。",
                ),
                RiskRule(
                    id="rule-005",
                    code="CALL_ISOLATION_PRESSURE",
                    name="通话隔离施压识别",
                    scene="call",
                    risk_level="high",
                    priority=15,
                    status="enabled",
                    trigger_expression="contains(不要告诉家人)",
                    reason_template="来电方要求不要告诉家人，属于典型诈骗隔离受害者手法。",
                    suggestion_template="立即结束通话并联系家属核实。",
                ),
                RiskRule(
                    id="rule-006",
                    code="CALL_TRANSFER_GUIDE",
                    name="通话转账诱导识别",
                    scene="call",
                    risk_level="high",
                    priority=20,
                    status="enabled",
                    trigger_expression="contains(转到指定账户) && contains(远程共享屏幕)",
                    reason_template="通话要求转账并共享屏幕，存在高危资金诈骗风险。",
                    suggestion_template="不要转账，不要共享屏幕，建议联系社区或家属。",
                ),
                PromptTemplate(
                    id="content-001",
                    code="ALERT_HIGH_RISK_FAMILY",
                    name="高风险通知模板",
                    category="notification_template",
                    channel="app",
                    content="老人收到高风险诈骗信息，请尽快联系核实。",
                    status="enabled",
                    is_default=True,
                    notes="用于子女端高风险告警提醒。",
                ),
                EducationContent(
                    id="content-002",
                    title="警惕冒充客服退款骗局",
                    category="anti_fraud_article",
                    audience="elder",
                    summary="讲解常见退款诈骗套路与识别要点。",
                    content_body="常见退款诈骗会伪装客服，诱导点击链接并索取验证码。",
                    publish_status="published",
                    published_at="2026-04-13T16:00:00Z",
                ),
                SystemConfig(
                    id="cfg-001",
                    key="risk.high_threshold",
                    name="高风险分数阈值",
                    value="85",
                    group="risk",
                    description="达到该分值时自动通知子女并生成社区工单。",
                ),
                SystemConfig(
                    id="cfg-002",
                    key="notification.family_channels",
                    name="子女通知渠道",
                    value="app,sms",
                    group="notification",
                    description="高风险事件默认通知渠道。",
                ),
                SystemConfig(
                    id="cfg-003",
                    key="workorder.auto_dispatch",
                    name="自动派单开关",
                    value="true",
                    group="workorder",
                    description="高风险告警是否自动生成社区工单。",
                ),
            ]
        )
