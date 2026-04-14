import { requestClient } from '#/api/request';

export interface RiskAlertListParams {
  page?: number;
  pageSize?: number;
  riskLevel?: string;
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
    result.items.map((item: any) => requestClient.get<any>(`/risk-alerts/${item.id}`)),
  );

  return {
    items: result.items.map(
      (item: any, index: number): RiskAlertItem => ({
        advice: details[index].suggestion_action,
        contactSuggestion:
          item.risk_level === 'high' ? '建议立即联系家属并视情况同步社区。' : '建议先联系家属核实。',
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
    ),
    total: result.pagination.total,
  };
}
