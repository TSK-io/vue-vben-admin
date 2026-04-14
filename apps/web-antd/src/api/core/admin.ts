import { requestClient } from '#/api/request';

export interface AdminUserListParams {
  keyword?: string;
  role?: string;
}

export interface AdminUserListItem {
  id: string;
  name: string;
  username: string;
  phone: string;
  role: 'admin' | 'community' | 'elder' | 'family';
  riskLevel: 'high' | 'low' | 'medium';
  bindCount: number;
  communityName: string;
  lastAlertAt: string;
  status: 'disabled' | 'enabled';
}

export interface AdminRuleItem {
  id: string;
  code: string;
  name: string;
  scene: string;
  riskLevel: 'high' | 'low' | 'medium';
  priority: number;
  status: string;
  triggerExpression: string;
  reasonTemplate: string;
  suggestionTemplate: string;
}

export interface AdminContentItem {
  id: string;
  contentType: string;
  code?: string | null;
  title: string;
  category: string;
  audience?: string | null;
  channel?: string | null;
  status: string;
  summary?: string | null;
  updatedAt: string;
}

export interface AdminSystemConfigItem {
  key: string;
  name: string;
  value: string;
  group: string;
  description: string;
}

export interface RiskRulePayload {
  code: string;
  name: string;
  scene: string;
  riskLevel: string;
  priority: number;
  status: string;
  triggerExpression: string;
  reasonTemplate: string;
  suggestionTemplate: string;
}

export interface ContentPayload {
  contentType: string;
  code?: string;
  title: string;
  category: string;
  audience?: string;
  channel?: string;
  status: string;
  summary?: string;
  contentBody: string;
}

function mapRiskLevelFromRoles(roles: string[]): 'high' | 'low' | 'medium' {
  if (roles.includes('elder')) return 'high';
  if (roles.includes('family')) return 'medium';
  return 'low';
}

export async function getAdminUserListApi(params: AdminUserListParams) {
  const rows = await requestClient.get<any[]>('/admin/users', { params });
  return {
    items: rows.map((item) => ({
      bindCount: item.roles.includes('elder') ? 1 : 0,
      communityName: item.roles.includes('community') ? '东湖社区' : '-',
      id: item.user_id,
      lastAlertAt: item.last_login_at || '-',
      name: item.display_name,
      phone: item.phone,
      riskLevel: mapRiskLevelFromRoles(item.roles),
      role: item.roles[0] || 'elder',
      status: item.status === 'active' ? 'enabled' : 'disabled',
      username: item.username,
    })),
    total: rows.length,
  };
}

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

export async function updateAdminRuleApi(ruleId: string, payload: RiskRulePayload) {
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

export async function getAdminContentListApi() {
  const rows = await requestClient.get<any[]>('/admin/contents');
  return rows.map(
    (item): AdminContentItem => ({
      audience: item.audience,
      category: item.category,
      channel: item.channel,
      code: item.code,
      contentType: item.content_type,
      id: item.id,
      status: item.status,
      summary: item.summary,
      title: item.title,
      updatedAt: item.updated_at,
    }),
  );
}

export async function createAdminContentApi(payload: ContentPayload) {
  return requestClient.post('/admin/contents', {
    audience: payload.audience,
    category: payload.category,
    channel: payload.channel,
    code: payload.code,
    content_body: payload.contentBody,
    content_type: payload.contentType,
    status: payload.status,
    summary: payload.summary,
    title: payload.title,
  });
}

export async function updateAdminContentApi(contentId: string, payload: ContentPayload) {
  return requestClient.put(`/admin/contents/${contentId}`, {
    audience: payload.audience,
    category: payload.category,
    channel: payload.channel,
    code: payload.code,
    content_body: payload.contentBody,
    content_type: payload.contentType,
    status: payload.status,
    summary: payload.summary,
    title: payload.title,
  });
}

export async function getAdminSystemConfigListApi() {
  return requestClient.get<AdminSystemConfigItem[]>('/admin/system-config');
}

export async function updateAdminSystemConfigApi(key: string, value: string) {
  return requestClient.put(`/admin/system-config/${key}`, { value });
}
