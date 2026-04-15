import { getAdminContentListApi } from '../admin/index';

import type {
  CommunityEducationContentItem,
  CommunityEducationOverview,
  CommunityEducationPlan,
} from './types';

const COMMUNITY_EDUCATION_PLAN_STORAGE_KEY =
  'guardian-shield:community-education-plans';

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
    .filter((item: Awaited<ReturnType<typeof getAdminContentListApi>>[number]) => item.contentType === 'education')
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
      (item: CommunityEducationContentItem) =>
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

export async function createCommunityEducationPlanApi(
  payload: Omit<CommunityEducationPlan, 'createdAt' | 'id'>,
) {
  const plans = await getCommunityEducationPlansApi();
  const nextPlan: CommunityEducationPlan = {
    ...payload,
    createdAt: new Date().toISOString(),
    id: `plan-${Date.now()}`,
  };
  const nextPlans = [nextPlan, ...plans];
  saveStoredEducationPlans(nextPlans);
  return nextPlan;
}

export async function updateCommunityEducationPlanApi(
  planId: string,
  payload: Partial<Omit<CommunityEducationPlan, 'createdAt' | 'id'>>,
) {
  const plans = await getCommunityEducationPlansApi();
  const nextPlans = plans.map((item) =>
    item.id === planId ? { ...item, ...payload } : item,
  );
  saveStoredEducationPlans(nextPlans);
  return nextPlans.find((item) => item.id === planId) || null;
}

export async function getCommunityEducationOverviewApi(): Promise<CommunityEducationOverview> {
  const [plans, library] = await Promise.all([
    getCommunityEducationPlansApi(),
    getCommunityEducationLibraryApi(),
  ]);

  const publishedCount = plans.filter((item: CommunityEducationPlan) => item.status === 'published').length;
  const draftCount = plans.filter((item: CommunityEducationPlan) => item.status === 'draft').length;
  const activeCount = plans.filter((item: CommunityEducationPlan) =>
    ['published', 'scheduled'].includes(item.status),
  ).length;
  const reachTotal = plans.reduce((sum: number, item: CommunityEducationPlan) => sum + item.reachCount, 0);
  const visitTotal = plans.reduce((sum: number, item: CommunityEducationPlan) => sum + item.visitCount, 0);

  return {
    activeCount,
    contentCount: library.length,
    draftCount,
    feedbackRate: reachTotal > 0 ? Number(((visitTotal / reachTotal) * 100).toFixed(1)) : 0,
    plans,
    publishedCount,
    recentFeedback: plans.slice(0, 3).map((item: CommunityEducationPlan) => ({
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
