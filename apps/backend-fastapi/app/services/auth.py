from dataclasses import dataclass

from fastapi import HTTPException, status

from app.constants.roles import UserRole
from app.core.security import create_access_token
from app.schemas.auth import LoginResponse
from app.schemas.user import UserProfile


@dataclass(frozen=True)
class DemoUser:
    user_id: str
    username: str
    password: str
    display_name: str
    phone: str
    roles: list[UserRole]
    permissions: list[str]


DEMO_USERS = [
    DemoUser(
        user_id="u-elder-001",
        username="elder_demo",
        password="Elder123!",
        display_name="李阿姨",
        phone="138****1001",
        roles=[UserRole.ELDER],
        permissions=["elder:read", "sos:create"],
    ),
    DemoUser(
        user_id="u-family-001",
        username="family_demo",
        password="Family123!",
        display_name="王女士",
        phone="139****2001",
        roles=[UserRole.FAMILY],
        permissions=["family:read", "alerts:read", "notifications:read"],
    ),
    DemoUser(
        user_id="u-community-001",
        username="community_demo",
        password="Community123!",
        display_name="社区网格员张强",
        phone="137****3001",
        roles=[UserRole.COMMUNITY],
        permissions=["community:read", "workorder:read", "workorder:update"],
    ),
    DemoUser(
        user_id="u-admin-001",
        username="admin_demo",
        password="Admin123!",
        display_name="系统管理员",
        phone="136****4001",
        roles=[UserRole.ADMIN],
        permissions=["*"],
    ),
]


def authenticate_user(username: str, password: str) -> LoginResponse:
    matched_user = next(
        (user for user in DEMO_USERS if user.username == username and user.password == password),
        None,
    )
    if not matched_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token, expires_at = create_access_token(
        user_id=matched_user.user_id,
        username=matched_user.username,
        roles=[role.value for role in matched_user.roles],
    )
    return LoginResponse(
        access_token=token,
        expires_in=expires_at,
        user_id=matched_user.user_id,
        username=matched_user.username,
        display_name=matched_user.display_name,
        roles=matched_user.roles,
    )


def get_demo_user_by_id(user_id: str) -> UserProfile | None:
    matched_user = next((user for user in DEMO_USERS if user.user_id == user_id), None)
    if not matched_user:
        return None
    return UserProfile(
        user_id=matched_user.user_id,
        username=matched_user.username,
        display_name=matched_user.display_name,
        phone=matched_user.phone,
        roles=matched_user.roles,
        permissions=matched_user.permissions,
    )

