# 桑榆智盾前端改造落地执行计划

更新时间：2026-04-27

本文基于 `frontend_demo_refactor_plan.md`，结合当前仓库代码现状，拆解后续前端改造的具体落地路径。核心结论是：现有系统已经具备用户手机号、角色路由、风险识别、通知、社区工单和 WebRTC 通话底座，但还缺少以电话号码为核心的通信事件层、输入端角色、老人端手机式交互、短信场景、号码级安全联系人和黑名单。

## 1. 当前代码现状

### 1.1 项目结构

当前仓库是前后端一体结构：

```text
apps/web-antd             Vue 3 + Vben Admin + Ant Design Vue 前端
apps/backend-fastapi      FastAPI 后端
```

前端核心目录：

```text
apps/web-antd/src/router/routes/modules/guardian.ts
apps/web-antd/src/api/core/*.ts
apps/web-antd/src/store/chat.ts
apps/web-antd/src/views/guardian-shield
```

后端核心目录：

```text
apps/backend-fastapi/app/constants/roles.py
apps/backend-fastapi/app/models
apps/backend-fastapi/app/schemas
apps/backend-fastapi/app/services
apps/backend-fastapi/app/api/v1/endpoints
```

### 1.2 已有角色和路由

前端已经有以下角色入口：

```text
/elder        老年端
/family       子女端
/community    社区端
/admin        管理端
/chat         实时聊天与 WebRTC 通话中心
```

路由文件为：

```text
apps/web-antd/src/router/routes/modules/guardian.ts
```

现有老年端路由：

```text
/elder/home
/elder/alerts
/elder/help
/elder/family-binding
/elder/knowledge
/elder/settings
```

现有子女端路由：

```text
/family/overview
/family/seniors
/family/alerts
/family/notifications
/family/settings
```

现有社区端路由：

```text
/community/dashboard
/community/seniors
/community/workorders
/community/education
/community/reports
```

当前缺口：

- 没有 `/input` 输入端角色和路由。
- 老人端没有 `/elder/phone`、`/elder/messages`、`/elder/contacts`。
- 老人端仍保留 `/elder/help` 一键求助入口，与新蓝图第一阶段“取消 SOS”不一致。
- 子女端没有 `/family/seniors/:id` 家人详情页。

### 1.3 已有用户手机号能力

后端 `users` 表已经有手机号字段：

```text
apps/backend-fastapi/app/models/user.py
```

种子用户也已经有固定手机号：

```text
elder_demo       13800001001
elder_demo_2     13800001002
family_demo      13900002001
family_demo_2    13900002002
community_demo   13700003001
admin_demo       13600004001
```

前端 `getUserInfoApi` 读取了 `phone`，但当前只放在 `UserInfo.desc`，没有作为明确的 `currentUser.phone` 业务字段使用。

当前缺口：

- 号码没有成为前端通信、联系人、黑名单和事件追踪的主键。
- 没有通过电话号码查找老人用户的普通业务接口。
- 绑定关系仍主要暴露 `elderUserId/familyUserId`，没有把老人电话、子女电话作为 UI 主信息展示。

### 1.4 已有风险识别能力

后端已实现：

```http
POST /api/v1/risk-recognition/sms
POST /api/v1/risk-recognition/call
POST /api/v1/risk-recognition/call-audio
GET  /api/v1/risk-alerts
GET  /api/v1/notifications
GET  /api/v1/community/workorders
POST /api/v1/community/workorders/{workorder_id}/transition
```

风险识别服务会：

- 写入短信或通话识别记录。
- 中高风险时创建风险告警。
- 通知绑定子女。
- 高风险时创建社区工单。

当前缺口：

- 前端 `risk.ts` 只有风险告警列表读取，没有封装 `recognizeSmsApi`、`recognizeCallTextApi`。
- 通话录音识别只在 `chat.ts` 中通过 `uploadCallAudioRecognitionApi` 使用。
- 当前通话录音小于 60 秒会跳过模型识别，比赛短演示需要通话文本识别兜底。
- 风险返回后，前端没有统一的风险弹窗、自动黑名单、通信事件状态更新流程。

