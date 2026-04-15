import { requestClient } from '#/api/request';

import type {
  CommunityWorkorderActionItem,
  CommunityWorkorderDetail,
  CommunityWorkorderListItem,
  CommunityWorkorderListParams,
} from './types';

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
