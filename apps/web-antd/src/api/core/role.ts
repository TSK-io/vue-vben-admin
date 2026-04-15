import {
  createAdminRoleApi,
  getAdminRoleListApi,
  updateAdminRoleApi,
} from './admin';

export interface RolePermissionOverviewItem {
  codeCount: number;
  description: string;
  menuCount: number;
  menus: string[];
  name: string;
  resources: string[];
  buttonPermissions: string[];
  apiPermissions: string[];
  dataScope: string;
  role: 'admin' | 'community' | 'elder' | 'family';
  scope: string;
  isSystem: boolean;
}

export async function getRolePermissionOverviewApi() {
  const rows = await getAdminRoleListApi();
  return rows.map(
    (item): RolePermissionOverviewItem => ({
      apiPermissions: item.apiPermissions,
      buttonPermissions: item.buttonPermissions,
      codeCount: item.permissions.length,
      dataScope: item.dataScope,
      description: item.description,
      isSystem: item.isSystem,
      menuCount: item.menus.length,
      menus: item.menus,
      name: item.name,
      resources: item.permissions,
      role: item.code,
      scope: `${item.name}可见范围`,
    }),
  );
}

export { createAdminRoleApi, updateAdminRoleApi };