### 1.5 已有 WebRTC 通话底座

前端已有：

```text
apps/web-antd/src/store/chat.ts
apps/web-antd/src/components/chat/chat-call-host.vue
apps/web-antd/src/views/guardian-shield/chat/index.vue
```

能力包括：

- WebSocket 连接。
- 会话列表。
- 一对一文本消息。
- 语音 / 视频通话。
- 来电弹窗。
- 接听、拒接、挂断、计时。
- 老人端通话录音上传识别。

当前缺口：

- 通话身份是 `initiator_user_id / receiver_user_id`，不是 `source_phone / target_phone`。
- 老人端看到的是聊天对象，不是剧情号码。
- 输入端无法设置“本次发起号码”。
- 通话结束上传识别时没有稳定传入本次剧情 `caller_number`。
- WebRTC 通话入口在 `/chat/index`，不是老人端手机式 `/elder/phone`。

### 1.6 已有黑名单能力

后端聊天模块有用户级黑名单：

```text
chat_user_relations.owner_user_id
chat_user_relations.target_user_id
is_blocked
```

当前缺口：

- 这是用户对用户的 IM 黑名单，不是老人对电话号码的黑名单。
- 陌生号码、诈骗号码、输入端自定义号码无法进入这个黑名单模型。
- 没有安全联系人号码表。
- 没有号码级“自动拉黑”动作记录。

### 1.7 当前 UI 状态

当前各角色页面已经能展示风险、通知和工单，但整体仍是后台 / 工作台页面：

- 老人端 `/elder/home` 是卡片式仪表盘，不像手机操作系统。
- 老人端 `/elder/alerts` 是风险列表页，不是手机弹窗式提醒。
- 子女端和社区端已有统计卡、列表和详情弹窗，可继续改造。
- 页面中大量 hero 文案和说明性文字适合开发说明，但比赛演示时应减少“解释功能”的可见文本。

## 2. 蓝图与现状差距矩阵

| 蓝图目标 | 当前状态 | 缺口判断 | 落地动作 |
| --- | --- | --- | --- |
| 电话号码作为身份骨架 | 用户表已有 `phone` | 未贯穿前端通信逻辑 | 新增号码领域类型、号码查找和事件结构 |
| 输入端可设置本次发起号码 | 无 `/input` 角色 | 缺完整入口 | 新增 input 角色、路由、页面 |
| 老人端像手机 OS | `/elder/home` 是后台卡片 | 需重做视觉和交互 | 重做 home，新增 phone/messages/contacts |
| Web 模拟电话 | `/chat` 已有 WebRTC | 未支持剧情号码 | 复用 chat store，扩展 call metadata |
| Web 模拟短信 | 只有聊天消息 | 无短信事件模型 | 新增短信事件 store 和页面 |
| 陌生短信首次识别 | 后端有 SMS 识别 | 前端未调用 | 新增 `recognizeSmsApi` 和陌生号码判断 |
| 通话结束后识别 | 后端有 call/call-audio | 短演示不稳定 | 音频识别 + 通话文本兜底 |
| 自动黑名单 | 无号码级黑名单 | 关键缺口 | 先前端状态实现，后端后续持久化 |
| 子女端查看事件链路 | 有 alerts/notifications | 缺号码和通信详情 | 扩展列表字段和详情页 |
| 社区端处置闭环 | 有 dashboard/workorders | 缺号码关系链 | 工单详情补电话链路和联系动作 |

## 3. 总体改造策略

### 3.1 推荐优先级

第一阶段目标不是把所有后端数据模型一次性重写，而是先做出比赛可演示闭环：

```text
输入端设置 source_phone
-> 按 target_phone 找到老人
-> 老人端收到电话 / 短信
-> 陌生号码触发识别
-> 风险弹窗
-> 自动加入老人端号码黑名单
-> 子女端看到风险事件
-> 社区端看到工单
```

推荐采用“两层状态”：

```text
后端真实层：
用户、手机号、绑定、风险识别、通知、工单、WebRTC 通话

前端剧情层：
source_phone、target_phone、联系人、黑名单、短信事件、电话剧情状态、风险弹窗状态
```

