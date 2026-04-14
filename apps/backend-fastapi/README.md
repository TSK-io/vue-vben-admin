# 后端基础工程

`apps/backend-fastapi` 是“守护桑榆”项目的 `FastAPI` 后端基础工程，目标是先完成 V1 所需的后端底座能力：

- 环境配置管理：开发、测试、生产
- 统一响应结构与异常处理
- 请求日志、中间件、健康检查
- JWT 鉴权与角色权限依赖
- OpenAPI 文档与接口目录草案
- SQLAlchemy 数据模型与 Alembic 迁移底座

## 快速启动

```bash
cd apps/backend-fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`
- `http://127.0.0.1:8000/api/v1/health`

## 默认演示账号

当前已进入 3.4 真实业务 API 联调阶段，内置演示账号用于验证鉴权、角色权限和业务接口：

- `elder_demo / Elder123!`
- `family_demo / Family123!`
- `community_demo / Community123!`
- `admin_demo / Admin123!`

## 已落地的业务 API

- 认证：`/api/v1/auth/login`、`/logout`、`/refresh`、`/me`、`/roles`
- 绑定关系：`/api/v1/bindings`
- 风险告警：`/api/v1/risk-alerts`
- 通知记录：`/api/v1/notifications`
- 社区重点老人和工单：`/api/v1/community/elders`、`/community/workorders`
- 管理端：`/api/v1/admin/users`、`/roles`、`/rules`、`/contents`、`/system-config`

这些接口当前使用内置演示数据服务返回稳定结构，适合前端联调、OpenAPI 演示和后续替换为数据库实现。

## 运行测试

```bash
cd apps/backend-fastapi
.venv/bin/pytest
```

## 目录结构

```text
apps/backend-fastapi
├── app
│   ├── api
│   ├── constants
│   ├── core
│   ├── db
│   ├── models
│   ├── schemas
│   └── services
├── alembic
├── docs
├── .env.example
├── alembic.ini
└── pyproject.toml
```

## 数据库迁移

```bash
cd apps/backend-fastapi
.venv/bin/pip install -e ".[dev]"
.venv/bin/alembic upgrade head
```

默认通过 `APP_DATABASE_URL` 连接 PostgreSQL。首版已补齐 3.3 所需核心表结构，详见 [docs/database-design.md](/workspaces/vue-vben-admin/apps/backend-fastapi/docs/database-design.md)。
