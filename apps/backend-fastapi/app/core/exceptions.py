import time

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ApiResponse, ErrorDetail, MetaPayload


def build_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        response = ApiResponse(
            code=exc.status_code,
            message=str(exc.detail),
            data=None,
            meta=build_meta(request),
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ErrorDetail(field=".".join(map(str, err["loc"])), reason=err["msg"]).model_dump()
            for err in exc.errors()
        ]
        response = ApiResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="请求参数校验失败",
            data=details,
            meta=build_meta(request),
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response.model_dump())

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        response = ApiResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="服务器内部异常",
            data={"type": type(exc).__name__},
            meta=build_meta(request),
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())

