# 桑榆智盾后端服务

这是从旧工程中抽离出的独立 FastAPI 后端。当前目标是保持后端简单、可运行、可测试，作为后续新前端的唯一业务服务。

## 保留能力

- JWT 登录、角色权限。
- 老人、子女、社区、管理员、输入端账号。
- 老人与子女绑定。
- 短信文本风险识别。
- 通话文本风险识别。
- 通话音频风险识别，调用本地音频反诈脚本。
- 风险告警、子女通知、社区工单。
- 手机号查询，用于输入端按老人电话号码定位目标。
- 聊天和 WebRTC 相关接口暂时保留，作为后续电话模拟的参考能力。

## 目录

```text
backend-fastapi
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
├── tests
├── .env.example
├── alembic.ini
└── pyproject.toml
```

## 启动

在 `New_version` 目录启动数据库：

```bash
docker compose up -d postgres
```

进入后端目录：

```bash
cd backend-fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
.venv/bin/alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
```

## 测试

```bash
cd New_version/backend-fastapi
.venv/bin/pytest
```

## 默认账号

```text
elder_demo / 111
family_demo / 111
community_demo / 111
admin_demo / 111
input_demo / 111
```

## 核心接口

```http
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/phone-directory/lookup
POST /api/v1/risk-recognition/sms
POST /api/v1/risk-recognition/call
POST /api/v1/risk-recognition/call-audio
GET  /api/v1/risk-alerts
GET  /api/v1/notifications
GET  /api/v1/community/workorders
POST /api/v1/community/workorders/{workorder_id}/transition
```

## 音频推理脚本

`.env.example` 里默认通过环境变量控制音频模型：

```env
AUDIO_GUARD_ENABLED="false"
AUDIO_GUARD_SCRIPT_PATH="./read_audio_guard_improved.sh"
AUDIO_GUARD_TIMEOUT_SECONDS="180"
```

如果要启用真实音频识别，把 `New_version/read_audio_guard_improved.sh` 复制或软链到后端目录，或把 `AUDIO_GUARD_SCRIPT_PATH` 指到该脚本的绝对路径。

## 原则

后端只保留必要业务闭环。新前端重构时，不再把管理后台、演示页、手机端、输入端揉成一个复杂入口，而是逐步接入这些清晰接口。
