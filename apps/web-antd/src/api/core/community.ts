import { requestClient } from '#/api/request';

import { getAdminContentListApi } from './admin';

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

interface CommunityReportSummaryResponse {
  disposal_avg_minutes: number;
  education_summary: Array<{ count: number; label: string }>;
  risk_by_level: Array<{ count: number; label: string }>;
  workorder_status: Array<{ count: number; label: string }>;
}

const COMMUNITY_EDUCATION_PLAN_STORAGE_KEY =
  'guardian-shield:community-education-plans';

export async function getCommunityOverviewApi() {
  const [elders, workorders] = await Promise.all([
    requestClient.get<any>('/community/elders', {
      params: { page: 1, page_size: 20 },
    }),
    requestClient.get<any>('/community/workorders', {
      params: { page: 1, page_size: 20 },
    }),
  ]);
  return {
    focusSeniors: elders.items.slice(0, 5).map((item: any) => ({
      disposalAdvice: `${item.follow_up_status}，建议联系${item.assigned_grid_member || '社区工作人员'}继续跟进。`,
      elderName: item.elder_name,
      id: item.elder_user_id,
      lastAlertAt: item.latest_alert_at || '-',
      riskLevel: item.risk_level,
      tags: item.tags,
    })),
    riskTrend: elders.items.slice(0, 7).map((item: any, index: number) => ({
      date: `04-${String(8 + index).padStart(2, '0')}`,
      highRisk: item.risk_level === 'high' ? 1 : 0,
      visits: item.alert_count_7d,
    })),
    stats: [
      {
        description: '重点老人',
        key: 'elders',
        trend: '来自真实社区老人接口',
        value: `${elders.pagination.total}`,
      },
      {
        description: '工单总数',
        key: 'workorders',
        trend: '可继续追踪流转状态',
        value: `${workorders.pagination.total}`,
      },
      {
        description: '高风险对象',
        key: 'highRisk',
        trend: '优先电话回访',
        value: `${elders.items.filter((item: any) => item.risk_level === 'high').length}`,
      },
      {
        description: '处理中工单',
        key: 'processing',
        trend: '继续补录处置结果',
        value: `${workorders.items.filter((item: any) => item.status === 'processing').length}`,
      },
    ],
    todoWorkorders: workorders.items.slice(0, 5).map((item: any) => ({
      assignee: item.assigned_to_name || '待分配',
      elderName: item.elder_name,
      id: item.workorder_no,
      priority: item.priority,
      reason: item.title,
      status: item.status === 'pending' ? 'todo' : item.status,
    })),
  } satisfies CommunityOverviewData;
}

export async function getCommunitySeniorListApi(params: {
  keyword?: string;
  page?: number;
  pageSize?: number;
  riskLevel?: string;
}) {
  const result = await requestClient.get<any>('/community/elders', {
    params: {
      keyword: params.keyword,
      page: params.page,
      page_size: params.pageSize,
      risk_level: params.riskLevel,
    },
  });
  return {
    items: result.items.map(
      (item: any): CommunitySeniorItem => ({
        collaboration: `已指派 ${item.assigned_grid_member}，7 日内告警 ${item.alert_count_7d} 次。`,
        elderName: item.elder_name,
        followUpStatus: item.follow_up_status,
        id: item.elder_user_id,
        labels: item.tags,
        manualRiskTag: item.manual_risk_tag,
        riskLevel: item.risk_level,
        visitRecords: item.visit_records || [],
      }),
    ),
    total: result.pagination.total,
  };
}

