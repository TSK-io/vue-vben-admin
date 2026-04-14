import time

from fastapi import APIRouter, Request

from app.schemas.common import ApiResponse, MetaPayload

router = APIRouter()


@router.get("/outline", summary="接口目录草案", response_model=ApiResponse)
async def api_outline(request: Request) -> ApiResponse:
    outline = [
        {"module": "auth", "endpoints": ["POST /auth/login", "POST /auth/logout", "POST /auth/refresh", "GET /auth/me"]},
        {"module": "elder-binding", "endpoints": ["GET /bindings", "POST /bindings", "DELETE /bindings/{id}"]},
        {"module": "risk-alerts", "endpoints": ["GET /risk-alerts", "GET /risk-alerts/{id}"]},
        {"module": "notifications", "endpoints": ["GET /notifications", "PATCH /notifications/{id}/read"]},
        {"module": "community-workorders", "endpoints": ["GET /workorders", "GET /workorders/{id}", "POST /workorders/{id}/transition"]},
        {"module": "admin-config", "endpoints": ["GET /admin/users", "GET /admin/roles", "GET /admin/rules", "GET /admin/templates", "GET /admin/system-config"]},
    ]
    return ApiResponse(
        data=outline,
        meta=MetaPayload(
            request_id=getattr(request.state, "request_id", None),
            timestamp=int(time.time() * 1000),
        ),
    )

