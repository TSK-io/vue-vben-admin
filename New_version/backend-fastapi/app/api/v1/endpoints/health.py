from fastapi import APIRouter, Request

from app.schemas.common import ApiResponse, MetaPayload

router = APIRouter()


@router.get("/health", summary="服务健康检查", response_model=ApiResponse)
async def health_check(request: Request) -> ApiResponse:
    return ApiResponse(
        data={"status": "ok", "service": "guard-silver-backend"},
        meta=MetaPayload(
            request_id=getattr(request.state, "request_id", None),
        ),
    )