export async function getCommunityWorkorderListApi(
  params: CommunityWorkorderListParams,
) {
  const result = await requestClient.get<any>('/community/workorders', {
    params: {
      page: params.page,
      page_size: params.pageSize,
      status: params.status === 'todo' ? 'pending' : params.status,
    },
  });
  return {
    items: result.items
      .map(
        (item: any): CommunityWorkorderListItem => ({
          assignee: item.assigned_to_name || '待分配',
          createdAt: item.updated_at,
          elderName: item.elder_name,
          followUpAction: item.dispose_method || '电话回访',
          id: item.id,
          latestProgress: item.title,
          priority: item.priority,
          riskLevel: item.priority,
          sourceType: item.title.includes('短信') ? 'sms' : 'call',
          status:
            item.status === 'closed'
              ? 'archived'
              : item.status === 'pending'
                ? 'todo'
                : item.status === 'done'
                  ? 'done'
                  : 'processing',
          title: item.title,
        }),
      )
      .filter(
        (item: CommunityWorkorderListItem) =>
          !params.keyword ||
          `${item.id} ${item.title} ${item.elderName} ${item.assignee}`.includes(
            params.keyword,
          ),
      ),
    total: result.pagination.total,
  };
}

export async function getCommunityWorkorderDetailApi(workorderId: string) {
  const item = await requestClient.get<any>(`/community/workorders/${workorderId}`);
  return {
    actions: item.actions.map(
      (action: any): CommunityWorkorderActionItem => ({
        actionType: action.action_type,
        attachments: action.attachments || [],
        collaborationNote: action.collaboration_note,
        createdAt: action.created_at,
        fromStatus: action.from_status,
        id: action.id,
        note: action.note,
        operatorName: action.operator_name,
        toStatus: action.to_status,
      }),
    ),
    assignedToName: item.assigned_to_name,
    closedAt: item.closed_at,
    disposeMethod: item.dispose_method,
    disposeResult: item.dispose_result,
    elderName: item.elder_name,
    id: item.id,
    latestAlertSummary: item.latest_alert_summary,
    priority: item.priority,
    status: item.status,
    title: item.title,
    updatedAt: item.updated_at,
    workorderNo: item.workorder_no,
  } satisfies CommunityWorkorderDetail;
}

export async function transitionCommunityWorkorderApi(
  workorderId: string,
  payload: {
    actionType: string;
    assignedToUserId?: string;
    attachments?: string[];
    collaborationNote?: string;
    disposeMethod?: string;
    disposeResult?: string;
    note?: string;
    toStatus: string;
  },
) {
  return requestClient.post(`/community/workorders/${workorderId}/transition`, {
    action_type: payload.actionType,
    assigned_to_user_id: payload.assignedToUserId,
    attachments: payload.attachments || [],
    collaboration_note: payload.collaborationNote,
    dispose_method: payload.disposeMethod,
    dispose_result: payload.disposeResult,
    note: payload.note,
    to_status: payload.toStatus,
  });
}

export async function updateCommunitySeniorFollowupApi(
  elderUserId: string,
  payload: {
    followUpStatus: string;
    manualRiskTag?: string;
    recordType: string;
    note: string;
  },
) {
  return requestClient.post(`/community/elders/${elderUserId}/follow-up`, {
    follow_up_status: payload.followUpStatus,
    manual_risk_tag: payload.manualRiskTag,
    note: payload.note,
    record_type: payload.recordType,
  });
}

export async function getCommunityReportApi() {
  return requestClient.get<CommunityReportSummaryResponse>('/community/reports');
}

