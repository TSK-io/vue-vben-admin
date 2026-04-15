# 接口目录与文档草案

## 1. 认证与权限

- `POST /api/v1/auth/login`：账号登录，返回 `access_token + refresh_token`
- `POST /api/v1/auth/logout`：退出登录占位接口，统一前端退出流程
- `POST /api/v1/auth/refresh`：基于当前登录态刷新 access token
- `GET /api/v1/auth/me`：获取当前用户信息
- `GET /api/v1/auth/roles`：获取角色定义与权限项
- `GET /api/v1/auth/admin-permissions`：管理员权限校验示例接口

## 2. 已实现业务域接口

### 2.1 绑定关系

- `GET /api/v1/bindings`：按当前角色查看绑定关系
- `POST /api/v1/bindings`：新增绑定
- `PATCH /api/v1/bindings/{binding_id}`：更新绑定关系
- `DELETE /api/v1/bindings/{binding_id}`：解绑

### 2.2 风险告警与通知

- `POST /api/v1/risk-recognition/sms`：短信文本风险识别，写入识别记录并按风险等级触发告警
- `POST /api/v1/risk-recognition/call`：通话文本风险识别，写入识别记录并按风险等级触发告警
- `GET /api/v1/risk-alerts`：风险告警分页列表，支持 `risk_level/page/page_size`
- `GET /api/v1/risk-alerts/{alert_id}`：风险告警详情
- `GET /api/v1/notifications`：通知记录分页列表，支持 `is_read/page/page_size`
- `PATCH /api/v1/notifications/{notification_id}/read`：通知已读写回
- `PATCH /api/v1/notifications/{notification_id}/action`：通知关闭/跟进动作写回

### 2.3 社区侧

- `GET /api/v1/community/elders`：重点老人分页列表，支持 `keyword/risk_level`
- `POST /api/v1/community/elders/{elder_user_id}/follow-up`：补录电话回访、走访、宣教与人工风险标记
- `GET /api/v1/community/workorders`：社区工单分页列表，支持 `status`
- `GET /api/v1/community/workorders/{workorder_id}`：工单详情
- `POST /api/v1/community/workorders/{workorder_id}/transition`：工单流转、附件与协同备注回写

### 2.4 管理侧

- `GET /api/v1/admin/users`：管理端用户管理列表，支持 `keyword/role`
- `GET /api/v1/admin/roles`：角色权限列表
- `POST /api/v1/admin/roles`：创建角色权限配置
- `PUT /api/v1/admin/roles/{role_code}`：更新菜单、按钮、接口与数据范围配置
- `GET /api/v1/admin/rules`：风险规则列表
- `POST /api/v1/admin/rules` / `PUT /api/v1/admin/rules/{rule_id}`：规则维护
- `GET /api/v1/admin/lexicon`：风险词库列表
- `POST /api/v1/admin/lexicon` / `PUT /api/v1/admin/lexicon/{term_id}`：风险词维护
- `GET /api/v1/admin/contents`：内容管理列表
- `POST /api/v1/admin/contents` / `PUT /api/v1/admin/contents/{content_id}`：内容、案例、模板维护
- `GET /api/v1/admin/risk-alerts`：独立告警记录列表
- `GET /api/v1/admin/risk-alerts/{alert_id}`：告警详情与闭环追踪
- `GET /api/v1/admin/system-config`：系统配置列表

## 3. 统一响应约定

```json
{
  "code": 0,
  "message": "ok",
  "data": {},
  "meta": {
    "request_id": "trace-id",
    "timestamp": 1710000000000
  }
}
```

## 4. 鉴权约定

- 使用 `Authorization: Bearer <token>` 传递 JWT
- JWT 载荷至少包含：`sub`、`username`、`roles`、`exp`
- 接口权限优先通过依赖注入方式控制，便于后续按模块组合

## 5. 当前实现说明

- 风险识别 V1 已支持短信与通话文本规则识别、风险分级、统一结果结构、识别记录落库，以及高风险自动触发通知和工单
- 其余 3.4 接口采用数据库演示数据服务，便于前端联调和 OpenAPI 演示
- 数据结构已与 `docs/database-design.md` 的核心实体保持一致，后续可继续平滑扩展
