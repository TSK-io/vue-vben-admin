import { requestClient } from '#/api/request';

export interface RolePermissionOverviewItem {
  codeCount: number;
  description: string;
  menuCount: number;
  menus: string[];
  name: string;
  resources: string[];
  role: 'admin' | 'ops' | 'reviewer' | 'support';
  scope: string;
}

const roleMenuMap: Record<string, string[]> = {
  admin: ['用户管理', '角色权限', '风险规则', '内容管理', '系统配置'],
  ops: ['用户管理', '内容管理'],
  reviewer: ['风险规则'],
  support: ['用户管理'],
};

export async function getRolePermissionOverviewApi() {
  const rows = await requestClient.get<any[]>('/admin/roles');
  return rows.map(
    (item): RolePermissionOverviewItem => ({
      codeCount: item.permissions.length,
      description: item.description,
      menuCount: (roleMenuMap[item.code] || []).length,
      menus: roleMenuMap[item.code] || [],
      name: item.name,
      resources: item.permissions,
      role: item.code,
      scope: `${item.name}可见范围`,
    }),
  );
}
