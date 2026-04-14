import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.constants.roles import UserRole
from app.core.deps import require_roles
from app.schemas.business import CallRecognitionRequest, RiskRecognitionResult, SmsRecognitionRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.services.risk_recognition import recognize_call, recognize_sms

router = APIRouter(prefix="/risk-recognition")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.post("/sms", summary="短信文本风险识别", response_model=ApiResponse)
async def post_sms_recognition(
    payload: SmsRecognitionRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN, UserRole.COMMUNITY, UserRole.ELDER, UserRole.FAMILY))],
) -> ApiResponse:
    result = RiskRecognitionResult(**recognize_sms(**payload.model_dump()))
    return ApiResponse(data=result.model_dump(), meta=response_meta(request))


@router.post("/call", summary="通话文本风险识别", response_model=ApiResponse)
async def post_call_recognition(
    payload: CallRecognitionRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN, UserRole.COMMUNITY, UserRole.ELDER, UserRole.FAMILY))],
) -> ApiResponse:
    result = RiskRecognitionResult(**recognize_call(**payload.model_dump()))
    return ApiResponse(data=result.model_dump(), meta=response_meta(request))
