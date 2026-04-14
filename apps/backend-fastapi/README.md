# 后端基础工程

`apps/backend-fastapi` 是“守护桑榆”项目的 `FastAPI` 后端基础工程，目标是先完成 V1 所需的后端底座能力：

- 环境配置管理：开发、测试、生产
- 统一响应结构与异常处理
- 请求日志、中间件、健康检查
- JWT 鉴权与角色权限依赖
- OpenAPI 文档与接口目录草案

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

当前为基础工程阶段，内置演示账号用于验证鉴权与角色权限：

- `elder_demo / Elder123!`
- `family_demo / Family123!`
- `community_demo / Community123!`
- `admin_demo / Admin123!`

## 目录结构

```text
apps/backend-fastapi
├── app
│   ├── api
│   ├── constants
│   ├── core
│   ├── schemas
│   └── services
├── docs
├── .env.example
└── pyproject.toml
```

后续 3.3、3.4 会在此目录继续补充数据库模型、迁移和真实业务接口。

