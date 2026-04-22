import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ["APP_DATABASE_URL"] = f"sqlite:///{tempfile.gettempdir()}/guard_silver_test.db"
os.environ["CHAT_MESSAGE_RATE_LIMIT_COUNT"] = "2"
os.environ["CHAT_MESSAGE_RATE_LIMIT_WINDOW_SECONDS"] = "60"

from app.main import app
from app.services.chat import rate_limiter


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


def test_auth_register_and_login(client: TestClient) -> None:
    username = f"elder_new_user_{uuid.uuid4().hex[:8]}"
    phone = f"138{uuid.uuid4().int % 100000000:08d}"
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


def test_chat_conversation_flow_and_unread_summary(client: TestClient) -> None:
    rate_limiter._events.clear()
    family_headers = auth_headers(client, "family_demo", "111")
    elder_headers = auth_headers(client, "elder_demo", "111")

    recommendation_response = client.get("/api/v1/chats/users/recommendations", headers=family_headers)
    assert recommendation_response.status_code == 200
    recommended = recommendation_response.json()["data"]
    assert any(item["user_id"] == "u-elder-001" for item in recommended)

    search_response = client.get("/api/v1/chats/users/search?keyword=李阿姨", headers=family_headers)
    assert search_response.status_code == 200
    elder_user = search_response.json()["data"][0]
    assert elder_user["user_id"] == "u-elder-001"

    create_response = client.post(
        "/api/v1/chats/conversations",
        headers=family_headers,
        json={"conversation_type": "direct", "participant_user_ids": ["u-elder-001"]},
    )
    assert create_response.status_code == 200
    conversation = create_response.json()["data"]

    send_response = client.post(
        f"/api/v1/chats/conversations/{conversation['id']}/messages",
        headers=family_headers,
        json={"message_type": "text", "content_text": "先别点链接，也不要给验证码。"},
    )
    assert send_response.status_code == 200
    message = send_response.json()["data"]
    assert message["risk_level"] == "high"

    unread_response = client.get("/api/v1/chats/unread-summary", headers=elder_headers)
    assert unread_response.status_code == 200
    assert unread_response.json()["data"]["total_unread"] >= 1

    read_response = client.post(
        f"/api/v1/chats/conversations/{conversation['id']}/read",
        headers=elder_headers,
        json={"last_read_message_id": message["id"]},
    )
    assert read_response.status_code == 200
    assert read_response.json()["data"]["total_unread"] == 0


def test_chat_websocket_ping_and_typing(client: TestClient) -> None:
    rate_limiter._events.clear()
    headers = auth_headers(client, "family_demo", "111")
    token = headers["Authorization"].replace("Bearer ", "", 1)

    with client.websocket_connect(f"/api/v1/chats/ws?token={token}") as websocket:
        connected = websocket.receive_json()
        assert connected["event"] == "connected"

        websocket.send_json({"event": "ping"})
        pong = websocket.receive_json()
        assert pong["event"] == "pong"


def test_chat_blacklist_report_and_relationships(client: TestClient) -> None:
    rate_limiter._events.clear()
    family_headers = auth_headers(client, "family_demo", "111")
    elder_headers = auth_headers(client, "elder_demo", "111")

    blacklist_response = client.post(
        "/api/v1/chats/blacklist",
        headers=elder_headers,
        json={"target_user_id": "u-family-001", "reason": "频繁发送可疑链接"},
    )
    assert blacklist_response.status_code == 200
    assert blacklist_response.json()["data"]["is_blocked"] is True

    relationships_response = client.get("/api/v1/chats/relationships", headers=elder_headers)
    assert relationships_response.status_code == 200
    assert any(item["target_user_id"] == "u-family-001" and item["is_blocked"] for item in relationships_response.json()["data"])

    create_response = client.post(
        "/api/v1/chats/conversations",
        headers=family_headers,
        json={"conversation_type": "direct", "participant_user_ids": ["u-elder-001"]},
    )
    assert create_response.status_code == 403

    report_response = client.post(
        "/api/v1/chats/report",
        headers=elder_headers,
        json={"target_user_id": "u-family-001", "reason": "疑似诱导转账"},
    )
    assert report_response.status_code == 200
    assert report_response.json()["data"]["is_reported"] is True

    unblacklist_response = client.delete("/api/v1/chats/blacklist/u-family-001", headers=elder_headers)
    assert unblacklist_response.status_code == 200
    assert unblacklist_response.json()["data"]["is_blocked"] is False


def test_chat_rate_limit_rejects_burst_messages(client: TestClient) -> None:
    rate_limiter._events.clear()
    family_headers = auth_headers(client, "family_demo", "111")

    create_response = client.post(
        "/api/v1/chats/conversations",
        headers=family_headers,
        json={"conversation_type": "direct", "participant_user_ids": ["u-elder-002"]},
    )
    assert create_response.status_code == 200
    conversation_id = create_response.json()["data"]["id"]

    for content in ["第一条提醒", "第二条提醒"]:
        response = client.post(
            f"/api/v1/chats/conversations/{conversation_id}/messages",
            headers=family_headers,
            json={"message_type": "text", "content_text": content},
        )
        assert response.status_code == 200

    limited_response = client.post(
        f"/api/v1/chats/conversations/{conversation_id}/messages",
        headers=family_headers,
        json={"message_type": "text", "content_text": "第三条提醒"},
    )
    assert limited_response.status_code == 429


def test_chat_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/chats/conversations")
    assert response.status_code == 401
