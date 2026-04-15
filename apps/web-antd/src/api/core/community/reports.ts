import { requestClient } from '#/api/request';

import type { CommunityReportSummaryResponse } from './types';

export async function getCommunityReportApi() {
  return requestClient.get<CommunityReportSummaryResponse>('/community/reports');
}
