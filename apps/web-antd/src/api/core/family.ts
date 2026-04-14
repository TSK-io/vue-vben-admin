import { requestClient } from '#/api/request';

export interface FamilyOverviewStat {
  description: string;
  key: string;
  trend: string;
  value: string;
}

export interface FamilyOverviewAlertTrendItem {
  date: string;
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

export async function getFamilyOverviewApi() {
  return requestClient.get<FamilyOverviewData>('/family/overview');
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

interface PaginatedResult<T> {
  items: T[];
  total: number;
}

export async function getFamilyAlertListApi(params: FamilyAlertListParams) {
  return requestClient.get<PaginatedResult<FamilyAlertItem>>(
    '/family/alerts/list',
    { params },
  );
}

export async function getFamilyNotificationListApi(
  params: FamilyNotificationListParams,
) {
  return requestClient.get<PaginatedResult<FamilyNotificationItem>>(
    '/family/notifications/list',
    { params },
  );
}
