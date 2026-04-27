# 桑榆智盾 New Version

这个目录用于重新整理项目，遵循 KISS 和 Occam's Razor：

- 后端先独立出来，保留可运行、可测试、可审核的 FastAPI 服务。
- 旧前端只作为参考，不在这里继续堆复杂度。
- 新前端后续从最小可演示闭环开始重建。

## 当前内容

```text
New_version
├── backend-fastapi                     后端服务，已从旧项目抽离
├── project_understand.md               项目理解精华
├── frontend_demo_refactor_execution_plan.md
├── read_audio_guard_improved.sh        本地音频反诈推理脚本
└── compose.yaml                        后端开发用 PostgreSQL
```

## 后端启动

```bash
cd New_version
docker compose up -d postgres

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

## 后端测试

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

## 下一步

先审核后端抽离结果。确认后，再围绕“老人手机端 + 输入端 + 子女通知 + 社区工单”的最小闭环重构新前端。
