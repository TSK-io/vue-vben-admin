# 测试与验收清单

本文档对应 `TODO.md` 中“4. 测试与验收”。

## 自动化测试

后端：

- `cd apps/backend-fastapi && .venv/bin/pytest`

前端：

- `pnpm test:unit -- apps/web-antd/src/router/routes/modules/guardian.test.ts apps/web-antd/src/api/core/auth.test.ts`

## 多角色联调脚本

在仓库根目录执行：

```bash
bash scripts/acceptance/guardian-shield-multirole.sh
```

脚本会串联验证：

- 健康检查与运行态指标
- 老年端登录、隐私导出、求助与适老设置
- 子女端通知、监护提醒与隐私申请
- 社区端重点老人、工单流转
- 管理端规则与系统配置读取

## 需求验收用例

1. 老年用户登录后可查看风险提醒、发起求助、保存适老设置、提交隐私授权与导出个人数据。
2. 子女用户登录后可读取通知记录、发送远程提醒、提交个人数据更正/删除申请。
3. 社区用户登录后可查看重点老人列表并完成工单流转。
4. 管理员登录后可读取用户、规则、内容、系统配置等管理数据。
5. 风险识别接口命中高危规则后，会自动生成告警、通知和工单闭环。
6. 运行态接口能够返回排队策略与性能统计，响应头包含 `X-Request-Id`、`X-Process-Time`、`X-Queue-Wait-Time`。
7. 合规模块能够记录授权、隐私申请和请求审计日志。
