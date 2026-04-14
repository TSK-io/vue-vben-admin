import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.constants.roles import UserRole
from app.core.deps import require_roles
from app.schemas.business import FamilyReminderCreateRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import send_family_reminder

router = APIRouter(prefix="/family")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.post("/reminders", summary="家属发送远程提醒", response_model=ApiResponse)
async def post_family_reminder(
    payload: FamilyReminderCreateRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(require_roles(UserRole.FAMILY, UserRole.ADMIN))],
) -> ApiResponse:
    data = send_family_reminder(user, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))
