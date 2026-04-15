from fastapi import APIRouter, Request
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import get_engine
from app.core.runtime import runtime_metrics
from app.schemas.common import ApiResponse, MetaPayload

router = APIRouter()
settings = get_settings()


@router.get("/health", summary="服务健康检查", response_model=ApiResponse)
async def health_check(request: Request) -> ApiResponse:
    return ApiResponse(
        data={"status": "ok", "service": "guard-silver-backend"},
        meta=MetaPayload(
            request_id=getattr(request.state, "request_id", None),
        ),
    )


@router.get("/health/runtime", summary="服务运行态指标", response_model=ApiResponse)
async def runtime_health(request: Request) -> ApiResponse:
    return ApiResponse(
        data={
            "status": "ok",
            "queue_strategy": {
                "max_concurrent_requests": settings.app_max_concurrent_requests,
                "queue_timeout_ms": settings.app_request_queue_timeout_ms,
                "slow_request_threshold_ms": settings.app_slow_request_threshold_ms,
            },
            "metrics": runtime_metrics.snapshot(),
        },
        meta=MetaPayload(
            request_id=getattr(request.state, "request_id", None),
        ),
    )


@router.get("/health/ready", summary="服务就绪检查", response_model=ApiResponse)
async def readiness_check(request: Request) -> ApiResponse:
    database_status = "ok"
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database_status = "error"

    status = "ok" if database_status == "ok" else "degraded"
    return ApiResponse(
        data={
            "status": status,
            "environment": settings.app_env,
            "database": database_status,
            "service": "guard-silver-backend",
        },
        meta=MetaPayload(
            request_id=getattr(request.state, "request_id", None),
        ),
    )
