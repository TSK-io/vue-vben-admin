import type { RiskDecision } from '#/types/guardian-phone';

import { requestClient } from '#/api/request';

interface RiskRecognitionResponse {
  alert_id?: null | string;
  hit_rule_codes: string[];
  hit_terms: string[];
  notification_ids: string[];
  reason_detail: string;
  record_id: string;
  risk_level: string;
  risk_score: number;
  scene: string;
  suggestion_action: string;
  workorder_id?: null | string;
}

function normalizeRiskDecision(
  result: RiskRecognitionResponse,
): RiskDecision {
  return {
    alertId: result.alert_id,
    autoBlocked: result.risk_level === 'high',
    hitRuleCodes: result.hit_rule_codes,
    hitTerms: result.hit_terms,
    reasonDetail: result.reason_detail,
    recordId: result.record_id,
    riskLevel: result.risk_level,
    riskScore: result.risk_score,
    scene: result.scene,
    suggestionAction: result.suggestion_action,
    workorderId: result.workorder_id,
  };
}

export async function recognizeSmsApi(payload: {
  elderUserId: string;
  messageText: string;
  occurredAt?: string;
  sender?: string;
}) {
  const result = await requestClient.post<RiskRecognitionResponse>(
    '/risk-recognition/sms',
    {
      elder_user_id: payload.elderUserId,
      message_text: payload.messageText,
      occurred_at: payload.occurredAt,
      sender: payload.sender,
    },
  );
  return normalizeRiskDecision(result);
}

export async function recognizeCallTextApi(payload: {
  callerNumber?: string;
  durationSeconds?: number;
  elderUserId: string;
  occurredAt?: string;
  transcriptText: string;
}) {
  const result = await requestClient.post<RiskRecognitionResponse>(
    '/risk-recognition/call',
    {
      caller_number: payload.callerNumber,
      duration_seconds: payload.durationSeconds,
      elder_user_id: payload.elderUserId,
      occurred_at: payload.occurredAt,
      transcript_text: payload.transcriptText,
    },
  );
  return normalizeRiskDecision(result);
}
