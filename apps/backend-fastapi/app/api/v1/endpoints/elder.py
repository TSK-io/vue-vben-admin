import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.constants.roles import UserRole
from app.core.deps import get_current_user, require_roles
from app.schemas.business import AccessibilitySettingsUpdateRequest, HelpRequestCreate
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import (
    create_help_request,
    get_accessibility_settings,
    list_education_contents,
    update_accessibility_settings,
)

router = APIRouter(prefix="/elder")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.post("/help-requests", summary="老年端一键求助", response_model=ApiResponse)
async def post_help_request(
    payload: HelpRequestCreate,
    request: Request,
    user: Annotated[UserProfile, Depends(require_roles(UserRole.ELDER, UserRole.ADMIN))],
) -> ApiResponse:
    data = create_help_request(user, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/accessibility-settings", summary="读取适老设置", response_model=ApiResponse)
async def get_elder_accessibility_settings(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = get_accessibility_settings(user)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.put("/accessibility-settings", summary="更新适老设置", response_model=ApiResponse)
async def put_elder_accessibility_settings(
    payload: AccessibilitySettingsUpdateRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(require_roles(UserRole.ELDER, UserRole.ADMIN))],
) -> ApiResponse:
    data = update_accessibility_settings(user, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/knowledge", summary="防骗知识库", response_model=ApiResponse)
async def get_elder_knowledge(
    request: Request,
    _: Annotated[UserProfile, Depends(get_current_user)],
    category: str | None = Query(default=None),
) -> ApiResponse:
    data = [item.model_dump() for item in list_education_contents(audience="elder", category=category)]
    return ApiResponse(data=data, meta=response_meta(request))
