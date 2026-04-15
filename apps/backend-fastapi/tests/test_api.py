import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ["APP_DATABASE_URL"] = f"sqlite:///{tempfile.gettempdir()}/guard_silver_test.db"

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_login_roles_and_refresh(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_demo", "password": "111"},
    )
    assert login_response.status_code == 200
    body = login_response.json()["data"]
    assert body["refresh_token"].startswith("refresh-")

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    roles_response = client.get("/api/v1/auth/roles", headers=headers)
    assert roles_response.status_code == 200
    assert len(roles_response.json()["data"]) >= 4

    refresh_response = client.post("/api/v1/auth/refresh", headers=headers, json={})
    assert refresh_response.status_code == 200
    assert refresh_response.json()["data"]["token_type"] == "bearer"
    runtime_response = client.get("/api/v1/health/runtime")
    assert runtime_response.status_code == 200
    assert runtime_response.json()["data"]["queue_strategy"]["max_concurrent_requests"] >= 1


def test_auth_register_and_login(client: TestClient) -> None:
    username = f"elder_new_user_{uuid.uuid4().hex[:8]}"
    phone = f"138{uuid.uuid4().hex[:8]}"[:11]
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "111",
            "display_name": "新注册老人",
            "phone": phone,
            "role": "elder",
            "invite_code": "ELDER-INVITE-001",
        },
    )
    assert register_response.status_code == 200
    body = register_response.json()["data"]
    assert body["roles"] == ["elder"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "111"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["data"]["display_name"] == "新注册老人"


def test_family_bindings_alerts_and_notifications(client: TestClient) -> None:
    headers = auth_headers(client, "family_demo", "111")

    bindings_response = client.get("/api/v1/bindings", headers=headers)
    assert bindings_response.status_code == 200
    assert bindings_response.json()["data"][0]["family_name"] == "王女士"

    alerts_response = client.get("/api/v1/risk-alerts", headers=headers)
    assert alerts_response.status_code == 200
    assert alerts_response.json()["data"]["items"][0]["elder_name"] == "李阿姨"

    notifications_response = client.get("/api/v1/notifications", headers=headers)
    assert notifications_response.status_code == 200
    assert notifications_response.json()["data"]["items"][0]["receiver_name"] == "王女士"


def test_community_workorder_transition(client: TestClient) -> None:
    headers = auth_headers(client, "community_demo", "111")

    elders_response = client.get("/api/v1/community/elders", headers=headers)
    assert elders_response.status_code == 200
    assert elders_response.json()["data"]["items"][0]["assigned_grid_member"] == "社区网格员张强"

    transition_response = client.post(
        "/api/v1/community/workorders/wo-001/transition",
        headers=headers,
        json={
            "action_type": "close",
            "to_status": "closed",
            "note": "已联系老人和家属确认，无转账发生。",
            "dispose_method": "phone_visit",
            "dispose_result": "完成电话回访并宣教提醒。",
        },
    )
    assert transition_response.status_code == 200
    assert transition_response.json()["data"]["status"] == "closed"


def test_admin_management_endpoints(client: TestClient) -> None:
    headers = auth_headers(client, "admin_demo", "111")

    users_response = client.get("/api/v1/admin/users", headers=headers)
    roles_response = client.get("/api/v1/admin/roles", headers=headers)
    rules_response = client.get("/api/v1/admin/rules", headers=headers)
    contents_response = client.get("/api/v1/admin/contents", headers=headers)
    configs_response = client.get("/api/v1/admin/system-config", headers=headers)

    assert users_response.status_code == 200
    assert roles_response.status_code == 200
    assert rules_response.status_code == 200
    assert contents_response.status_code == 200
    assert configs_response.status_code == 200
    assert users_response.json()["data"][0]["user_id"].startswith("u-")


def test_risk_recognition_sms_creates_alert_notifications_and_workorder(client: TestClient) -> None:
    headers = auth_headers(client, "admin_demo", "111")

    response = client.post(
        "/api/v1/risk-recognition/sms",
        headers=headers,
        json={
            "elder_user_id": "u-elder-001",
            "sender": "10690000",
            "message_text": "您好，您的退款已到账，请立即点击链接并提供验证码完成补偿。",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["risk_level"] == "high"
    assert "SMS_VERIFY_CODE" in data["hit_rule_codes"]
    assert data["alert_id"] is not None
    assert len(data["notification_ids"]) >= 2
    assert data["workorder_id"] is not None


def test_risk_recognition_call_creates_structured_result(client: TestClient) -> None:
    headers = auth_headers(client, "community_demo", "111")

    response = client.post(
        "/api/v1/risk-recognition/call",
        headers=headers,
        json={
            "elder_user_id": "u-elder-002",
            "caller_number": "01012345678",
            "duration_seconds": 180,
            "transcript_text": "这里是警方专线，你涉嫌案件，请配合调查，把资金转到指定账户，不要告诉家人。",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["scene"] == "call"
    assert data["risk_level"] == "high"
    assert "CALL_ISOLATION_PRESSURE" in data["hit_rule_codes"]
    assert data["reason_detail"]


def test_elder_help_settings_and_family_reminder(client: TestClient) -> None:
    elder_headers = auth_headers(client, "elder_demo", "111")
    family_headers = auth_headers(client, "family_demo", "111")

    help_response = client.post(
        "/api/v1/elder/help-requests",
        headers=elder_headers,
        json={
            "action_type": "联系家人",
            "note": "收到可疑电话，想先联系家人。",
            "notify_family": True,
            "notify_community": True,
        },
    )
    assert help_response.status_code == 200
    assert len(help_response.json()["data"]["notification_ids"]) >= 1

    settings_response = client.put(
        "/api/v1/elder/accessibility-settings",
        headers=elder_headers,
        json={
            "font_scale": "x-large",
            "high_contrast": True,
            "voice_assistant": True,
            "voice_speed": "slow",
        },
    )
    assert settings_response.status_code == 200
    assert settings_response.json()["data"]["font_scale"] == "x-large"

    reminder_response = client.post(
        "/api/v1/family/reminders",
        headers=family_headers,
        json={
            "elder_user_id": "u-elder-001",
            "content": "先别转账，我马上打给你。",
            "channel": "app",
        },
    )
    assert reminder_response.status_code == 200
    assert reminder_response.json()["data"]["receiver_name"] == "李阿姨"


def test_compliance_consents_export_requests_and_audit_logs(client: TestClient) -> None:
    headers = auth_headers(client, "family_demo", "111")

    policy_response = client.get("/api/v1/compliance/policy-summary")
    assert policy_response.status_code == 200
    assert "privacy_policy" in policy_response.json()["data"]["consent_types"]

    consent_response = client.post(
        "/api/v1/compliance/consents",
        headers=headers,
        json={
            "consent_type": "privacy_policy",
            "policy_version": "2026.04",
        },
    )
    assert consent_response.status_code == 200
    assert consent_response.json()["data"]["status"] == "granted"

    export_response = client.get("/api/v1/compliance/export", headers=headers)
    assert export_response.status_code == 200
    assert export_response.json()["data"]["profile"]["phone"] == "139****2001"

    correction_response = client.post(
        "/api/v1/compliance/corrections",
        headers=headers,
        json={
            "field_name": "phone",
            "new_value": "13900009999",
            "reason": "更换联系方式",
        },
    )
    assert correction_response.status_code == 200
    assert correction_response.json()["data"]["request_type"] == "correction"

    deletion_response = client.post(
        "/api/v1/compliance/deletions",
        headers=headers,
        json={"reason": "申请注销演示账号"},
    )
    assert deletion_response.status_code == 200
    assert deletion_response.json()["data"]["request_type"] == "deletion"

    requests_response = client.get("/api/v1/compliance/requests", headers=headers)
    assert requests_response.status_code == 200
    assert len(requests_response.json()["data"]) >= 2

    audit_response = client.get("/api/v1/compliance/audit-logs", headers=headers)
    assert audit_response.status_code == 200
    assert len(audit_response.json()["data"]) >= 1
