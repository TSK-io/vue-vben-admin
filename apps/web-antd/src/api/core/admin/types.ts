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
  versionHistory: Array<{
    operator: string;
    status: string;
    updatedAt: string;
    version: number;
  }>;
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
  effectiveValue?: string | null;
  lastUpdatedAt?: string | null;
  lastUpdatedBy?: string | null;
  auditCount?: number;
}

export interface AdminRoleItem {
  code: 'admin' | 'community' | 'elder' | 'family';
  name: string;
  description: string;
  permissions: string[];
  menus: string[];
  buttonPermissions: string[];
  apiPermissions: string[];
  dataScope: string;
  userCount?: number | null;
  isSystem: boolean;
}

export interface AdminRiskAlertItem {
  id: string;
  elderUserId: string;
  elderName: string;
  title: string;
  riskLevel: string;
  sourceType: string;
  status: string;
  occurredAt: string;
  relatedNotifications: number;
  relatedWorkorders: number;
}

export interface AdminRiskAlertDetail extends AdminRiskAlertItem {
  reasonDetail: string;
  suggestionAction: string;
  relatedNotificationIds: string[];
  relatedWorkorderIds: string[];
}

export interface RiskLexiconItem {
  id: string;
  term: string;
  category: string;
  scene: string;
  riskLevel: string;
  status: string;
  source?: string | null;
  notes?: string | null;
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

export interface AdminRolePayload {
  code: AdminRoleItem['code'];
  name: string;
  description?: string;
  permissions: string[];
  menus: string[];
  buttonPermissions: string[];
  apiPermissions: string[];
  dataScope: string;
}

export interface RiskLexiconPayload {
  term: string;
  category: string;
  scene: string;
  riskLevel: string;
  status: string;
  source?: string;
  notes?: string;
}
