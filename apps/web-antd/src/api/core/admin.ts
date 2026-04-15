import { requestClient } from '#/api/request';

export interface AdminUserListParams {
  keyword?: string;
  page?: number;
  pageSize?: number;
  role?: string;
  status?: string;
}

export interface AdminUserListItem {
  age: number | null;
  createdAt: string;
  id: string;
  bindCount: number;
  communityName: string;
  lastAlertAt: string;
  name: string;
  phone: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskScore: number;
  role: 'admin' | 'community' | 'elder' | 'family';
  status: 'disabled' | 'enabled';
  username: string;
  notes?: Record<string, string>;
  roles?: string[];
  latestAlertTitle?: string | null;
  bindingIds?: string[];
  roleDescriptions?: string[];
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
  version: number;
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
  auditStatus: string;
  assetUrl?: string | null;
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
  auditStatus: string;
  assetUrl?: string;
}

function mapRiskLevelFromRoles(roles: string[]): 'high' | 'low' | 'medium' {
  if (roles.includes('elder')) return 'high';
  if (roles.includes('family')) return 'medium';
  return 'low';
}

export async function getAdminUserListApi(params: AdminUserListParams) {
  const rows = await requestClient.get<any[]>('/admin/users', {
    params: {
      keyword: params.keyword,
      role: params.role,
      status: params.status,
    },
  });
  return {
    items: rows.map(
      (item): AdminUserListItem => ({
        age: null,
        bindCount: item.roles.includes('elder') ? 1 : 0,
        communityName: item.roles.includes('community') ? '东湖社区' : '-',
        createdAt: '-',
        id: item.user_id,
        lastAlertAt: item.last_login_at || '-',
        latestAlertTitle: item.latest_alert_title,
        name: item.display_name,
        notes: item.notes,
        phone: item.phone,
        riskLevel: mapRiskLevelFromRoles(item.roles),
        riskScore:
          item.roles.includes('elder')
            ? 90
            : item.roles.includes('family')
              ? 60
              : 20,
        role: item.roles[0] || 'elder',
        status: item.status === 'active' ? 'enabled' : 'disabled',
        username: item.username,
        roles: item.roles,
      }),
    ),
    total: rows.length,
  };
}

export async function getAdminUserDetailApi(userId: string) {
  const item = await requestClient.get<any>(`/admin/users/${userId}`);
  return {
    age: null,
    bindCount: item.bind_count,
    bindingIds: item.binding_ids,
    communityName: item.roles.includes('community') ? '东湖社区' : '-',
    createdAt: '-',
    id: item.user_id,
    lastAlertAt: item.latest_alert_at || '-',
    latestAlertTitle: item.latest_alert_title,
    name: item.display_name,
    notes: item.notes,
    phone: item.phone,
    riskLevel: item.latest_risk_level,
    riskScore: item.latest_risk_level === 'high' ? 90 : item.latest_risk_level === 'medium' ? 60 : 20,
    role: item.roles[0] || 'elder',
    roleDescriptions: item.role_descriptions,
    roles: item.roles,
    status: item.status === 'active' ? 'enabled' : 'disabled',
    username: item.username,
  } satisfies AdminUserListItem;
}

export async function createAdminUserApi(payload: {
  username: string;
  displayName: string;
  phone: string;
  roles: string[];
  status: string;
  password?: string;
  notes?: Record<string, string>;
}) {
  return requestClient.post('/admin/users', {
    display_name: payload.displayName,
    notes: payload.notes,
    password: payload.password,
    phone: payload.phone,
    roles: payload.roles,
    status: payload.status === 'enabled' ? 'active' : 'inactive',
    username: payload.username,
  });
}

export async function updateAdminUserApi(
  userId: string,
  payload: {
    username: string;
    displayName: string;
    phone: string;
    roles: string[];
    status: string;
    password?: string;
    notes?: Record<string, string>;
  },
) {
  return requestClient.put(`/admin/users/${userId}`, {
    display_name: payload.displayName,
    notes: payload.notes,
    password: payload.password,
    phone: payload.phone,
    roles: payload.roles,
    status: payload.status === 'enabled' ? 'active' : 'inactive',
    username: payload.username,
  });
}

export async function resetAdminUserPasswordApi(
  userId: string,
  password: string,
) {
  return requestClient.post(`/admin/users/${userId}/reset-password`, { password });
}

export async function updateAdminUserPhoneApi(userId: string, phone: string) {
  return requestClient.put(`/admin/users/${userId}/phone`, { phone });
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
      version: item.version ?? 1,
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
      auditStatus: item.audit_status,
      assetUrl: item.asset_url,
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
    audit_status: payload.auditStatus,
    asset_url: payload.assetUrl,
    status: payload.status,
    summary: payload.summary,
    title: payload.title,
  });
}

export async function updateAdminContentApi(
  contentId: string,
  payload: ContentPayload,
) {
  return requestClient.put(`/admin/contents/${contentId}`, {
    audience: payload.audience,
    category: payload.category,
    channel: payload.channel,
    code: payload.code,
    content_body: payload.contentBody,
    content_type: payload.contentType,
    audit_status: payload.auditStatus,
    asset_url: payload.assetUrl,
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
