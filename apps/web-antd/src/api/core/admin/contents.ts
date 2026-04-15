import { requestClient } from '#/api/request';

import type { AdminContentItem, ContentPayload } from './types';

export async function getAdminContentListApi() {
  const rows = await requestClient.get<any[]>('/admin/contents');
  return rows.map(
    (item): AdminContentItem => ({
      audience: item.audience,
      category: item.category,
      channel: item.channel,
      code: item.code,
      contentType: item.content_type,
      id: item.id,
      status: item.status,
      summary: item.summary,
      title: item.title,
      updatedAt: item.updated_at,
      auditStatus: item.audit_status,
      assetUrl: item.asset_url,
    }),
  );
}

export async function createAdminContentApi(payload: ContentPayload) {
  return requestClient.post('/admin/contents', {
    audience: payload.audience,
    category: payload.category,
    channel: payload.channel,
    code: payload.code,
    content_body: payload.contentBody,
    content_type: payload.contentType,
    audit_status: payload.auditStatus,
    asset_url: payload.assetUrl,
    status: payload.status,
    summary: payload.summary,
    title: payload.title,
  });
}

export async function updateAdminContentApi(
  contentId: string,
  payload: ContentPayload,
) {
  return requestClient.put(`/admin/contents/${contentId}`, {
    audience: payload.audience,
    category: payload.category,
    channel: payload.channel,
    code: payload.code,
    content_body: payload.contentBody,
    content_type: payload.contentType,
    audit_status: payload.auditStatus,
    asset_url: payload.assetUrl,
    status: payload.status,
    summary: payload.summary,
    title: payload.title,
  });
}
