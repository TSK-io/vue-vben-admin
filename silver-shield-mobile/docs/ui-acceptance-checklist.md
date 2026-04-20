# Silver Shield Mobile UI 验收清单

## 页面骨架

- 页面根节点使用 `ss-page`，并按场景补充 `ss-page--with-nav`、`ss-page--with-bottom-bar`、`ss-page--with-tabbar`
- 顶部导航统一使用 `AppNavBar`，不要在页面内手写状态栏高度和返回按钮
- 需要固定底部操作时统一使用 `AppBottomActionBar`，不能直接 `position: fixed` 贴底
- 卡片容器优先使用 `AppCard`，分区标题优先使用 `AppSection`

## 视觉一致性

- 颜色、圆角、阴影、字号全部来自 `src/uni.scss` token，不在页面里写新的视觉体系
- 列表项优先使用 `AppListCell` 或 `ss-list-group + ss-list-cell` 组合，避免同类列表出现不同间距和头像样式
- 页面内最多保留 1 个主强调色，风险态统一走 `danger / warn / success` 语义色
- 空态、加载态、弱网态统一使用 `ss-feedback-state`

## 适老化与可用性

- 主按钮和关键点击区高度不低于 `--ss-touch-height`
- 标题、正文、说明文案分别落在既定字号层级内，不单独发明字号
- 有高风险、黑名单、未读等状态时，必须用明确标签或数字反馈，不靠颜色单独表达
- 字体放大和高对比模式打开后，页面不能出现内容遮挡、按钮挤压或文案重叠

## 兼容与交互

- H5 与微信小程序都要检查顶部安全区、底部手势区和滚动末端留白
- 聊天页、列表页、设置页等核心页面要确认底部操作区不会遮住最后一条内容
- 反馈动画只使用项目内已有的 `ss-fade-up / ss-fade-in / ss-pop-in`，避免每页自定义一套
- 新页面提测前至少覆盖正常态、空态、失败态、弱网态四种展示
