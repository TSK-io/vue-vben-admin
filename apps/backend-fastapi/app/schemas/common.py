from typing import Any

from pydantic import BaseModel, Field


class MetaPayload(BaseModel):
    request_id: str | None = Field(default=None, description="Request trace id")
    timestamp: int | None = Field(default=None, description="Unix timestamp in milliseconds")


class ApiResponse(BaseModel):
    code: int = Field(default=0, description="0 means success")
    message: str = Field(default="ok")
    data: Any = Field(default=None)
    meta: MetaPayload | None = Field(default=None)


class ErrorDetail(BaseModel):
    field: str | None = None
    reason: str

