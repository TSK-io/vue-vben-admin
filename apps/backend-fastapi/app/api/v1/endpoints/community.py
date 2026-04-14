import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.constants.roles import UserRole
from app.core.deps import get_current_user, require_roles
from app.schemas.business import WorkorderTransitionRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import (
    get_paged_payload,
    get_workorder_detail,
    list_community_elders,
    list_workorders,
    transition_workorder,
)

router = APIRouter(prefix="/community")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("/elders", summary="社区重点老人列表", response_model=ApiResponse)
async def get_focus_elders(
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.COMMUNITY, UserRole.ADMIN))],
    keyword: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> ApiResponse:
    items = list_community_elders(keyword=keyword, risk_level=risk_level)
    return ApiResponse(data=get_paged_payload(items, page, page_size), meta=response_meta(request))


@router.get("/workorders", summary="社区工单列表", response_model=ApiResponse)
async def get_workorders(
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.COMMUNITY, UserRole.ADMIN))],
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> ApiResponse:
    items = list_workorders(status_filter=status)
    return ApiResponse(data=get_paged_payload(items, page, page_size), meta=response_meta(request))


@router.get("/workorders/{workorder_id}", summary="社区工单详情", response_model=ApiResponse)
async def get_workorder(
    workorder_id: str,
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.COMMUNITY, UserRole.ADMIN))],
) -> ApiResponse:
    return ApiResponse(data=get_workorder_detail(workorder_id).model_dump(), meta=response_meta(request))


@router.post("/workorders/{workorder_id}/transition", summary="社区工单流转", response_model=ApiResponse)
async def post_workorder_transition(
    workorder_id: str,
    payload: WorkorderTransitionRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(require_roles(UserRole.COMMUNITY, UserRole.ADMIN))],
) -> ApiResponse:
    data = transition_workorder(workorder_id, payload, user).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))