### 3.2 必须补的轻后端能力

虽然蓝图希望第一阶段尽量不重写后端，但以下能力建议轻量补齐，否则多角色登录会很脆：

1. 新增 `input` 角色。
2. 新增 `input_demo` 种子账号。
3. 新增手机号查找接口，例如：

```http
GET /api/v1/phone-directory/lookup?phone=13800001001
```

返回最小信息：

```ts
interface PhoneDirectoryUser {
  userId: string;
  displayName: string;
  phone: string;
  roles: string[];
  status: string;
}
```

4. 允许 `input` 角色调用风险识别接口，或新增专用通信输入接口代理风险识别。

不建议第一阶段重写风险模型、通知模型和工单模型。

### 3.3 前端剧情层存储建议

第一阶段可以先用 Pinia + `localStorage` + `BroadcastChannel` 组织剧情状态：

```text
store/communication.ts
localStorage key: guardian-shield:communication-events
localStorage key: guardian-shield:phone-contacts
localStorage key: guardian-shield:phone-blacklist
BroadcastChannel: guardian-shield-communication
```

如果比赛现场是多台设备或不同浏览器环境，`BroadcastChannel/localStorage` 无法跨设备同步，需要追加轻后端通信事件 API：

```http
POST /api/v1/communication/events
GET  /api/v1/communication/events?phone=13800001001
PATCH /api/v1/communication/events/{id}
```

建议开发时把 Pinia store 的读写封装成 repository，先接 localStorage，后续替换成后端接口时页面不用大改。

## 4. 目标前端数据结构

建议新增文件：

```text
apps/web-antd/src/types/guardian-phone.ts
apps/web-antd/src/store/communication.ts
apps/web-antd/src/api/core/phone.ts
apps/web-antd/src/api/core/communication.ts
```

核心类型：

```ts
export type CommunicationScene = 'call' | 'sms';
export type PhoneTrustType = 'blacklisted' | 'self' | 'trusted' | 'unknown';
export type RiskLevel = 'high' | 'low' | 'medium';

export interface PhoneIdentity {
  displayName: string;
  phone: string;
  role: 'admin' | 'community' | 'elder' | 'family' | 'input';
  userId?: string;
}

export interface TrustedContact {
  id: string;
  elderPhone: string;
  contactName: string;
  contactPhone: string;
  contactRole?: 'community' | 'family' | 'friend' | 'spouse';
  relationshipType: string;
  isEmergencyContact: boolean;
  source: 'binding' | 'manual' | 'seed';
}

export interface BlockedNumber {
  id: string;
  elderPhone: string;
  phone: string;
  reason: string;
  source: 'auto-risk' | 'manual';
  riskEventId?: string;
  createdAt: string;
}

export interface CommunicationEvent {
  id: string;
  scene: CommunicationScene;
  sourcePhone: string;
  targetPhone: string;
  elderUserId: string;
  operatorUserId?: string;
  status:
    | 'delivered'
    | 'ended'
    | 'failed'
    | 'intercepted'
    | 'pending'
    | 'ringing';
  trustType: PhoneTrustType;
  contentText?: string;
  callSessionId?: string;
  durationSeconds?: number;
  risk?: RiskDecision;
  createdAt: string;
  updatedAt: string;
}

export interface RiskDecision {
  alertId?: string | null;
  autoBlocked: boolean;
  hitRuleCodes: string[];
  hitTerms: string[];
  reasonDetail: string;
  recordId: string;
  riskLevel: RiskLevel | string;
  riskScore: number;
  scene: string;
  suggestionAction: string;
  workorderId?: string | null;
}
```

## 5. 文件级改造计划

### 5.1 路由

修改：

```text
apps/web-antd/src/router/routes/modules/guardian.ts
```

新增：

```text
/input
  /input/phone
  /input/messages

/elder
  /elder/phone
  /elder/messages
  /elder/contacts
  /elder/bindings
```

调整：

