import { requestClient } from '#/api/request';

import { getRiskAlertListApi } from './risk';

export interface FamilyOverviewStat {
  description: string;
  key: string;
  trend: string;
  value: string;
}

export interface FamilyOverviewAlertTrendItem {
  date: string;
  high: number;
  low: number;
  medium: number;
  total: number;
}

export interface FamilyOverviewRiskDistributionItem {
  count: number;
  label: string;
}

export interface FamilyOverviewFocusItem {
  currentStatus: string;
  elderName: string;
  id: string;
  lastAlertAt: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskSummary: string;
}

export interface FamilyOverviewData {
  alertTrend: FamilyOverviewAlertTrendItem[];
  focusList: FamilyOverviewFocusItem[];
  riskDistribution: FamilyOverviewRiskDistributionItem[];
  stats: FamilyOverviewStat[];
}

export interface FamilySeniorListItem {
  bindStatus: string;
  elderName: string;
  id: string;
  lastAlert: string;
  latestAlertTitle: string;
  relation: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskSummary: string;
}

export interface FamilyAlertListParams {
  page?: number;
  pageSize?: number;
  readStatus?: string;
  riskLevel?: string;
  status?: string;
}

export interface FamilyAlertItem {
  advice: string;
  contactSuggestion: string;
  elderName: string;
  handledAt?: string;
  hitReason: string;
  id: string;
  occurredAt: string;
  readStatus: 'read' | 'unread';
  remoteMessage: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskScore: number;
  sourceType: 'call' | 'sms';
  status: 'handled' | 'pending';
  title: string;
}

export interface FamilyNotificationItem {
  channel: 'app' | 'sms' | 'voice';
  elderName: string;
  id: string;
  notifiedAt: string;
  operatorName: string;
  readStatus: 'read' | 'unread';
  relatedAlertTitle: string;
  result: 'delivered' | 'failed' | 'processing';
  riskLevel: 'high' | 'low' | 'medium';
  status: 'closed' | 'follow_up' | 'pending';
}

export interface FamilyNotificationListParams {
  page?: number;
  pageSize?: number;
  readStatus?: string;
  riskLevel?: string;
  status?: string;
}

export interface FamilyReminderTemplateItem {
  id: string;
  code: string;
  name: string;
  channel: string;
  content: string;
  status: string;
  isDefault: boolean;
  notes?: string | null;
}

export interface FamilyReminderReceiptItem {
  notificationId: string;
  elderUserId: string;
  elderName: string;
  channel: 'app' | 'sms' | 'voice';
  content: string;
  sentAt: string;
  receiptStatus: string;
  readAt?: string | null;
}

export async function getFamilyOverviewApi() {
  const [bindings, alerts] = await Promise.all([
    requestClient.get<any[]>('/bindings'),
    getRiskAlertListApi({ page: 1, pageSize: 50 }),
  ]);
  const trendMap = new Map<
    string,
    { date: string; high: number; low: number; medium: number; total: number }
  >();
  for (const item of alerts.items) {
    const date = item.occurredAt.slice(5, 10);
    const current = trendMap.get(date) || {
      date,
      high: 0,
      low: 0,
      medium: 0,
      total: 0,
    };
    current.total += 1;
    if (item.riskLevel === 'high') current.high += 1;
    if (item.riskLevel === 'medium') current.medium += 1;
    if (item.riskLevel === 'low') current.low += 1;
    trendMap.set(date, current);
  }
  const riskDistribution = [
    {
      count: alerts.items.filter(
        (item: { riskLevel: string }) => item.riskLevel === 'high',
      ).length,
      label: '高风险',
    },
    {
      count: alerts.items.filter(
        (item: { riskLevel: string }) => item.riskLevel === 'medium',
      ).length,
      label: '中风险',
    },
    {
      count: alerts.items.filter(
        (item: { riskLevel: string }) => item.riskLevel === 'low',
      ).length,
      label: '低风险',
    },
  ];
  const highRiskCount =
    riskDistribution.find((item) => item.label === '高风险')?.count ?? 0;
  return {
    alertTrend: alerts.items
      .slice(0, 7)
      .map((item: { occurredAt: string }) => item.occurredAt.slice(5, 10))
      .filter((value, index, values) => values.indexOf(value) === index)
      .map((date) => trendMap.get(date)!)
      .filter(Boolean),
    focusList: alerts.items.slice(0, 5).map((item: FamilyAlertItem | any) => ({
      currentStatus: item.status === 'pending' ? '待跟进' : '已处理',
      elderName: item.elderName,
      id: item.id,
      lastAlertAt: item.occurredAt,
      riskLevel: item.riskLevel,
      riskSummary: item.hitReason,
    })),
    riskDistribution,
    stats: [
      {
        description: '已绑定老人',
        key: 'bindings',
        trend: '监护关系已接真实绑定数据',
        value: `${bindings.length}`,
      },
      {
        description: '风险事件',
        key: 'alerts',
        trend: '来自真实风险告警接口',
        value: `${alerts.total}`,
      },
      {
        description: '高风险',
        key: 'high',
        trend: '优先联系老人并核实',
        value: `${highRiskCount}`,
      },
      {
        description: '待跟进',
        key: 'pending',
        trend: '继续查看通知与提醒发送',
        value: `${alerts.items.filter((item: { status: string }) => item.status === 'pending').length}`,
      },
    ],
  } satisfies FamilyOverviewData;
}

