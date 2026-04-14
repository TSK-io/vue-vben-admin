from pydantic import BaseModel, Field

from app.constants.roles import UserRole


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class TokenPayload(BaseModel):
    sub: str
    username: str
    roles: list[UserRole]
    exp: int


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    display_name: str
    roles: list[UserRole]
