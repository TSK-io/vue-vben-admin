import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.constants.roles import UserRole
from app.core.deps import get_current_user, require_roles
from app.schemas.business import BindingCreateRequest, BindingUpdateRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import create_binding, delete_binding, list_bindings, update_binding

router = APIRouter(prefix="/bindings")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("", summary="查询老人绑定关系", response_model=ApiResponse)
async def get_bindings(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = [item.model_dump() for item in list_bindings(user)]
    return ApiResponse(data=data, meta=response_meta(request))


@router.post("", summary="新增老人绑定关系", response_model=ApiResponse)
async def add_binding(
    payload: BindingCreateRequest,
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.ELDER, UserRole.ADMIN))],
) -> ApiResponse:
    return ApiResponse(data=create_binding(payload).model_dump(), meta=response_meta(request))


@router.patch("/{binding_id}", summary="更新绑定关系", response_model=ApiResponse)
async def patch_binding(
    binding_id: str,
    payload: BindingUpdateRequest,
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.ELDER, UserRole.ADMIN))],
) -> ApiResponse:
    return ApiResponse(data=update_binding(binding_id, payload).model_dump(), meta=response_meta(request))


@router.delete("/{binding_id}", summary="解绑老人关系", response_model=ApiResponse)
async def remove_binding(
    binding_id: str,
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.ELDER, UserRole.ADMIN))],
) -> ApiResponse:
    delete_binding(binding_id)
    return ApiResponse(data={"success": True}, meta=response_meta(request))
