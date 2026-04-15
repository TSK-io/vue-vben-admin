import { requestClient } from '#/api/request';

import type { AdminRoleItem, AdminRolePayload } from './types';

export async function getAdminRoleListApi() {
  const rows = await requestClient.get<any[]>('/admin/roles');
  return rows.map(
    (item): AdminRoleItem => ({
      apiPermissions: item.api_permissions || [],
      buttonPermissions: item.button_permissions || [],
      code: item.code,
      dataScope: item.data_scope || 'self',
      description: item.description,
      isSystem: item.is_system,
      menus: item.menus || [],
      name: item.name,
      permissions: item.permissions || [],
      userCount: item.user_count,
    }),
  );
}

export async function createAdminRoleApi(payload: AdminRolePayload) {
  return requestClient.post('/admin/roles', {
    api_permissions: payload.apiPermissions,
    button_permissions: payload.buttonPermissions,
    code: payload.code,
    data_scope: payload.dataScope,
    description: payload.description,
    menus: payload.menus,
    name: payload.name,
    permissions: payload.permissions,
  });
}

export async function updateAdminRoleApi(
  roleCode: string,
  payload: AdminRolePayload,
) {
  return requestClient.put(`/admin/roles/${roleCode}`, {
    api_permissions: payload.apiPermissions,
    button_permissions: payload.buttonPermissions,
    code: payload.code,
    data_scope: payload.dataScope,
    description: payload.description,
    menus: payload.menus,
    name: payload.name,
    permissions: payload.permissions,
  });
}
