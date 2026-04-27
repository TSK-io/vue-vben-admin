from pydantic import BaseModel

from app.constants.roles import UserRole


class UserProfile(BaseModel):
    user_id: str
    username: str
    display_name: str
    phone: str
    roles: list[UserRole]
    permissions: list[str]

