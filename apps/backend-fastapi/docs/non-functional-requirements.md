# 非功能需求落地说明

本文档对应 `TODO.md` 中“3. 非功能需求”，说明当前已经交付的基础能力与验收口径。

## 1. 隐私与数据保护

- 新增 `/api/v1/compliance/policy-summary`，统一返回隐私政策版本、授权类型和支持的数据更正字段。
- 新增 `/api/v1/compliance/consents`，支持记录用户授权动作，保存授权版本、来源 IP 和 User-Agent。
- 新增 `/api/v1/compliance/export`，支持当前登录用户导出个人数据摘要。
- 新增 `/api/v1/compliance/corrections` 与 `/api/v1/compliance/deletions`，支持提交更正与删除申请。
- 隐私申请内容使用 `Fernet` 加密后存储在 `privacy_requests.encrypted_payload`，避免明文落库。
- 导出结果默认对手机号做掩码处理，减少敏感信息直接暴露。

## 2. 审计日志

- 请求中间件会为全部 `/api/v1/*` 请求写入 `audit_logs`。
- 审计日志保留 `request_id`、用户、模块、方法、路径、耗时、队列等待时间和结果状态。
- 隐私授权、导出、更正、删除申请会额外写入业务审计事件，便于追踪关键操作。
- 当前用户可通过 `/api/v1/compliance/audit-logs` 查询自己的最近审计记录。

## 3. 高可用与低延迟保护

- 请求中间件增加并发闸门，基于 `APP_MAX_CONCURRENT_REQUESTS` 控制同时处理的请求数。
- 当等待超过 `APP_REQUEST_QUEUE_TIMEOUT_MS` 时，接口会返回 `503`，避免服务在高压下无限堆积。
- 所有响应头新增 `X-Queue-Wait-Time`，便于联调时判断排队情况。
- `/api/v1/health/runtime` 会输出近实时的平均耗时、P95、最大耗时和平均排队等待时间。

## 4. 合规承接

- V1 已补齐隐私政策摘要接口、授权记录、审计留痕、导出/更正/删除申请链路。
- 前端如果需要承接隐私弹窗或政策页，可直接消费 `policy-summary` 和 `consents` 接口。
- 当前实现为业务演示阶段的合规基础版，后续可以继续扩展为审核流、审批 SLA、素材页与正式法务文案。
