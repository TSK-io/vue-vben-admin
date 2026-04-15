import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.deps import get_current_user
from app.schemas.business import (
    PrivacyConsentGrantRequest,
    PrivacyCorrectionRequest,
    PrivacyDeletionRequest,
)
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.compliance import (
    export_user_data,
    get_policy_summary,
    grant_consent,
    list_audit_logs,
    list_consents,
    list_privacy_requests,
    submit_correction_request,
    submit_deletion_request,
)

router = APIRouter(prefix="/compliance")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


def client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("/policy-summary", summary="隐私与授权摘要", response_model=ApiResponse)
async def policy_summary(request: Request) -> ApiResponse:
    return ApiResponse(data=get_policy_summary().model_dump(), meta=response_meta(request))


@router.get("/consents", summary="当前用户授权记录", response_model=ApiResponse)
async def consents(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_consents(user)],
        meta=response_meta(request),
    )


@router.post("/consents", summary="新增授权记录", response_model=ApiResponse)
async def create_consent(
    payload: PrivacyConsentGrantRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = grant_consent(
        user,
        payload,
        ip_address=client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/export", summary="导出当前用户数据摘要", response_model=ApiResponse)
async def export_data(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=export_user_data(user).model_dump(), meta=response_meta(request))


@router.get("/requests", summary="查询隐私请求记录", response_model=ApiResponse)
async def privacy_requests(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_privacy_requests(user)],
        meta=response_meta(request),
    )


@router.post("/corrections", summary="提交数据更正申请", response_model=ApiResponse)
async def create_correction_request(
    payload: PrivacyCorrectionRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = submit_correction_request(user, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.post("/deletions", summary="提交删除申请", response_model=ApiResponse)
async def create_deletion_request(
    payload: PrivacyDeletionRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = submit_deletion_request(user, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/audit-logs", summary="查询当前用户审计日志", response_model=ApiResponse)
async def audit_logs(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_audit_logs(user)],
        meta=response_meta(request),
    )
