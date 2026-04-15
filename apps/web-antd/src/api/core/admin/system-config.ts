import { requestClient } from '#/api/request';

import type { AdminSystemConfigItem } from './types';

export async function getAdminSystemConfigListApi() {
  const rows = await requestClient.get<any[]>('/admin/system-config');
  return rows.map(
    (item): AdminSystemConfigItem => ({
      auditCount: item.audit_count ?? 0,
      description: item.description,
      effectiveValue: item.effective_value,
      group: item.group,
      key: item.key,
      lastUpdatedAt: item.last_updated_at,
      lastUpdatedBy: item.last_updated_by,
      name: item.name,
      value: item.value,
    }),
  );
}

export async function updateAdminSystemConfigApi(key: string, value: string) {
  return requestClient.put(`/admin/system-config/${key}`, { value });
}
