import { requestClient } from '#/api/request';

export interface CommunityOverviewStat {
  description: string;
  key: string;
  trend: string;
  value: string;
}

export interface CommunityOverviewTrendItem {
  date: string;
  highRisk: number;
  visits: number;
}

export interface CommunityOverviewFocusSenior {
  disposalAdvice: string;
  elderName: string;
  id: string;
  lastAlertAt: string;
  riskLevel: 'high' | 'low' | 'medium';
  tags: string[];
}

export interface CommunityOverviewWorkorder {
  assignee: string;
  elderName: string;
  id: string;
  priority: 'high' | 'low' | 'medium';
  reason: string;
  status: 'archived' | 'processing' | 'todo';
}

export interface CommunityOverviewData {
  focusSeniors: CommunityOverviewFocusSenior[];
  riskTrend: CommunityOverviewTrendItem[];
  stats: CommunityOverviewStat[];
  todoWorkorders: CommunityOverviewWorkorder[];
}

export async function getCommunityOverviewApi() {
  return requestClient.get<CommunityOverviewData>('/community/overview');
}

export interface CommunityWorkorderListParams {
  keyword?: string;
  page?: number;
  pageSize?: number;
  priority?: string;
  status?: string;
}

export interface CommunityWorkorderListItem {
  assignee: string;
  createdAt: string;
  elderName: string;
  followUpAction: string;
  id: string;
  latestProgress: string;
  priority: 'high' | 'low' | 'medium';
  riskLevel: 'high' | 'low' | 'medium';
  sourceType: 'call' | 'sms';
  status: 'archived' | 'done' | 'processing' | 'todo';
  title: string;
}

export interface CommunityWorkorderListResult {
  items: CommunityWorkorderListItem[];
  total: number;
}

export async function getCommunityWorkorderListApi(
  params: CommunityWorkorderListParams,
) {
  return requestClient.get<CommunityWorkorderListResult>(
    '/community/workorders/list',
    { params },
  );
}