- `/elder/help` 第一阶段从菜单隐藏，保留路由可暂不删除，避免已有链接 404。
- `/elder/family-binding` 可先重定向到 `/elder/bindings`，后续再移除旧入口。
- `/chat` 可继续保留，作为调试和家属联系能力，不作为主舞台入口。

### 5.2 认证和角色

后端修改：

```text
apps/backend-fastapi/app/constants/roles.py
apps/backend-fastapi/app/services/db_init.py
apps/backend-fastapi/app/schemas/auth.py
apps/backend-fastapi/app/services/auth.py
```

前端修改：

```text
apps/web-antd/src/api/core/auth.ts
apps/web-antd/src/api/core/user.ts
```

动作：

- 新增 `input` 角色。
- 新增 `input_demo / 111` 种子账号。
- `getUserInfoApi` 的 `homePathMap` 增加：

```ts
input: '/input/phone'
```

- 前端业务中不要再只依赖 `UserInfo.desc` 取手机号，建议新增 `useCurrentPhoneIdentity()` 或扩展本项目自己的用户类型。

### 5.3 API 封装

新增或扩展：

```text
apps/web-antd/src/api/core/phone.ts
apps/web-antd/src/api/core/communication.ts
apps/web-antd/src/api/core/risk.ts
apps/web-antd/src/api/core/index.ts
```

建议新增 API：

```ts
lookupPhoneApi(phone: string): Promise<PhoneDirectoryUser>
recognizeSmsApi(payload): Promise<RiskDecision>
recognizeCallTextApi(payload): Promise<RiskDecision>
```

`risk.ts` 当前只负责读取风险告警，后续要补写入侧识别 API。

### 5.4 通信 Store

新增：

```text
apps/web-antd/src/store/communication.ts
```

职责：

- 维护当前老人号码、安全联系人、黑名单。
- 根据 `sourcePhone + targetPhone` 创建短信和电话事件。
- 判断 `trusted / blacklisted / unknown`。
- 处理陌生短信首次识别。
- 处理通话结束识别。
- 收到高风险结果后自动写入黑名单。
- 通过 `BroadcastChannel` 通知其他角色页面刷新。
- 为老人端提供 `incomingCall`、`messageThreads`、`riskPopupQueue`。
- 为输入端提供 `deliveryStatus`、`recognitionStatus`。

### 5.5 Chat Store 扩展

修改：

```text
apps/web-antd/src/store/chat.ts
apps/web-antd/src/components/chat/chat-call-host.vue
```

动作：

- 增加场景通话元数据：

```ts
interface ScenarioCallMeta {
  operatorUserId: string;
  sourcePhone: string;
  targetPhone: string;
  targetUserId: string;
  scene: 'external_phone';
}
```

- `startCall` 支持可选 `meta`，并把 `sourcePhone/targetPhone` 放进 `call.offer` payload。
- 老人端来电弹窗优先显示 `sourcePhone`，而不是聊天对象名称。
- `uploadCallRecording` 传入 `callerNumber: sourcePhone`。
- 若通话短于 60 秒或录音失败，允许走 `recognizeCallTextApi` 的“通话摘要识别兜底”。
- 保留 `/chat/index` 原本调试能力，不把它改成剧情主入口。

## 6. 页面改造计划

### 6.1 老人端 `/elder/home`

目标：第一眼像手机系统，而不是后台 dashboard。

修改：

```text
apps/web-antd/src/views/guardian-shield/elder/home/index.vue
```

页面结构：

```text
手机外层容器
顶部状态栏：时间、网络、电量、本人号码
守护状态卡：今日是否安全、最近风险
App 图标区：电话、短信、联系人、风险提醒、绑定家人、设置
底部 Tab：首页 / 电话 / 短信 / 联系人
风险弹窗宿主：统一展示最新风险判定
```

注意：

- 去掉大段说明性文案。
- 字号和按钮保持适老，但不要做后台统计卡堆叠。
- 首页只展示老人最需要立刻理解的信息。

### 6.2 老人端 `/elder/phone`

新增：

```text
apps/web-antd/src/views/guardian-shield/elder/phone/index.vue
```

能力：

