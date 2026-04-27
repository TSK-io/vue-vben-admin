import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.constants.roles import UserRole
from app.core.deps import get_current_user
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.phone_directory import lookup_phone

router = APIRouter(prefix="/phone-directory")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("/lookup", summary="按电话号码查询用户", response_model=ApiResponse)
async def get_phone_lookup(
    request: Request,
    _: Annotated[UserProfile, Depends(get_current_user)],
    phone: str = Query(min_length=6, max_length=20),
    role: UserRole | None = Query(default=None),
) -> ApiResponse:
    return ApiResponse(
        data=lookup_phone(phone, role=role).model_dump(),
        meta=response_meta(request),
    )
