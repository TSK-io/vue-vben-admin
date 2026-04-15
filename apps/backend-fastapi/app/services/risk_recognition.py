from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import re
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy import select

from app.db.session import session_scope
from app.models import (
    ElderFamilyBinding,
    NotificationRecord,
    RiskAlert,
    RiskLexiconTerm,
    RiskRule,
    SmsRecognitionRecord,
    CallRecognitionRecord,
    User,
    UserRoleLink,
    Workorder,
    WorkorderAction,
)

RISK_LEVEL_SCORE = {"low": 30, "medium": 65, "high": 90}
RISK_LEVEL_PRIORITY = {"low": 1, "medium": 2, "high": 3}

DEFAULT_LEXICON_TERMS = [
    {"term": "验证码", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "短信验证码索取高危词"},
    {"term": "点击链接", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "短信诱导点击链接"},
    {"term": "短链接", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "短信短链跳转"},
    {"term": "退款", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "退款补偿类诈骗"},
    {"term": "补偿", "category": "sms_keyword", "scene": "sms", "risk_level": "medium", "notes": "客服补偿诱导"},
    {"term": "中奖", "category": "sms_keyword", "scene": "sms", "risk_level": "medium", "notes": "中奖领奖类诈骗"},
    {"term": "银行卡冻结", "category": "sms_keyword", "scene": "sms", "risk_level": "high", "notes": "冒充银行风控"},
    {"term": "安全账户", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "冒充公检法高危话术"},
    {"term": "配合调查", "category": "call_phrase", "scene": "call", "risk_level": "medium", "notes": "施压调查话术"},
    {"term": "不要告诉家人", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "隔离受害者常见话术"},
    {"term": "转到指定账户", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "诱导转账"},
    {"term": "远程共享屏幕", "category": "call_phrase", "scene": "call", "risk_level": "high", "notes": "远控协助诈骗"},
    {"term": "刷流水", "category": "call_phrase", "scene": "call", "risk_level": "medium", "notes": "刷单刷流水骗局"},
]

DEFAULT_RULES = [
    {
        "code": "SMS_REFUND_LINK",
        "name": "短信退款链接识别",
        "scene": "sms",
        "risk_level": "high",
        "priority": 10,
        "trigger_terms": ["退款", "点击链接"],
        "reason_template": "短信同时出现退款补偿和链接跳转信息，疑似冒充客服引导点击诈骗页面。",
        "suggestion_template": "不要点击链接，不要继续填写个人信息，先联系子女或官方客服核实。",
    },
    {
        "code": "SMS_VERIFY_CODE",
        "name": "短信验证码索取识别",
        "scene": "sms",
        "risk_level": "high",
        "priority": 20,
        "trigger_terms": ["验证码"],
        "reason_template": "短信要求提供验证码，存在盗取账号或支付验证信息风险。",
        "suggestion_template": "不要向任何人透露验证码，建议立即删除短信并联系家属确认。",
    },
    {
        "code": "SMS_PRIZE_TRAP",
        "name": "短信中奖诱导识别",
        "scene": "sms",
        "risk_level": "medium",
        "priority": 30,
        "trigger_terms": ["中奖"],
        "reason_template": "短信存在中奖领奖诱导，常见于引导转账或填写隐私信息骗局。",
        "suggestion_template": "不要轻信中奖信息，不要缴纳任何手续费。",
    },
    {
        "code": "CALL_POLICE_IMPERSONATION",
        "name": "冒充公检法来电",
        "scene": "call",
        "risk_level": "high",
        "priority": 10,
        "trigger_terms": ["安全账户", "配合调查"],
        "reason_template": "通话出现安全账户和配合调查等话术，符合冒充公检法诈骗特征。",
        "suggestion_template": "立即挂断，通过官方公布电话回拨核实，不要转账。",
    },
    {
        "code": "CALL_ISOLATION_PRESSURE",
        "name": "通话隔离施压识别",
        "scene": "call",
        "risk_level": "high",
        "priority": 15,
        "trigger_terms": ["不要告诉家人"],
        "reason_template": "来电方要求不要告诉家人，属于典型诈骗隔离受害者手法。",
        "suggestion_template": "结束通话后马上联系家属或社区人员，不要独自处理。",
    },
    {
        "code": "CALL_TRANSFER_GUIDE",
        "name": "通话转账诱导识别",
        "scene": "call",
        "risk_level": "high",
        "priority": 20,
        "trigger_terms": ["转到指定账户", "远程共享屏幕"],
        "reason_template": "通话包含指定账户转账或共享屏幕要求，存在资金被盗风险。",
        "suggestion_template": "不要转账，不要开启屏幕共享，建议立即联系家属。",
    },
]