- 拨号盘。
- 最近通话。
- 来电全屏弹窗。
- 接听、拒接、通话中、计时、挂断。
- 黑名单号码来电直接显示“已拦截 / 强风险”。
- 陌生号码通话结束后进入风险识别。
- 风险结果弹窗。
- 高风险自动加入黑名单。

实现建议：

- WebRTC 连接复用 `useChatStore`。
- 剧情号码和识别流程由 `useCommunicationStore` 管。
- `call.offer` payload 里读取 `sourcePhone`。
- 通话短演示可在挂断后弹出“补录通话摘要”输入框，调用 `/risk-recognition/call`。

### 6.3 老人端 `/elder/messages`

新增：

```text
apps/web-antd/src/views/guardian-shield/elder/messages/index.vue
```

能力：

- 会话列表。
- 短信详情。
- 陌生号码首次短信自动识别。
- 安全联系人短信默认可信。
- 黑名单短信突出拦截。
- 识别中、低风险、中风险、高风险状态。
- 高风险自动加入黑名单。

短信识别流程：

```text
收到 SmsEvent
-> 判断 sourcePhone 是否安全联系人 / 黑名单
-> unknown 且首次出现，调用 recognizeSmsApi
-> 写入 RiskDecision
-> 高风险弹窗
-> 自动 addBlockedNumber
-> 刷新子女端和社区端数据
```

### 6.4 老人端 `/elder/contacts`

新增：

```text
apps/web-antd/src/views/guardian-shield/elder/contacts/index.vue
```

能力：

- 安全联系人列表。
- 家属绑定联系人自动进入安全联系人。
- 手动添加可信号码。
- 黑名单列表。
- 手动添加 / 移除黑名单。
- 展示自动拉黑来源事件。

第一阶段联系人数据来源：

```text
绑定关系接口 /bindings
本地手动联系人 localStorage
自动黑名单 localStorage
```

后续再落正式后端联系人表。

### 6.5 老人端 `/elder/bindings`

可由当前页面改名和重构：

```text
apps/web-antd/src/views/guardian-shield/elder/family-binding/index.vue
```

动作：

- 路由新建 `/elder/bindings`。
- UI 改成手机设置页风格。
- 展示子女姓名、子女电话、关系、是否紧急联系人。
- 新增绑定时优先支持输入子女电话号码查找。
- 原 `/elder/family-binding` 可重定向或隐藏。

### 6.6 输入端 `/input/phone`

新增：

```text
apps/web-antd/src/views/guardian-shield/input/phone/index.vue
```

能力：

- 选择测试场景号码：

```text
安全号码
陌生号码
已拉黑号码
诈骗号码
自定义号码
```

- 输入目标老人电话号码。
- 调用手机号查找接口定位 `elderUserId`。
- 发起 WebRTC 语音电话。
- 展示送达状态、接听状态、通话时长、识别状态、是否自动拉黑、是否通知家属和社区。

注意：

- 输入端不选择诈骗类型。
- 诈骗类型和风险等级由后端识别结果决定。
- 输入端登录账号是 `operator_user_id`，剧情展示号码是 `source_phone`。

### 6.7 输入端 `/input/messages`

新增：

```text
apps/web-antd/src/views/guardian-shield/input/messages/index.vue
```

能力：

- 与电话页共用 source phone 设置组件。
- 输入目标老人电话号码。
- 输入短信内容。
- 发送短信事件。
- 展示老人端是否收到、是否触发识别、风险等级、是否自动拉黑。

第一阶段推荐预置短信模板，但仍允许自由输入：

```text
退款 + 点击链接 + 验证码
冒充银行冻结
中奖领奖
普通安全短信
```

### 6.8 子女端 `/family/overview`

修改：

```text
apps/web-antd/src/views/guardian-shield/family/overview/index.vue
```

目标：

- 从“监护统计总览”改成“我的家人是否安全”。
- 展示绑定老人电话。
- 展示最近陌生来电、陌生短信、风险提醒。
- 增加“联系老人”“查看详情”“标记已处理”。

### 6.9 子女端 `/family/seniors` 和详情页

修改：

