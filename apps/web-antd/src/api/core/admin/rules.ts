import { requestClient } from '#/api/request';

import type { AdminRuleItem, RiskRulePayload } from './types';

export async function getAdminRuleListApi() {
  const rows = await requestClient.get<any[]>('/admin/rules');
  return rows.map(
    (item): AdminRuleItem => ({
      code: item.code,
      id: item.id,
      name: item.name,
      priority: item.priority,
      reasonTemplate: item.reason_template,
      riskLevel: item.risk_level,
      scene: item.scene,
      status: item.status,
      suggestionTemplate: item.suggestion_template,
      triggerExpression: item.trigger_expression,
      version: item.version ?? 1,
      versionHistory: (item.version_history || []).map((entry: any) => ({
        operator: entry.operator,
        status: entry.status,
        updatedAt: entry.updated_at,
        version: entry.version,
      })),
    }),
  );
}

export async function createAdminRuleApi(payload: RiskRulePayload) {
  return requestClient.post('/admin/rules', {
    code: payload.code,
    name: payload.name,
    priority: payload.priority,
    reason_template: payload.reasonTemplate,
    risk_level: payload.riskLevel,
    scene: payload.scene,
    status: payload.status,
    suggestion_template: payload.suggestionTemplate,
    trigger_expression: payload.triggerExpression,
  });
}

export async function updateAdminRuleApi(
  ruleId: string,
  payload: RiskRulePayload,
) {
  return requestClient.put(`/admin/rules/${ruleId}`, {
    code: payload.code,
    name: payload.name,
    priority: payload.priority,
    reason_template: payload.reasonTemplate,
    risk_level: payload.riskLevel,
    scene: payload.scene,
    status: payload.status,
    suggestion_template: payload.suggestionTemplate,
    trigger_expression: payload.triggerExpression,
  });
}