export async function getFamilyAlertListApi(params: FamilyAlertListParams) {
  const alerts = await getRiskAlertListApi({
    page: params.page,
    pageSize: params.pageSize,
    riskLevel: params.riskLevel,
  });
  return {
    items: alerts.items
      .map(
        (item: (typeof alerts.items)[number]): FamilyAlertItem => ({
          advice: item.advice,
          contactSuggestion: item.contactSuggestion,
          elderName: item.elderName,
          handledAt: item.status === 'handled' ? item.occurredAt : undefined,
          hitReason: item.hitReason,
          id: item.id,
          occurredAt: item.occurredAt,
          readStatus: 'unread',
          remoteMessage: '先不要转账，我马上联系您核实。',
          riskLevel: item.riskLevel,
          riskScore: item.riskScore,
          sourceType: item.sourceType,
          status: item.status,
          title: item.title,
        }),
      )
      .filter(
        (item: FamilyAlertItem) =>
          !params.status || item.status === params.status,
      ),
    total: alerts.total,
  };
}

function formatBindingDays(authorizedAt?: string) {
  if (!authorizedAt) {
    return '已绑定';
  }
  const start = new Date(authorizedAt).getTime();
  if (Number.isNaN(start)) {
    return '已绑定';
  }
  const days = Math.max(
    1,
    Math.floor((Date.now() - start) / (24 * 60 * 60 * 1000)),
  );
  return `已绑定 ${days} 天`;
}

export async function getFamilySeniorListApi(params: {
  keyword?: string;
  riskLevel?: string;
}) {
  const [bindings, alerts] = await Promise.all([
    requestClient.get<any[]>('/bindings'),
    getRiskAlertListApi({ page: 1, pageSize: 100 }),
  ]);

  const latestAlertMap = new Map<string, (typeof alerts.items)[number]>();
  for (const item of alerts.items) {
    if (!latestAlertMap.has(item.elderName)) {
      latestAlertMap.set(item.elderName, item);
    }
  }

  const items = bindings
    .map((item): FamilySeniorListItem => {
      const latestAlert = latestAlertMap.get(item.elder_name);
      return {
        bindStatus: formatBindingDays(item.authorized_at),
        elderName: item.elder_name,
        id: item.elder_user_id,
        lastAlert: latestAlert?.occurredAt ?? '暂无告警',
        latestAlertTitle: latestAlert?.title ?? '暂无风险告警',
        relation: item.relationship_type,
        riskLevel: latestAlert?.riskLevel ?? 'low',
        riskSummary:
          latestAlert?.hitReason ?? '当前暂无风险告警，可继续保持日常关怀。',
      };
    })
    .filter(
      (item) =>
        !params.keyword ||
        [
          item.elderName,
          item.relation,
          item.latestAlertTitle,
          item.id,
          item.riskSummary,
        ]
          .join(' ')
          .toLowerCase()
          .includes(params.keyword.toLowerCase()),
    )
    .filter((item) => !params.riskLevel || item.riskLevel === params.riskLevel);

  return {
    items,
    total: items.length,
  };
}

