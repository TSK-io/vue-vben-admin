import { requestClient } from '#/api/request';

export interface RolePermissionOverviewItem {
  codeCount: number;
  description: string;
  menuCount: number;
  menus: string[];
  name: string;
  resources: string[];
  role: 'admin' | 'community' | 'elder' | 'family' | 'input';
  scope: string;
}

const roleMenuMap: Record<string, string[]> = {
  admin: ['用户管理', '角色权限', '风险规则', '内容管理', '系统配置'],
  community: ['辖区总览', '重点老人', '风险工单', '宣教管理', '统计报表'],
  elder: ['首页', '风险提醒', '一键求助', '亲属绑定', '防骗知识', '适老设置'],
  family: ['监护总览', '老人列表', '风险详情', '通知记录', '监护设置'],
  input: ['电话输入', '短信输入'],
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
