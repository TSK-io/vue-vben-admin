# 个人项目精简 TODO

基于当前仓库结构扫描后的判断，这个项目更像“可发布的后台模板 + 多端演示仓库”，而不是单一业务型个人项目。
如果目标是降低维护成本、减少学习/构建负担、尽快迭代业务功能，可以优先做下面这些减法。

## 一、优先考虑移除的功能/模块

### 1. 多套前端 UI 实现

当前同时存在：

- `apps/web-antd`
- `apps/web-antdv-next`
- `apps/web-ele`
- `apps/web-naive`
- `apps/web-tdesign`

个人项目建议：

- 只保留 1 套前端实现，优先保留你当前最熟悉、已经在改的那一套
- 如果没有特殊原因，建议保留 `apps/web-antd`

原因：

- 5 套 UI 壳子会显著增加依赖、脚本、升级和排查成本
- 同一业务要兼容多套组件库，对个人开发几乎没有收益
- `packages/styles`、`packages/effects` 中很多适配层也会因此变复杂

### 2. Mock 后端

当前存在：

- `apps/backend-mock`

个人项目建议：

- 如果你已经接入 `apps/backend-fastapi`，可以移除 mock 服务

原因：

- 前后端双套接口源会让联调逻辑更分裂
- Nitro + mock 数据更适合模板演示，不适合长期业务维护

### 3. 文档站与 Playground

当前存在：

- `docs`
- `playground`

个人项目建议：

- 如果不是要做开源模板/组件库，直接移除

原因：

- 这两部分更偏展示、验证、对外说明
- 对个人业务开发的直接价值较低，但会增加构建和依赖体积

### 4. 国际化

当前相关：

- `packages/locales`
- `apps/web-antd/src/locales`

个人项目建议：

- 如果近期只服务中文用户，先移除 i18n，只保留中文文案

原因：

- 文案维护成本高
- 页面改动时要同步 key、翻译文件和类型，个人项目通常不划算

### 5. 动态权限 / 多角色复杂路由

当前相关：

- `packages/effects/access`
- `apps/web-antd/src/router/access.ts`
- `apps/web-antd/src/router/guard.ts`
- `apps/web-antd/src/store/auth.ts`

个人项目建议：

- 前期简化为“是否登录 + 是否管理员”两级
- 暂时不要保留复杂的菜单权限、按钮权限、动态路由生成

原因：

- 企业后台常见，但个人项目前期很容易过度设计
- 会牵动菜单、路由、接口、状态管理、测试一起复杂化

### 6. 主题切换 / 偏好设置体系

当前相关：

- `packages/preferences`
- `packages/@core/preferences`
- `apps/web-antd/src/preferences.ts`

个人项目建议：

- 只保留浅色主题和少量基础布局配置
- 暂时移除多主题、复杂偏好持久化、界面级定制

原因：

- 功能看起来高级，但真实业务收益很有限
- 会增加状态管理、样式和兼容成本

### 7. 表格增强、富文本、图表等“演示型能力”

从依赖和结构看，仓库中集成了很多常见后台增强能力，例如：

- `vxe-table`
- `echarts`
- `qrcode`
- `@tiptap/*`
- 拖拽、气泡、动效等扩展

个人项目建议：

- 只在真正需要时再按需引入
- 不要把这些作为默认基础设施长期保留

原因：

- 这类能力很适合模板展示，但会抬高基础复杂度
- 对早期 MVP 来说，简单表单 + 普通表格通常就够了

### 8. 发行型工程化能力

当前相关：

- `.changeset`
- 多语言 README
- 大量 `build:*` 脚本
- monorepo 发布/校验脚本

个人项目建议：

- 如果不是要维护 npm 包和模板生态，可以大幅收缩

原因：

- 这些配置更适合“框架/模板维护者”
- 对单项目开发者的收益，通常低于维护成本

## 二、优先考虑简化的技术栈

### 推荐精简为

- 前端：Vue 3 + Vite + TypeScript + 1 套 UI 组件库
- 状态：Pinia
- 路由：Vue Router
- 后端：FastAPI + SQLAlchemy + Alembic + PostgreSQL

### 可考虑逐步移除/弱化

- `turbo`：如果最终只剩前端 + 后端两个主应用，甚至可以不再坚持复杂 monorepo 编排
- 多组件库并存：Ant Design Vue / Element Plus / Naive UI / TDesign 同时保留没有必要
- `backend-mock` 使用的 Nitro 体系：如果真实后端已确定，建议直接退场
- `vue-i18n`：单语言项目可先移除
- `pinia-plugin-persistedstate` + `secure-ls`：如果只是存 token 和少量用户信息，可以先用更轻的方案
- 大量 workspace 包拆分：如果团队规模很小，包拆得过细会增加理解成本

## 三、建议保留的部分

这些对个人项目仍然有明显价值：

- `apps/web-antd`：作为唯一前端入口
- `apps/backend-fastapi`：作为真实业务后端
- `TypeScript`
- `Pinia`
- `Vue Router`
- `FastAPI` / `SQLAlchemy` / `Alembic`
- 基础登录鉴权
- 基础布局、表单、表格、请求封装

## 四、执行 TODO

### P0：先把仓库收窄成“一个前端 + 一个后端”

- [x] 确认主前端，仅保留 `apps/web-antd`
- [x] 删除 `apps/web-antdv-next`
- [x] 删除 `apps/web-ele`
- [x] 删除 `apps/web-naive`
- [x] 删除 `apps/web-tdesign`
- [x] 更新根目录 `package.json` 脚本，只保留主前端相关命令
- [x] 更新 `pnpm-workspace.yaml`，移除不再使用的 app

### P1：移除模板演示性质较强的配套

- [x] 删除 `apps/backend-mock`
- [x] 删除 `docs`
- [x] 删除 `playground`
- [x] 清理 README 中对应的说明和命令
- [x] 清理根脚本里 `build:docs`、`build:ele`、`build:naive`、`build:tdesign`、`dev:*` 等无用脚本

### P2：简化前端复杂能力

- [ ] 评估并移除国际化，仅保留中文文案
- [ ] 简化权限系统为“登录态 + 管理员标记”
- [ ] 简化路由守卫，去掉复杂动态菜单/动态路由装配
- [ ] 简化偏好设置，仅保留必要布局项
- [ ] 梳理演示页面，删除 `views/demos`

### P3：减少过度抽象

- [ ] 检查 `packages/*` 是否有仅被单一前端使用的包
- [ ] 对只服务当前项目的 workspace 包，逐步回收进主应用目录
- [ ] 减少跨包跳转和过深封装，优先让业务代码“就近可读”

### P4：精简依赖与脚本

- [ ] 清理多 UI 库相关依赖
- [ ] 清理 mock、docs、playground 相关依赖
- [ ] 清理不再使用的样式导出和适配层
- [ ] 重新安装依赖并检查 lockfile 变化
- [ ] 跑一遍主前端和后端的启动/构建/类型检查

## 五、适合个人项目的最终形态

建议最终收敛到：

- 一个主前端：`apps/web-antd`
- 一个主后端：`apps/backend-fastapi`
- 一个数据库迁移体系：Alembic
- 一套固定 UI
- 一套简单权限模型
- 单语言
- 少量必要的公共封装

这样会更适合个人项目持续开发，也更容易定位问题、控制心智负担和部署成本。
