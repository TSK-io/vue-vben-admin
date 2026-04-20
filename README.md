# Silver Shield IM

Silver Shield IM is a multi-module project centered on a `uni-app` instant messaging client for end users.

The repository is now split by clear responsibilities:

- User client: `silver-shield-mobile`
- Admin console only: `apps/web-antd`
- Main business backend: `apps/backend-fastapi`
- Independent AI risk service: `ai-api-service`

`apps/web-antd` has been cleaned up into a pure admin console. End-user portals and their related frontend routes, pages, and APIs have been removed from the web app.

## Product Focus

- `silver-shield-mobile` is the real end-user product and should focus on conversations, contacts, chat, risk reminders, and SOS flows.
- `apps/web-antd` is the admin backend for admin accounts, permissions, risk records, content, and system settings.
- `apps/backend-fastapi` provides the main business APIs for mobile and admin.
- `ai-api-service` provides independent fraud and risk detection APIs for message text, chat logs, and suspicious links.

## Core Flow

`Login -> Conversations -> Chat -> Risk Detection -> Risk Reminder / SOS -> Admin Review / Configuration`

## Project Structure

- User client: `silver-shield-mobile`
- Admin frontend: `apps/web-antd`
- Main backend: `apps/backend-fastapi`
- Independent AI API Service: `ai-api-service`
- Requirements: [`需求文档.md`](./需求文档.md)
- TODO: [`TODO.md`](./TODO.md)

## Independent AI Service

This repository now also contains an isolated anti-fraud AI service in [`ai-api-service`](./ai-api-service/).

It is designed as a standalone service that:

- lives at the repository root but does not depend on the monorepo packages
- provides fraud-detection APIs for text, batch input, chat logs, suspicious links, and manual review
- supports remote Qwen-compatible endpoints through local environment configuration
- can fall back to rule-based detection when the remote model is unavailable or returns invalid structured output

Key documents:

- Module README: [`ai-api-service/README.md`](./ai-api-service/README.md)
- Module TODO: [`ai-api-service/TODO.md`](./ai-api-service/TODO.md)

Local configuration is expected in:

```bash
ai-api-service/.env.local
```

Main fields:

```bash
QWEN_BASE_URL=...
QWEN_API_KEY=...
QWEN_MODEL=...
```

## Run Locally

1. Install dependencies

```bash
pnpm install
```

2. Start admin frontend

```bash
pnpm dev:antd
```

3. Start mobile client

```bash
cd silver-shield-mobile
npm run dev:h5
```

4. Start backend

```bash
cd apps/backend-fastapi
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Build admin frontend

```bash
pnpm build:antd
```

## Notes

- This repository has been refocused from a scaffold project into a mobile IM plus admin-console project.
- The current goal is to make the mobile messaging flow and backend management boundary clear, stable, and demo-ready.
- The current `web` app is already restricted to admin-only modules and should not reintroduce end-user pages.

## License

[MIT](./LICENSE)