DEFAULT_RULE_TERMS_BY_CODE = {
    item["code"]: list(item["trigger_terms"])
    for item in DEFAULT_RULES
}


@dataclass
class MatchedRule:
    code: str
    name: str
    risk_level: str
    priority: int
    hit_terms: list[str]
    reason_template: str
    suggestion_template: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _ensure_elder_exists(session, elder_user_id: str) -> User:
    elder = session.get(User, elder_user_id)
    if not elder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="老人用户不存在")
    return elder


def _load_lexicon_terms(session, scene: str) -> list[RiskLexiconTerm]:
    items = session.execute(
        select(RiskLexiconTerm)
        .where(RiskLexiconTerm.scene == scene, RiskLexiconTerm.status == "enabled")
        .order_by(RiskLexiconTerm.term.asc())
    ).scalars().all()
    if items:
        return items
    return [
        RiskLexiconTerm(
            id=f"default-lex-{scene}-{index}",
            term=item["term"],
            category=item["category"],
            scene=item["scene"],
            risk_level=item["risk_level"],
            status="enabled",
            source="builtin",
            notes=item["notes"],
        )
        for index, item in enumerate(DEFAULT_LEXICON_TERMS, start=1)
        if item["scene"] == scene
    ]


def _parse_trigger_terms(rule: RiskRule) -> list[str]:
    expression = (rule.trigger_expression or "").replace("&&", ",").replace("||", ",")
    parts = [part.strip() for part in expression.split(",") if part.strip()]
    terms: list[str] = []
    for part in parts:
        if "contains(" in part and ")" in part:
            term = part.split("contains(", 1)[1].split(")", 1)[0]
            term = term.strip().strip("'\"")
            if term:
                terms.append(term)
    return terms


def _looks_like_placeholder_terms(terms: list[str]) -> bool:
    if not terms:
        return True
    for term in terms:
        if any(ord(char) > 127 for char in term):
            return False
    return True


def _load_rules(session, scene: str) -> list[MatchedRule]:
    rows = session.execute(
        select(RiskRule)
        .where(RiskRule.scene == scene, RiskRule.status == "enabled")
        .order_by(RiskRule.priority.asc())
    ).scalars().all()
    matched_rules: list[MatchedRule] = []
    loaded_codes: set[str] = set()
    if rows:
        for row in rows:
            hit_terms = _parse_trigger_terms(row)
            if _looks_like_placeholder_terms(hit_terms):
                hit_terms = DEFAULT_RULE_TERMS_BY_CODE.get(row.code, [])
            matched_rules.append(
                MatchedRule(
                    code=row.code,
                    name=row.name,
                    risk_level=row.risk_level,
                    priority=row.priority,
                    hit_terms=hit_terms,
                    reason_template=row.reason_template or "",
                    suggestion_template=row.suggestion_template or "",
                )
            )
            loaded_codes.add(row.code)

    for item in DEFAULT_RULES:
        if item["scene"] != scene or item["code"] in loaded_codes:
            continue
        matched_rules.append(
            MatchedRule(
                code=item["code"],
                name=item["name"],
                risk_level=item["risk_level"],
                priority=item["priority"],
                hit_terms=list(item["trigger_terms"]),
                reason_template=item["reason_template"],
                suggestion_template=item["suggestion_template"],
            )
        )
    return matched_rules


def _detect_terms(text: str, lexicon_terms: list[RiskLexiconTerm]) -> tuple[list[str], str]:
    normalized = text.lower()
    matched_terms: list[str] = []
    max_level = "low"
    for term in lexicon_terms:
        if term.term.lower() in normalized:
            matched_terms.append(term.term)
            if RISK_LEVEL_PRIORITY[term.risk_level] > RISK_LEVEL_PRIORITY[max_level]:
                max_level = term.risk_level
    return sorted(set(matched_terms)), max_level


