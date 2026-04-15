import asyncio
import json
import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.runtime import runtime_metrics
from app.db.session import session_scope
from app.models import AuditLog
from app.schemas.common import MetaPayload

logger = logging.getLogger(__name__)
settings = get_settings()
request_semaphore = asyncio.Semaphore(settings.app_max_concurrent_requests)


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def _write_audit_log(
    request: Request,
    response_status: int,
    duration_ms: float,
    queue_wait_ms: float,
) -> None:
    if not request.url.path.startswith(settings.app_api_prefix):
        return

    user = getattr(request.state, "current_user", None)
    with session_scope() as session:
        session.add(
            AuditLog(
                user_id=getattr(user, "user_id", None),
                request_id=getattr(request.state, "request_id", None),
                action=f"{request.method} {request.url.path}",
                module=request.url.path.strip("/").split("/")[2] if len(request.url.path.strip("/").split("/")) >= 3 else "system",
                status="success" if response_status < 400 else "failed",
                ip_address=_client_ip(request),
                method=request.method,
                path=request.url.path,
                duration_ms=f"{duration_ms:.2f}",
                details=json.dumps(
                    {
                        "queue_wait_ms": round(queue_wait_ms, 2),
                        "status_code": response_status,
                    },
                    ensure_ascii=False,
                ),
            )
        )


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = request_id
        queue_started_at = time.perf_counter()

        try:
            await asyncio.wait_for(
                request_semaphore.acquire(),
                timeout=settings.app_request_queue_timeout_ms / 1000,
            )
        except TimeoutError:
            return JSONResponse(
                status_code=503,
                content={
                    "code": 503,
                    "message": "服务器繁忙，请稍后重试",
                    "data": {
                        "queue_timeout_ms": settings.app_request_queue_timeout_ms,
                    },
                    "meta": MetaPayload(request_id=request_id).model_dump(),
                },
            )

        queue_wait_ms = (time.perf_counter() - queue_started_at) * 1000
        started_at = time.perf_counter()

        try:
            response = await call_next(request)

            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            response.headers["X-Request-Id"] = request_id
            response.headers["X-Process-Time"] = str(duration_ms)
            response.headers["X-Queue-Wait-Time"] = f"{queue_wait_ms:.2f}"
            runtime_metrics.record(duration_ms, queue_wait_ms)

            logger.info(
                "request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "queue_wait_ms": round(queue_wait_ms, 2),
                },
            )
            _write_audit_log(request, response.status_code, duration_ms, queue_wait_ms)
            return response
        finally:
            request_semaphore.release()
