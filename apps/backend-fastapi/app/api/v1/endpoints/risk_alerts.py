import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.core.deps import get_current_user
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.business import get_paged_payload, get_risk_alert_detail, list_risk_alerts

router = APIRouter(prefix="/risk-alerts")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("", summary="风险告警列表", response_model=ApiResponse)
async def get_risk_alerts(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    risk_level: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> ApiResponse:
    items = list_risk_alerts(user, risk_level=risk_level)
    return ApiResponse(data=get_paged_payload(items, page, page_size), meta=response_meta(request))


@router.get("/{alert_id}", summary="风险告警详情", response_model=ApiResponse)
async def get_risk_alert(
    alert_id: str,
    request: Request,
    _: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=get_risk_alert_detail(alert_id).model_dump(), meta=response_meta(request))
