import { requestClient } from '#/api/request';

import type { RiskLexiconItem, RiskLexiconPayload } from './types';

export async function getAdminLexiconListApi(scene?: string) {
  const rows = await requestClient.get<any[]>('/admin/lexicon', {
    params: { scene },
  });
  return rows.map(
    (item): RiskLexiconItem => ({
      category: item.category,
      id: item.id,
      notes: item.notes,
      riskLevel: item.risk_level,
      scene: item.scene,
      source: item.source,
      status: item.status,
      term: item.term,
    }),
  );
}

export async function createAdminLexiconApi(payload: RiskLexiconPayload) {
  return requestClient.post('/admin/lexicon', {
    category: payload.category,
    notes: payload.notes,
    risk_level: payload.riskLevel,
    scene: payload.scene,
    source: payload.source,
    status: payload.status,
    term: payload.term,
  });
}

export async function updateAdminLexiconApi(
  termId: string,
  payload: RiskLexiconPayload,
) {
  return requestClient.put(`/admin/lexicon/${termId}`, {
    category: payload.category,
    notes: payload.notes,
    risk_level: payload.riskLevel,
    scene: payload.scene,
    source: payload.source,
    status: payload.status,
    term: payload.term,
  });
}
