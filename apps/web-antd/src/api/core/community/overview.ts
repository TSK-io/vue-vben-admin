import { requestClient } from '#/api/request';

import type { CommunityOverviewData, CommunityOverviewParams } from './types';

export async function getCommunityOverviewApi(
  params: CommunityOverviewParams = {},
) {
  const [elders, workorders] = await Promise.all([
    requestClient.get<any>('/community/elders', {
      params: { page: 1, page_size: 20 },
    }),
    requestClient.get<any>('/community/workorders', {
      params: { page: 1, page_size: 20 },
    }),
  ]);
  const filteredElders = elders.items.filter((item: any) => {
    const matchesKeyword =
      !params.keyword ||
      item.elder_name?.includes(params.keyword) ||
      item.tags?.some((tag: string) => params.keyword ? tag.includes(params.keyword) : false);
    const matchesRisk =
      !params.riskLevel || item.risk_level === params.riskLevel;
    const matchesRange =
      !params.range ||
      params.range === 'all' ||
      (item.assigned_grid_member || '').includes(params.range) ||
      (item.tags || []).some((tag: string) => params.range ? tag.includes(params.range) : false);
    return matchesKeyword && matchesRisk && matchesRange;
  });
  const filteredWorkorders = workorders.items.filter((item: any) => {
    if (!params.riskLevel) return true;
    return (
      item.priority === params.riskLevel || item.risk_level === params.riskLevel
    );
  });
  const trendSource = filteredElders.slice(0, params.days ?? 7);
  return {
    focusSeniors: filteredElders.slice(0, 5).map((item: any) => ({
      disposalAdvice: `${item.follow_up_status}，建议联系${item.assigned_grid_member || '社区工作人员'}继续跟进。`,
      elderName: item.elder_name,
      id: item.elder_user_id,
      lastAlertAt: item.latest_alert_at || '-',
      riskLevel: item.risk_level,
      tags: item.tags,
    })),
    riskTrend: trendSource.map((item: any, index: number) => ({
      date: `04-${String(8 + index).padStart(2, '0')}`,
      highRisk: item.risk_level === 'high' ? 1 : 0,
      visits: item.alert_count_7d,
    })),
    stats: [
      {
        description: '重点老人',
        key: 'elders',
        trend: '来自真实社区老人接口',
        value: `${filteredElders.length}`,
      },
      {
        description: '工单总数',
        key: 'workorders',
        trend: '可继续追踪流转状态',
        value: `${filteredWorkorders.length}`,
      },
      {
        description: '高风险对象',
        key: 'highRisk',
        trend: '优先电话回访',
        value: `${filteredElders.filter((item: any) => item.risk_level === 'high').length}`,
      },
      {
        description: '处理中工单',
        key: 'processing',
        trend: '继续补录处置结果',
        value: `${filteredWorkorders.filter((item: any) => item.status === 'processing').length}`,
      },
    ],
    todoWorkorders: filteredWorkorders.slice(0, 5).map((item: any) => ({
      assignee: item.assigned_to_name || '待分配',
      elderName: item.elder_name,
      id: item.workorder_no,
      priority: item.priority,
      reason: item.title,
      status: item.status === 'pending' ? 'todo' : item.status,
    })),
  } satisfies CommunityOverviewData;
}
