import { requestClient } from '#/api/request';

import type { AdminUserListItem, AdminUserListParams } from './types';

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
        riskScore: item.roles.includes('elder')
          ? 90
          : item.roles.includes('family')
            ? 60
            : 20,
        role: item.roles[0] || 'elder',
        roles: item.roles,
        status: item.status === 'active' ? 'enabled' : 'disabled',
        username: item.username,
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
    riskScore:
      item.latest_risk_level === 'high'
        ? 90
        : item.latest_risk_level === 'medium'
          ? 60
          : 20,
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