```text
apps/web-antd/src/views/guardian-shield/family/seniors/index.vue
```

新增：

```text
apps/web-antd/src/views/guardian-shield/family/seniors/detail.vue
```

新增路由：

```text
/family/seniors/:id
```

详情页内容：

- 老人基础信息和电话号码。
- 安全联系人状态。
- 最近通话事件。
- 最近短信事件。
- 风险记录。
- 模型证据。
- 联系老人。

### 6.10 子女端 `/family/alerts`

修改：

```text
apps/web-antd/src/views/guardian-shield/family/alerts/index.vue
```

增强：

- 展示 `sourcePhone`、`targetPhone`。
- 展示短信原文或通话摘要。
- 展示命中规则、证据片段、建议动作。
- 展示是否已自动加入老人黑名单。
- 操作增加：联系老人、发送提醒、标记已处理、查看社区工单状态。

### 6.11 社区端 `/community/dashboard`

修改：

```text
apps/web-antd/src/views/guardian-shield/community/dashboard/index.vue
```

增强：

- 汇总电话风险和短信风险。
- 突出高风险号码。
- 展示今日新增黑名单。
- 展示待处理工单。
- 支持按老人电话、来源号码快速筛选。

### 6.12 社区端 `/community/workorders`

修改：

```text
apps/web-antd/src/views/guardian-shield/community/workorders/index.vue
```

增强工单详情：

```text
来源号码 source_phone
老人号码 target_phone
老人姓名
子女号码
触发场景 call/sms
模型判定
证据片段
通知状态
黑名单动作
处置状态
```

操作：

- 联系老人。
- 联系子女。
- 标记处理中。
- 标记已完成。
- 补充处置备注。

## 7. 推荐开发阶段

### 阶段 0：权限、路由和基础类型

目标：让五个角色入口成立。

任务：

1. 新增 `input` 角色和 `input_demo` 账号。
2. 新增 `/input/phone`、`/input/messages` 路由。
3. 新增 `/elder/phone`、`/elder/messages`、`/elder/contacts`、`/elder/bindings` 路由。
4. 隐藏 `/elder/help` 菜单。
5. 新增 `guardian-phone.ts` 类型。
6. 新增 `phone.ts`、`communication.ts` API 空壳。
7. 新增 `communication` Pinia store 空壳。

验收：

- 五类账号登录后进入对应首页。
- 路由菜单与蓝图一致。
- 项目 typecheck 通过。

### 阶段 1：号码身份和通信事件层

目标：让 source_phone / target_phone 在前端流动起来。

任务：

1. 实现手机号查找。
2. 实现 `useCommunicationStore`。
3. 从 `/bindings` 派生老人安全联系人。
4. 实现本地黑名单。
5. 实现通信事件创建、更新、广播。
6. 封装 `recognizeSmsApi`、`recognizeCallTextApi`。
7. 统一 `handleRiskDecision`：

```text
写入事件 risk
弹风险提醒
高风险自动拉黑
刷新 alerts / notifications / workorders
```

验收：

- 输入一个老人手机号能解析到老人用户。
- 手动创建短信事件后，老人端 store 能收到。
- 高风险识别结果能写入黑名单。

### 阶段 2：老人端手机 OS

目标：老人端成为第一演示主屏。

任务：

1. 重做 `/elder/home`。
2. 新增 `/elder/phone`。
3. 新增 `/elder/messages`。
4. 新增 `/elder/contacts`。
5. 改造 `/elder/bindings`。
6. 风险弹窗做成全老人端通用组件。

验收：

- 老人端第一屏不像后台。
- 可接收陌生来电。
- 可接收陌生短信。
- 高风险提示语言直接清楚。
- 黑名单号码再次出现时能突出拦截。

### 阶段 3：输入端

目标：比赛成员能通过输入端发起电话和短信剧情。

任务：

1. 新增 source phone 选择组件。
2. 完成 `/input/phone`。
3. 完成 `/input/messages`。
4. 电话页接入 WebRTC 通话。
5. 短信页接入 `CommunicationEvent`。
6. 输入端展示事件状态和识别结果。

验收：