export async function getFamilyNotificationListApi(
  params: FamilyNotificationListParams,
) {
  const result = await requestClient.get<any>('/notifications', {
    params: {
      is_read: params.readStatus ? params.readStatus === 'read' : undefined,
      page: params.page,
      page_size: params.pageSize,
    },
  });

  return {
    items: result.items
      .map(
        (item: any): FamilyNotificationItem => ({
          channel:
            item.channel === 'voice'
              ? 'voice'
              : item.channel === 'sms'
                ? 'sms'
                : 'app',
          elderName: item.alert_title.includes('周叔叔') ? '周叔叔' : '李阿姨',
          id: item.id,
          notifiedAt: item.sent_at,
          operatorName: item.receiver_name,
          readStatus: item.is_read ? 'read' : 'unread',
          relatedAlertTitle: item.alert_title,
          result:
            item.status === 'failed'
              ? 'failed'
              : item.status === 'pending'
                ? 'processing'
                : 'delivered',
          riskLevel: item.alert_title.includes('高风险') ? 'high' : 'medium',
          status:
            item.status === 'follow_up' || item.status === 'closed'
              ? item.status
              : item.is_read
                ? 'closed'
                : 'pending',
        }),
      )
      .filter(
        (item: FamilyNotificationItem) =>
          !params.riskLevel || item.riskLevel === params.riskLevel,
      )
      .filter(
        (item: FamilyNotificationItem) =>
          !params.status || item.status === params.status,
      ),
    total: result.pagination.total,
  };
}

export async function markFamilyNotificationReadApi(notificationId: string) {
  return (requestClient as any).patch(`/notifications/${notificationId}/read`);
}

export async function updateFamilyNotificationActionApi(
  notificationId: string,
  payload: { note?: string; status: string },
) {
  return (requestClient as any).patch(`/notifications/${notificationId}/action`, {
    note: payload.note,
    status: payload.status,
  });
}

export async function sendFamilyReminderApi(payload: {
  channel: string;
  content: string;
  elderUserId: string;
}) {
  return requestClient.post('/family/reminders', {
    channel: payload.channel,
    content: payload.content,
    elder_user_id: payload.elderUserId,
  });
}

export async function getFamilyReminderTemplatesApi() {
  const rows = await requestClient.get<any[]>('/family/reminder-templates');
  return rows.map(
    (item): FamilyReminderTemplateItem => ({
      channel: item.channel,
      code: item.code,
      content: item.content,
      id: item.id,
      isDefault: item.is_default,
      name: item.name,
      notes: item.notes,
      status: item.status,
    }),
  );
}

export async function createFamilyReminderTemplateApi(
  payload: Omit<FamilyReminderTemplateItem, 'id'>,
) {
  return requestClient.post('/family/reminder-templates', {
    channel: payload.channel,
    code: payload.code,
    content: payload.content,
    is_default: payload.isDefault,
    name: payload.name,
    notes: payload.notes,
    status: payload.status,
  });
}

export async function updateFamilyReminderTemplateApi(
  templateId: string,
  payload: Omit<FamilyReminderTemplateItem, 'id'>,
) {
  return requestClient.put(`/family/reminder-templates/${templateId}`, {
    channel: payload.channel,
    code: payload.code,
    content: payload.content,
    is_default: payload.isDefault,
    name: payload.name,
    notes: payload.notes,
    status: payload.status,
  });
}

export async function getFamilyReminderReceiptsApi() {
  const rows = await requestClient.get<any[]>('/family/reminder-receipts');
  return rows.map(
    (item): FamilyReminderReceiptItem => ({
      channel: item.channel,
      content: item.content,
      elderName: item.elder_name,
      elderUserId: item.elder_user_id,
      notificationId: item.notification_id,
      readAt: item.read_at,
      receiptStatus: item.receipt_status,
      sentAt: item.sent_at,
    }),
  );
}
