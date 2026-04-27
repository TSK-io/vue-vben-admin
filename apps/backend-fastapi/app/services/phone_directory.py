from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.constants.roles import UserRole
from app.db.session import session_scope
from app.models import User, UserRoleLink
from app.schemas.business import PhoneDirectoryUser


def lookup_phone(phone: str, role: UserRole | None = None) -> PhoneDirectoryUser:
    normalized = phone.strip()
    with session_scope() as session:
        user = session.scalar(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRoleLink.role))
            .where(User.phone == normalized)
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到该电话号码")

        roles = [UserRole(link.role.code) for link in user.roles]
        if role and role not in roles:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该电话号码不属于指定角色")

        return PhoneDirectoryUser(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            phone=user.phone,
            roles=roles,
            status=user.status,
        )
