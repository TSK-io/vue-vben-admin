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

export interface CommunityOverviewParams {
  days?: 7 | 15 | 30;
  keyword?: string;
  range?: string;
  riskLevel?: string;
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

export interface CommunitySeniorItem {
  collaboration: string;
  elderName: string;
  followUpStatus: string;
  id: string;
  labels: string[];
  manualRiskTag?: string | null;
  riskLevel: 'high' | 'low' | 'medium';
  visitRecords: Array<{ created_at: string; note: string; record_type: string }>;
}

export interface CommunityWorkorderActionItem {
  actionType: string;
  attachments: string[];
  collaborationNote?: string | null;
  createdAt: string;
  fromStatus: string;
  id: string;
  note?: string | null;
  operatorName: string;
  toStatus: string;
}

export interface CommunityWorkorderDetail {
  actions: CommunityWorkorderActionItem[];
  assignedToName?: string | null;
  closedAt?: string | null;
  disposeMethod?: string | null;
  disposeResult?: string | null;
  elderName: string;
  id: string;
  latestAlertSummary: string;
  priority: 'high' | 'low' | 'medium';
  status: string;
  title: string;
  updatedAt: string;
  workorderNo: string;
}

export interface CommunityEducationContentItem {
  audience: string;
  category: string;
  channel: string;
  id: string;
  status: string;
  summary: string;
  title: string;
  updatedAt: string;
}

export interface CommunityEducationPlan {
  channel: string;
  contentId: string;
  contentTitle: string;
  coverageGoal: number;
  createdAt: string;
  feedbackNote: string;
  id: string;
  plannedAt: string;
  pushScope: string;
  reachCount: number;
  status: 'cancelled' | 'draft' | 'published' | 'scheduled';
  targetCommunity: string;
  targetGroup: string;
  visitCount: number;
}

export interface CommunityEducationOverview {
  activeCount: number;
  contentCount: number;
  draftCount: number;
  feedbackRate: number;
  plans: CommunityEducationPlan[];
  publishedCount: number;
  recentFeedback: Array<{
    contentTitle: string;
    feedbackNote: string;
    id: string;
    plannedAt: string;
    reachCount: number;
    targetGroup: string;
    visitCount: number;
  }>;
}

export interface CommunityReportTrendItem {
  label: string;
  value: number;
}

export interface CommunityReportRankItem {
  label: string;
  value: number;
}

export interface CommunityReportExportPayload {
  csv: string;
  fileName: string;
}

export interface CommunityReportView {
  disposalAvgMinutes: number;
  educationCoverage: Array<{ label: string; value: number }>;
  exportPayload: CommunityReportExportPayload;
  monthlyTrends: CommunityReportTrendItem[];
  riskByLevel: Array<{ label: string; value: number }>;
  topCategories: CommunityReportRankItem[];
  topSeniors: CommunityReportRankItem[];
  workorderStatus: Array<{ label: string; value: number }>;
}

export interface CommunityReportSummaryResponse {
  disposal_avg_minutes: number;
  education_summary: Array<{ count: number; label: string }>;
  risk_by_level: Array<{ count: number; label: string }>;
  workorder_status: Array<{ count: number; label: string }>;
}