def _match_rules(text: str, rules: list[MatchedRule]) -> list[MatchedRule]:
    normalized = text.lower()
    hits: list[MatchedRule] = []
    for rule in rules:
        if not rule.hit_terms:
            continue
        if all(term.lower() in normalized for term in rule.hit_terms):
            hits.append(rule)
    return sorted(
        hits,
        key=lambda item: (-RISK_LEVEL_PRIORITY[item.risk_level], item.priority, item.code),
    )


def _score_result(hit_rules: list[MatchedRule], term_level: str) -> tuple[str, int]:
    if hit_rules:
        risk_level = hit_rules[0].risk_level
        base_score = RISK_LEVEL_SCORE[risk_level]
        bonus = min(8, max(0, len(hit_rules) - 1) * 3)
        return risk_level, min(99, base_score + bonus)
    return term_level, RISK_LEVEL_SCORE[term_level]


def _build_reason(scene_label: str, hit_rules: list[MatchedRule], hit_terms: list[str], risk_level: str) -> str:
    if hit_rules:
        rule_names = "、".join(rule.name for rule in hit_rules[:3])
        terms = "、".join(hit_terms[:6]) if hit_terms else "无"
        return f"{scene_label}命中规则：{rule_names}；命中风险词：{terms}；综合判定为{risk_level}风险。"
    if hit_terms:
        return f"{scene_label}命中风险词：{'、'.join(hit_terms[:6])}；当前为基础词库识别，综合判定为{risk_level}风险。"
    return f"{scene_label}未命中已启用规则和词库，当前判定为低风险。"


def _build_suggestion(hit_rules: list[MatchedRule], risk_level: str) -> str:
    if hit_rules and hit_rules[0].suggestion_template:
        return hit_rules[0].suggestion_template
    if risk_level == "high":
        return "建议立即停止继续沟通或操作，联系子女或社区人员核实。"
    if risk_level == "medium":
        return "建议保持警惕，不要转账或泄露隐私信息，先联系熟人核实。"
    return "目前未发现明显高危特征，仍建议保持警惕，不点击陌生链接。"


def _get_family_receivers(session, elder_user_id: str) -> list[User]:
    family_ids = session.scalars(
        select(ElderFamilyBinding.family_user_id).where(
            ElderFamilyBinding.elder_user_id == elder_user_id,
            ElderFamilyBinding.status == "active",
        )
    ).all()
    if not family_ids:
        return []
    return session.execute(select(User).where(User.id.in_(family_ids))).scalars().all()


def _get_community_receiver(session) -> User | None:
    community_ids = session.scalars(
        select(UserRoleLink.user_id).join(User, User.id == UserRoleLink.user_id).where(UserRoleLink.role_id == "role-community")
    ).all()
    if not community_ids:
        return None
    return session.execute(select(User).where(User.id.in_(community_ids)).order_by(User.created_at.asc())).scalars().first()


def _create_alert_related_records(
    session,
    *,
    elder: User,
    source_type: str,
    source_record_id: str,
    risk_level: str,
    risk_score: int,
    reason_detail: str,
    suggestion_action: str,
    occurred_at: str,
    title: str,
    summary: str,
) -> tuple[RiskAlert | None, list[NotificationRecord], Workorder | None]:
    if risk_level not in {"medium", "high"}:
        return None, [], None

    alert = RiskAlert(
        elder_user_id=elder.id,
        source_type=source_type,
        source_record_id=source_record_id,
        risk_level=risk_level,
        risk_score=risk_score,
        title=title,
        summary=summary,
        reason_detail=reason_detail,
        suggestion_action=suggestion_action,
        status="pending_follow_up" if risk_level == "high" else "new",
        occurred_at=occurred_at,
    )
    session.add(alert)
    session.flush()

    notifications: list[NotificationRecord] = []
    for family_user in _get_family_receivers(session, elder.id):
        notification = NotificationRecord(
            alert_id=alert.id,
            receiver_user_id=family_user.id,
            channel="app",
            notification_type="risk_alert",
            title=f"{elder.display_name}出现{risk_level}风险告警",
            content=f"{elder.display_name}触发{title}，建议尽快联系核实。",
            status="sent",
            sent_at=occurred_at,
        )
        notifications.append(notification)
        session.add(notification)

    workorder = None
    if risk_level == "high":
        community_user = _get_community_receiver(session)
        if community_user:
            community_notification = NotificationRecord(
                alert_id=alert.id,
                receiver_user_id=community_user.id,
                channel="workbench",
                notification_type="community_dispatch",
                title=f"{elder.display_name}出现高风险告警",
                content=f"{elder.display_name}触发{title}，建议尽快电话回访或上门核实。",
                status="sent",
                sent_at=occurred_at,
            )
            notifications.append(community_notification)
            session.add(community_notification)
            workorder = Workorder(
                alert_id=alert.id,
                elder_user_id=elder.id,
                assigned_to_user_id=community_user.id,
                workorder_no=f"GD{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}{elder.id[-3:]}",
                title=f"{elder.display_name}{title}处置工单",
                priority="high",
                status="pending",
                dispose_method="phone_visit",
            )
            session.add(workorder)
            session.flush()
            session.add(
                WorkorderAction(
                    workorder_id=workorder.id,
                    operator_user_id=community_user.id,
                    action_type="create",
                    from_status=None,
                    to_status="pending",
                    note="高风险识别结果自动生成工单。",
                )
            )

    return alert, notifications, workorder