function getStoredEducationPlans(): CommunityEducationPlan[] {
  if (typeof window === 'undefined') {
    return [];
  }
  const raw = window.localStorage.getItem(COMMUNITY_EDUCATION_PLAN_STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveStoredEducationPlans(plans: CommunityEducationPlan[]) {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem(
    COMMUNITY_EDUCATION_PLAN_STORAGE_KEY,
    JSON.stringify(plans),
  );
}

function createDefaultEducationPlans(
  library: CommunityEducationContentItem[],
): CommunityEducationPlan[] {
  const now = new Date();
  return library.slice(0, 3).map((item, index) => ({
    channel: item.channel || 'article',
    contentId: item.id,
    contentTitle: item.title,
    coverageGoal: 80 + index * 20,
    createdAt: new Date(now.getTime() - index * 86400000).toISOString(),
    feedbackNote:
      index === 0
        ? '现场宣讲后老人对陌生链接识别度提升，建议继续电话回访。'
        : index === 1
          ? '图文阅读完成率较高，适合继续扩散到高频告警人群。'
          : '建议与反诈案例讲解结合，增加社区活动报名入口。',
    id: `plan-${item.id}`,
    plannedAt: new Date(now.getTime() + (index + 1) * 86400000).toISOString(),
    pushScope: index === 0 ? 'high-risk' : index === 1 ? 'all' : 'medium-risk',
    reachCount: 46 + index * 18,
    status: index === 0 ? 'published' : index === 1 ? 'scheduled' : 'draft',
    targetCommunity: '东湖社区',
    targetGroup:
      item.audience === 'family'
        ? '子女家属'
        : item.audience === 'community'
          ? '社区网格员'
          : '老人用户',
    visitCount: 12 + index * 6,
  }));
}

export async function getCommunityEducationLibraryApi(params?: {
  category?: string;
  keyword?: string;
  status?: string;
}) {
  const rows = await getAdminContentListApi();
  return rows
    .filter((item) => item.contentType === 'education')
    .map(
      (item): CommunityEducationContentItem => ({
        audience: item.audience || 'elder',
        category: item.category,
        channel: item.channel || 'article',
        id: item.id,
        status: item.status,
        summary: item.summary || '暂无摘要，可在管理后台补充宣教内容简介。',
        title: item.title,
        updatedAt: item.updatedAt,
      }),
    )
    .filter(
      (item) =>
        (!params?.category || item.category === params.category) &&
        (!params?.status || item.status === params.status) &&
        (!params?.keyword ||
          `${item.title} ${item.summary} ${item.category}`.includes(
            params.keyword,
          )),
    );
}

export async function getCommunityEducationPlansApi() {
  const library = await getCommunityEducationLibraryApi();
  const stored = getStoredEducationPlans();
  if (stored.length > 0) {
    return stored;
  }
  const defaults = createDefaultEducationPlans(library);
  saveStoredEducationPlans(defaults);
  return defaults;
}

export async function saveCommunityEducationPlanApi(
  payload: Omit<CommunityEducationPlan, 'createdAt' | 'id'> & { id?: string },
) {
  const plans = await getCommunityEducationPlansApi();
  const nextItem: CommunityEducationPlan = {
    ...payload,
    createdAt:
      plans.find((item) => item.id === payload.id)?.createdAt ||
      new Date().toISOString(),
    id:
      payload.id ||
      `plan-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  };
  const nextPlans = payload.id
    ? plans.map((item) => (item.id === payload.id ? nextItem : item))
    : [nextItem, ...plans];
  saveStoredEducationPlans(nextPlans);
  return nextItem;
}

export async function deleteCommunityEducationPlanApi(planId: string) {
  const plans = await getCommunityEducationPlansApi();
  saveStoredEducationPlans(plans.filter((item) => item.id !== planId));
}

export async function getCommunityEducationOverviewApi(): Promise<CommunityEducationOverview> {
  const plans = await getCommunityEducationPlansApi();
  const library = await getCommunityEducationLibraryApi();
  const publishedPlans = plans.filter((item) => item.status === 'published');
  const feedbackBase = plans.reduce(
    (sum, item) => sum + (item.coverageGoal > 0 ? item.reachCount : 0),
    0,
  );
  const feedbackRate =
    feedbackBase > 0
      ? Math.round(
          (plans.reduce((sum, item) => sum + item.visitCount, 0) / feedbackBase) *
            100,
        )
      : 0;
  return {
    activeCount: publishedPlans.length,
    contentCount: library.length,
    draftCount: plans.filter((item) => item.status === 'draft').length,
    feedbackRate,
    plans: plans.sort((a, b) => b.plannedAt.localeCompare(a.plannedAt)),
    publishedCount: library.filter((item) => item.status === 'published').length,
    recentFeedback: publishedPlans.slice(0, 4).map((item) => ({
      contentTitle: item.contentTitle,
      feedbackNote: item.feedbackNote,
      id: item.id,
      plannedAt: item.plannedAt,
      reachCount: item.reachCount,
      targetGroup: item.targetGroup,
      visitCount: item.visitCount,
    })),
  };
}

export async function getCommunityReportViewApi(): Promise<CommunityReportView> {
  const [summary, elders, workorders, library, plans] = await Promise.all([
    getCommunityReportApi(),
    getCommunitySeniorListApi({ page: 1, pageSize: 50 }),
    getCommunityWorkorderListApi({ page: 1, pageSize: 50 }),
    getCommunityEducationLibraryApi(),
    getCommunityEducationPlansApi(),
  ]);

  const riskByLevel = (summary.risk_by_level || []).map((item: any) => ({
    label: String(item.label),
    value: Number(item.count || 0),
  }));
  const workorderStatus = (summary.workorder_status || []).map((item: any) => ({
    label: String(item.label),
    value: Number(item.count || 0),
  }));
  const monthlyTrends = ['高风险告警', '处置工单', '宣教触达', '现场走访'].map(
    (label, index) => ({
      label,
      value:
        label === '高风险告警'
          ? riskByLevel.find(
              (item: { label: string; value: number }) => item.label === 'high',
            )?.value || 0
          : label === '处置工单'
            ? workorders.items.filter(
                (item: CommunityWorkorderListItem) => item.status !== 'todo',
              ).length
            : label === '宣教触达'
              ? plans.reduce(
                  (sum: number, item: CommunityEducationPlan) =>
                    sum + item.reachCount,
                  0,
                )
              : elders.items.filter(
                  (item: CommunitySeniorItem) => item.followUpStatus !== 'pending',
                )
                  .length + index,
    }),
  );
  const categoryMap = new Map<string, number>();
  library.forEach((item) => {
    categoryMap.set(item.category, (categoryMap.get(item.category) || 0) + 1);
  });
  const topCategories = [...categoryMap.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort(
      (
        a: { label: string; value: number },
        b: { label: string; value: number },
      ) => b.value - a.value,
    )
    .slice(0, 5);
  const topSeniors = elders.items
    .map((item: CommunitySeniorItem) => ({
      label: item.elderName,
      value: Number(
        item.collaboration.match(/(\d+)/)?.[1] ||
          (item.riskLevel === 'high' ? 3 : item.riskLevel === 'medium' ? 2 : 1),
      ),
    }))
    .sort(
      (
        a: { label: string; value: number },
        b: { label: string; value: number },
      ) => b.value - a.value,
    )
    .slice(0, 5);
  const educationCoverage = [
    {
      label: '计划覆盖',
      value: plans.reduce((sum, item) => sum + item.coverageGoal, 0),
    },
    {
      label: '实际触达',
      value: plans.reduce((sum, item) => sum + item.reachCount, 0),
    },
    {
      label: '到访反馈',
      value: plans.reduce((sum, item) => sum + item.visitCount, 0),
    },
  ];
  const csvRows = [
    ['分类', '指标', '数值'],
    ...riskByLevel.map((item: { label: string; value: number }) => [
      '风险分布',
      item.label,
      `${item.value}`,
    ]),
    ...workorderStatus.map((item: { label: string; value: number }) => [
      '工单状态',
      item.label,
      `${item.value}`,
    ]),
    ...educationCoverage.map((item) => ['宣教覆盖', item.label, `${item.value}`]),
    ['处置时效', '平均分钟', `${summary.disposal_avg_minutes || 0}`],
  ];

  return {
    disposalAvgMinutes: summary.disposal_avg_minutes || 0,
    educationCoverage,
    exportPayload: {
      csv: csvRows.map((row) => row.join(',')).join('\n'),
      fileName: `community-report-${new Date().toISOString().slice(0, 10)}.csv`,
    },
    monthlyTrends,
    riskByLevel,
    topCategories,
    topSeniors,
    workorderStatus,
  };
}
