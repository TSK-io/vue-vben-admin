import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.core.deps import get_current_user
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import get_paged_payload, list_notifications

router = APIRouter(prefix="/notifications")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("", summary="通知记录列表", response_model=ApiResponse)
async def get_notifications(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    is_read: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> ApiResponse:
    items = list_notifications(user, is_read=is_read)
    return ApiResponse(data=get_paged_payload(items, page, page_size), meta=response_meta(request))
