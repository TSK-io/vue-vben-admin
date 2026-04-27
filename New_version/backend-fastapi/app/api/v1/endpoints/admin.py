import time
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from app.constants.roles import UserRole
from app.core.deps import require_roles
from app.schemas.business import (
    ContentUpsertRequest,
    RiskRuleUpsertRequest,
    SystemConfigUpdateRequest,
)
from app.schemas.common import ApiResponse, MetaPayload
from app.services.business import (
    create_content,
    create_risk_rule,
    list_admin_users,
    list_contents,
    list_risk_rules,
    list_roles,
    list_system_configs,
    update_content,
    update_risk_rule,
    update_system_config,
)

router = APIRouter(prefix="/admin")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("/users", summary="管理端用户管理列表", response_model=ApiResponse)
async def get_admin_users(
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
    keyword: str | None = Query(default=None),
    role: UserRole | None = Query(default=None),
) -> ApiResponse:
    data = [item.model_dump() for item in list_admin_users(keyword=keyword, role=role)]
    return ApiResponse(data=data, meta=response_meta(request))


@router.get("/roles", summary="管理端角色权限列表", response_model=ApiResponse)
async def get_admin_roles(
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    data = [item.model_dump() for item in list_roles()]
    return ApiResponse(data=data, meta=response_meta(request))


@router.get("/rules", summary="管理端风险规则列表", response_model=ApiResponse)
async def get_admin_rules(
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    data = [item.model_dump() for item in list_risk_rules()]
    return ApiResponse(data=data, meta=response_meta(request))


@router.post("/rules", summary="新增风险规则", response_model=ApiResponse)
async def post_admin_rule(
    payload: RiskRuleUpsertRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    data = create_risk_rule(payload).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))


@router.put("/rules/{rule_id}", summary="更新风险规则", response_model=ApiResponse)
async def put_admin_rule(
    payload: RiskRuleUpsertRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
    rule_id: str = Path(),
) -> ApiResponse:
    data = update_risk_rule(rule_id, payload).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))


@router.get("/contents", summary="管理端内容管理列表", response_model=ApiResponse)
async def get_admin_contents(
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    data = [item.model_dump() for item in list_contents()]
    return ApiResponse(data=data, meta=response_meta(request))


@router.post("/contents", summary="新增内容", response_model=ApiResponse)
async def post_admin_content(
    payload: ContentUpsertRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    data = create_content(payload).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))


@router.put("/contents/{content_id}", summary="更新内容", response_model=ApiResponse)
async def put_admin_content(
    payload: ContentUpsertRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
    content_id: str = Path(),
) -> ApiResponse:
    data = update_content(content_id, payload).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))


@router.get("/system-config", summary="系统配置列表", response_model=ApiResponse)
async def get_system_config(
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    data = [item.model_dump() for item in list_system_configs()]
    return ApiResponse(data=data, meta=response_meta(request))


@router.put("/system-config/{config_key}", summary="更新系统配置", response_model=ApiResponse)
async def put_system_config(
    payload: SystemConfigUpdateRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN))],
    config_key: str = Path(),
) -> ApiResponse:
    data = update_system_config(config_key, payload).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))
