import time
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request

from app.constants.roles import UserRole
from app.core.deps import require_roles
from app.schemas.business import FamilyReminderCreateRequest, FamilyReminderTemplateUpsertRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import (
    create_family_reminder_template,
    list_family_reminder_receipts,
    list_family_reminder_templates,
    send_family_reminder,
    update_family_reminder_template,
)

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


@router.get("/reminder-templates", summary="家属提醒模板", response_model=ApiResponse)
async def get_family_reminder_templates(
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.FAMILY, UserRole.ADMIN))],
) -> ApiResponse:
    data = [item.model_dump() for item in list_family_reminder_templates()]
    return ApiResponse(data=data, meta=response_meta(request))


@router.post("/reminder-templates", summary="新增家属提醒模板", response_model=ApiResponse)
async def post_family_reminder_template(
    payload: FamilyReminderTemplateUpsertRequest,
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.FAMILY, UserRole.ADMIN))],
) -> ApiResponse:
    data = create_family_reminder_template(payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.put("/reminder-templates/{template_id}", summary="更新家属提醒模板", response_model=ApiResponse)
async def put_family_reminder_template(
    payload: FamilyReminderTemplateUpsertRequest,
    request: Request,
    _: Annotated[UserProfile, Depends(require_roles(UserRole.FAMILY, UserRole.ADMIN))],
    template_id: str = Path(),
) -> ApiResponse:
    data = update_family_reminder_template(template_id, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/reminder-receipts", summary="家属提醒回执", response_model=ApiResponse)
async def get_family_reminder_receipts(
    request: Request,
    user: Annotated[UserProfile, Depends(require_roles(UserRole.FAMILY, UserRole.ADMIN))],
) -> ApiResponse:
    data = [item.model_dump() for item in list_family_reminder_receipts(user)]
    return ApiResponse(data=data, meta=response_meta(request))