def _analyze_text(scene: str, text: str) -> tuple[str, int, list[str], list[MatchedRule], str, str]:
    with session_scope() as session:
        lexicon_terms = _load_lexicon_terms(session, scene)
        rules = _load_rules(session, scene)
    hit_terms, term_level = _detect_terms(text, lexicon_terms)
    hit_rules = _match_rules(text, rules)
    risk_level, risk_score = _score_result(hit_rules, term_level)
    scene_label = "短信内容" if scene == "sms" else "通话文本"
    reason_detail = _build_reason(scene_label, hit_rules, hit_terms, risk_level)
    suggestion_action = _build_suggestion(hit_rules, risk_level)
    return risk_level, risk_score, hit_terms, hit_rules, reason_detail, suggestion_action


def _analyze_links(text: str) -> dict[str, object]:
    urls = re.findall(r"(https?://[^\s]+|[a-zA-Z0-9.-]+\.(?:cn|com|net|cc|top|vip|xyz)/[^\s]*)", text)
    normalized_urls: list[str] = []
    suspicious_domains: list[str] = []
    short_link_detected = False
    suspicious_reasons: list[str] = []
    ip_host_detected = False
    uncommon_tld_detected = False
    punycode_detected = False
    for item in urls:
        url = item if item.startswith("http") else f"https://{item}"
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        normalized_urls.append(url)
        if any(domain.endswith(suffix) for suffix in ("t.cn", "bit.ly", "url.cn", "dwz.cn")):
            short_link_detected = True
            suspicious_domains.append(domain)
            suspicious_reasons.append(f"{domain}: 短链接域名")
        if any(flag in domain for flag in ("refund", "bonus", "gift", "verify", "safe")):
            suspicious_domains.append(domain)
            suspicious_reasons.append(f"{domain}: 含诱导性英文关键词")
        if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", domain):
            ip_host_detected = True
            suspicious_domains.append(domain)
            suspicious_reasons.append(f"{domain}: 使用 IP 地址承载链接")
        if "xn--" in domain:
            punycode_detected = True
            suspicious_domains.append(domain)
            suspicious_reasons.append(f"{domain}: 疑似同形异义域名")
        if any(domain.endswith(suffix) for suffix in (".top", ".vip", ".xyz", ".cc")):
            uncommon_tld_detected = True
            suspicious_domains.append(domain)
            suspicious_reasons.append(f"{domain}: 命中高风险后缀")
    if not normalized_urls and ("点击链接" in text or "短链" in text):
        normalized_urls.append("embedded-link-indicator")
        short_link_detected = True
        suspicious_reasons.append("短信内容提示点击链接，但未给出完整 URL")
    return {
        "urls": normalized_urls,
        "short_link_detected": short_link_detected,
        "suspicious_domains": sorted(set(suspicious_domains)),
        "ip_host_detected": ip_host_detected,
        "uncommon_tld_detected": uncommon_tld_detected,
        "punycode_detected": punycode_detected,
        "suspicious_reasons": suspicious_reasons,
    }