- 输入端能选择或填写发起号码。
- 输入端能输入老人号码并发起电话。
- 输入端能输入老人号码并发送短信。
- 输入端能看到是否触发识别和拉黑。

### 阶段 4：风险闭环

目标：电话和短信都能走完整识别链路。

任务：

1. 短信陌生号码首次识别。
2. 通话结束后音频识别。
3. 通话短演示文本摘要兜底识别。
4. 风险结果统一写回事件。
5. 自动黑名单。
6. 老人端弹窗。
7. 子女端通知刷新。
8. 社区端工单刷新。

验收：

- 诈骗短信触发高风险、通知、工单和黑名单。
- 诈骗电话触发高风险、通知、工单和黑名单。
- 安全联系人默认不进入诈骗推理主链路。
- 陌生号码不是立即拉黑，必须有识别结果。

### 阶段 5：子女端和社区端补链路

目标：风险事件能被家人和社区解释、追踪和处置。

任务：

1. 改造 `/family/overview`。
2. 改造 `/family/seniors`。
3. 新增 `/family/seniors/:id`。
4. 改造 `/family/alerts`。
5. 改造 `/community/dashboard`。
6. 改造 `/community/workorders`。

验收：

- 子女端能看到老人电话、通信事件、风险判断。
- 社区端能看到完整事件链路。
- 工单详情能解释来源号码、老人号码、子女联系方式和处置状态。

### 阶段 6：演示稳定性和数据重置

目标：比赛现场不翻车。

任务：

1. 增加演示数据重置按钮或脚本。
2. 增加号码库预设。
3. 增加通话失败、权限拒绝、后端识别失败的兜底提示。
4. 增加演示脚本数据。
5. 做移动端和桌面端响应式检查。

验收：

- 一键恢复演示初始状态。
- 麦克风权限失败时仍可走文本摘要识别。
- 刷新页面后核心事件不丢失。

## 8. 第一阶段文件清单

优先新增：

```text
apps/web-antd/src/types/guardian-phone.ts
apps/web-antd/src/store/communication.ts
apps/web-antd/src/api/core/phone.ts
apps/web-antd/src/api/core/communication.ts
apps/web-antd/src/views/guardian-shield/input/phone/index.vue
apps/web-antd/src/views/guardian-shield/input/messages/index.vue
apps/web-antd/src/views/guardian-shield/elder/phone/index.vue
apps/web-antd/src/views/guardian-shield/elder/messages/index.vue
apps/web-antd/src/views/guardian-shield/elder/contacts/index.vue
```

优先修改：

```text
apps/web-antd/src/router/routes/modules/guardian.ts
apps/web-antd/src/api/core/index.ts
apps/web-antd/src/api/core/risk.ts
apps/web-antd/src/api/core/user.ts
apps/web-antd/src/store/index.ts
apps/web-antd/src/store/chat.ts
apps/web-antd/src/components/chat/chat-call-host.vue
apps/web-antd/src/views/guardian-shield/elder/home/index.vue
apps/web-antd/src/views/guardian-shield/elder/family-binding/index.vue
apps/web-antd/src/views/guardian-shield/family/overview/index.vue
apps/web-antd/src/views/guardian-shield/family/seniors/index.vue
apps/web-antd/src/views/guardian-shield/family/alerts/index.vue
apps/web-antd/src/views/guardian-shield/community/dashboard/index.vue
apps/web-antd/src/views/guardian-shield/community/workorders/index.vue
```

轻后端建议修改：

```text
apps/backend-fastapi/app/constants/roles.py
apps/backend-fastapi/app/services/db_init.py
apps/backend-fastapi/app/schemas/auth.py
apps/backend-fastapi/app/api/v1/endpoints/risk_recognition.py
apps/backend-fastapi/app/api/v1/endpoints/phone_directory.py
apps/backend-fastapi/app/services/phone_directory.py
apps/backend-fastapi/app/api/router.py
```

## 9. 测试和验收方案

### 9.1 自动检查

前端：

```bash
pnpm --filter @vben/web-antd typecheck
pnpm --filter @vben/web-antd build
```

