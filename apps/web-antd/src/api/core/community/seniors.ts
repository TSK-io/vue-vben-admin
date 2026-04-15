import { requestClient } from '#/api/request';

import type { CommunitySeniorItem } from './types';

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
