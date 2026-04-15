import { requestClient } from '#/api/request';

import type { AdminRiskAlertDetail, AdminRiskAlertItem } from './types';

export async function getAdminRiskAlertListApi() {
  const rows = await requestClient.get<any[]>('/admin/risk-alerts');
  return rows.map(
    (item): AdminRiskAlertItem => ({
      elderName: item.elder_name,
      elderUserId: item.elder_user_id,
      id: item.id,
      occurredAt: item.occurred_at,
      relatedNotifications: item.related_notifications,
      relatedWorkorders: item.related_workorders,
      riskLevel: item.risk_level,
      sourceType: item.source_type,
      status: item.status,
      title: item.title,
    }),
  );
}

export async function getAdminRiskAlertDetailApi(alertId: string) {
  const item = await requestClient.get<any>(`/admin/risk-alerts/${alertId}`);
  return {
    elderName: item.elder_name,
    elderUserId: item.elder_user_id,
    id: item.id,
    occurredAt: item.occurred_at,
    reasonDetail: item.reason_detail,
    relatedNotificationIds: item.related_notification_ids,
    relatedNotifications: item.related_notifications,
    relatedWorkorderIds: item.related_workorder_ids,
    relatedWorkorders: item.related_workorders,
    riskLevel: item.risk_level,
    sourceType: item.source_type,
    status: item.status,
    suggestionAction: item.suggestion_action,
    title: item.title,
  } satisfies AdminRiskAlertDetail;
}