def recognize_sms(*, elder_user_id: str, message_text: str, sender: str | None = None, occurred_at: str | None = None) -> dict:
    occurred_at = occurred_at or _now_iso()
    risk_level, risk_score, hit_terms, hit_rules, reason_detail, suggestion_action = _analyze_text("sms", message_text)
    link_analysis = _analyze_links(message_text)
    if (
        link_analysis["short_link_detected"]
        or link_analysis["suspicious_domains"]
        or link_analysis["ip_host_detected"]
        or link_analysis["uncommon_tld_detected"]
        or link_analysis["punycode_detected"]
    ):
        risk_score = min(99, risk_score + 8)
        risk_level = "high" if risk_score >= 85 else risk_level
        if link_analysis["suspicious_domains"]:
            reason_detail = (
                f"{reason_detail} 额外识别到可疑域名：{'、'.join(link_analysis['suspicious_domains'][:3])}。"
            )
        if link_analysis["suspicious_reasons"]:
            reason_detail = (
                f"{reason_detail} 链接特征命中：{'；'.join(link_analysis['suspicious_reasons'][:3])}。"
            )

    with session_scope() as session:
        elder = _ensure_elder_exists(session, elder_user_id)
        record = SmsRecognitionRecord(
            elder_user_id=elder_user_id,
            sender=sender,
            message_text=message_text,
            masked_message_text=message_text,
            risk_level=risk_level,
            risk_score=risk_score,
            hit_rule_codes=",".join(rule.code for rule in hit_rules),
            hit_terms=",".join(hit_terms),
            analysis_summary=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
        )
        session.add(record)
        session.flush()
        title = "疑似诈骗短信"
        summary = "短信命中诈骗关键词和规则，请谨慎处理。"
        alert, notifications, workorder = _create_alert_related_records(
            session,
            elder=elder,
            source_type="sms",
            source_record_id=record.id,
            risk_level=risk_level,
            risk_score=risk_score,
            reason_detail=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
            title=title,
            summary=summary,
        )
        return {
            "scene": "sms",
            "record_id": record.id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "hit_rule_codes": [rule.code for rule in hit_rules],
            "hit_terms": hit_terms,
            "reason_detail": reason_detail,
            "suggestion_action": suggestion_action,
            "alert_id": alert.id if alert else None,
            "notification_ids": [item.id for item in notifications],
            "workorder_id": workorder.id if workorder else None,
            "link_analysis": link_analysis,
        }


def recognize_call(
    *,
    elder_user_id: str,
    transcript_text: str,
    caller_number: str | None = None,
    duration_seconds: int | None = None,
    occurred_at: str | None = None,
) -> dict:
    occurred_at = occurred_at or _now_iso()
    risk_level, risk_score, hit_terms, hit_rules, reason_detail, suggestion_action = _analyze_text("call", transcript_text)

    with session_scope() as session:
        elder = _ensure_elder_exists(session, elder_user_id)
        record = CallRecognitionRecord(
            elder_user_id=elder_user_id,
            caller_number=caller_number,
            transcript_text=transcript_text,
            transcript_summary=transcript_text[:200],
            duration_seconds=duration_seconds,
            risk_level=risk_level,
            risk_score=risk_score,
            hit_rule_codes=",".join(rule.code for rule in hit_rules),
            hit_terms=",".join(hit_terms),
            analysis_summary=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
        )
        session.add(record)
        session.flush()
        title = "疑似诈骗来电"
        summary = "通话文本命中诈骗话术和规则，请尽快核实。"
        alert, notifications, workorder = _create_alert_related_records(
            session,
            elder=elder,
            source_type="call",
            source_record_id=record.id,
            risk_level=risk_level,
            risk_score=risk_score,
            reason_detail=reason_detail,
            suggestion_action=suggestion_action,
            occurred_at=occurred_at,
            title=title,
            summary=summary,
        )
        return {
            "scene": "call",
            "record_id": record.id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "hit_rule_codes": [rule.code for rule in hit_rules],
            "hit_terms": hit_terms,
            "reason_detail": reason_detail,
            "suggestion_action": suggestion_action,
            "alert_id": alert.id if alert else None,
            "notification_ids": [item.id for item in notifications],
            "workorder_id": workorder.id if workorder else None,
            "link_analysis": None,
        }