后端：

```bash
cd apps/backend-fastapi
.venv/bin/pytest
```

### 9.2 手工演示脚本

账号：

```text
elder_demo / 111       老人端
input_demo / 111       输入端
family_demo / 111      子女端
community_demo / 111   社区端
admin_demo / 111       管理端
```

短信高风险脚本：

```text
输入端 source_phone = 17099990001
target_phone = 13800001001
短信内容 = 您的退款已到账，请立即点击链接并提供验证码完成补偿

预期：
老人端收到陌生短信
老人端弹出高风险提醒
17099990001 自动进入黑名单
子女端出现风险通知
社区端出现高风险工单
```

电话高风险脚本：

```text
输入端 source_phone = 01012345678
target_phone = 13800001001
通话话术 = 这里是警方专线，请配合调查，把资金转到指定账户，不要告诉家人

预期：
老人端收到陌生来电
老人接听并通话
挂断后触发识别
老人端弹出高风险提醒
01012345678 自动进入黑名单
子女端和社区端同步出现事件
```

安全联系人脚本：

```text
source_phone = 13900002001
target_phone = 13800001001

预期：
老人端识别为安全联系人
不进入诈骗推理主链路
不自动拉黑
```

黑名单脚本：

```text
source_phone = 已被自动拉黑的号码
target_phone = 13800001001

预期：
老人端电话或短信直接展示强风险 / 已拦截
不需要再次等待模型结果
```

## 10. 关键风险和建议决策

### 10.1 输入端角色必须补

当前后端只有 `elder/family/community/admin`。如果不补 `input`，输入端只能借用 admin 或 community 权限，会让演示身份不清晰。建议第一步就补 `input`。

### 10.2 多设备演示需要后端通信事件

如果比赛现场每个成员使用不同电脑或不同浏览器，纯前端 `localStorage/BroadcastChannel` 不够。建议在确认演示方式后尽快决定：

```text
同一浏览器多标签页：前端本地事件层可行
多电脑 / 多浏览器：必须补 communication events 轻后端
```

推荐按多设备方案设计 store 接口，哪怕第一版先用 localStorage。

### 10.3 通话识别不能只依赖录音

当前后端短通话小于 60 秒会跳过音频模型。比赛演示通常很短，所以必须保留 `/risk-recognition/call` 文本摘要兜底入口。

### 10.4 黑名单先做号码级，不复用聊天黑名单

聊天黑名单是用户对用户，不适合诈骗号码。第一阶段先在前端维护号码黑名单，后续再补后端表：

```text
elder_phone
blocked_phone
reason
source
risk_event_id
created_at
```

### 10.5 老人端视觉要尽早重做

老人端是本轮改造的第一视觉记忆点。建议先做 `/elder/home + /elder/phone + /elder/messages`，不要先深挖管理端页面。

## 11. 建议的第一周开发顺序

```text
Day 1:
  input 角色、路由、基础类型、phone lookup、risk API 封装

Day 2:
  communication store、安全联系人、黑名单、短信事件流

Day 3:
  老人端 home/messages/contacts 第一版

Day 4:
  输入端 messages、短信识别、风险弹窗、自动拉黑

Day 5:
  输入端 phone、ChatStore 通话元数据、老人端 phone

Day 6:
  子女端 overview/seniors/alerts 补通信链路

Day 7:
  社区 dashboard/workorders 补链路，演示脚本和重置能力
```

## 12. 最小可演示闭环定义

第一阶段可以认为完成的标准：

- `input_demo` 可以登录输入端。
- 输入端可填写 `source_phone` 和 `target_phone`。
- 老人端首页像手机系统。
- 老人端能收到输入端短信。
- 老人端能收到输入端电话。
- 陌生短信能调用后端 SMS 识别。
- 陌生电话能在结束后调用后端 call 或 call-audio 识别。
- 高风险号码能自动进入老人号码黑名单。
- 老人端能看到风险弹窗。
- 子女端能看到绑定老人风险事件。
- 社区端能看到高风险工单。

达到以上标准后，再继续打磨样式、统计图、正式后端模型和演示重置。
