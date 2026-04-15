import { requestClient } from '#/api/request';

export interface RiskAlertListParams {
  page?: number;
  pageSize?: number;
  riskLevel?: string;
  sourceType?: string;
  status?: string;
}

export interface RiskAlertItem {
  advice: string;
  contactSuggestion: string;
  contentPreview: string;
  elderName: string;
  hitReason: string;
  id: string;
  occurredAt: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskScore: number;
  sourceType: 'call' | 'sms';
  status: 'handled' | 'pending';
  title: string;
}

export interface RiskEventViewItem {
  alertId: string;
  alertTitle: string;
  elderName: string;
  notifiedCount: number;
  occurredAt: string;
  readNotificationCount: number;
  riskLevel: 'high' | 'low' | 'medium';
  status: 'handled' | 'pending';
  workorderCount: number;
}

function normalizeStatus(status: string): 'handled' | 'pending' {
  return status === 'closed' || status === 'handled' ? 'handled' : 'pending';
}

export async function getRiskAlertListApi(params: RiskAlertListParams) {
  const result = await requestClient.get<any>('/risk-alerts', {
    params: {
      page: params.page,
      page_size: params.pageSize,
      risk_level: params.riskLevel,
    },
  });

  const details = await Promise.all(
    result.items.map((item: any) =>
      requestClient.get<any>(`/risk-alerts/${item.id}`),
    ),
  );

  return {
    items: result.items
      .map(
        (item: any, index: number): RiskAlertItem => ({
          advice: details[index].suggestion_action,
          contactSuggestion:
            item.risk_level === 'high'
              ? '建议立即联系家属并视情况同步社区。'
              : '建议先联系家属核实。',
          contentPreview: item.summary,
          elderName: item.elder_name,
          hitReason: details[index].reason_detail,
          id: item.id,
          occurredAt: item.occurred_at,
          riskLevel: item.risk_level,
          riskScore: item.risk_score,
          sourceType: item.source_type,
          status: normalizeStatus(item.status),
          title: item.title,
        }),
      )
      .filter(
        (item: RiskAlertItem) =>
          !params.sourceType || item.sourceType === params.sourceType,
      )
      .filter(
        (item: RiskAlertItem) =>
          !params.status || item.status === params.status,
      ),
    total: result.pagination.total,
  };
}

export async function getRiskEventViewApi() {
  const [alerts, notifications] = await Promise.all([
    getRiskAlertListApi({ page: 1, pageSize: 100 }),
    requestClient.get<any>('/notifications', {
      params: {
        page: 1,
        page_size: 100,
      },
    }),
  ]);

  const notificationStats = new Map<
    string,
    { notifiedCount: number; readNotificationCount: number }
  >();

  for (const item of notifications.items ?? []) {
    const key = item.alert_id;
    const current = notificationStats.get(key) ?? {
      notifiedCount: 0,
      readNotificationCount: 0,
    };
    current.notifiedCount += 1;
    if (item.is_read) {
      current.readNotificationCount += 1;
    }
    notificationStats.set(key, current);
  }

  const detailList = await Promise.all(
    alerts.items.map((item: RiskAlertItem) =>
      requestClient.get<any>(`/risk-alerts/${item.id}`),
    ),
  );

  return alerts.items.map(
    (item: RiskAlertItem, index: number): RiskEventViewItem => ({
      alertId: item.id,
      alertTitle: item.title,
      elderName: item.elderName,
      notifiedCount: notificationStats.get(item.id)?.notifiedCount ?? 0,
      occurredAt: item.occurredAt,
      readNotificationCount:
        notificationStats.get(item.id)?.readNotificationCount ?? 0,
      riskLevel: item.riskLevel,
      status: item.status,
      workorderCount: detailList[index].related_workorder_ids.length,
    }),
  );
}
