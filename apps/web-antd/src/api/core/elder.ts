import { requestClient } from '#/api/request';

export interface BindingItem {
  elderUserId: string;
  familyUserId: string;
  id: string;
  elderName: string;
  familyName: string;
  relationshipType: string;
  status: string;
  isEmergencyContact: boolean;
  authorizedAt: string;
  familyUserId: string;
}

export interface AccessibilitySettings {
  fontScale: string;
  highContrast: boolean;
  voiceAssistant: boolean;
  voiceSpeed: string;
}

export interface KnowledgeItem {
  id: string;
  title: string;
  category: string;
  audience: string;
  summary?: string | null;
  contentBody: string;
  publishStatus: string;
  publishedAt?: string | null;
}

export async function getBindingListApi() {
  const rows = await requestClient.get<any[]>('/bindings');
  return rows.map(
    (item): BindingItem => ({
      authorizedAt: item.authorized_at,
      elderName: item.elder_name,
      elderUserId: item.elder_user_id,
      familyName: item.family_name,
      familyUserId: item.family_user_id,
      id: item.id,
      isEmergencyContact: item.is_emergency_contact,
      relationshipType: item.relationship_type,
      status: item.status,
    }),
  );
}

export async function createBindingApi(payload: {
  elderUserId: string;
  familyUserId: string;
  isEmergencyContact: boolean;
  relationshipType: string;
}) {
  return requestClient.post('/bindings', {
    elder_user_id: payload.elderUserId,
    family_user_id: payload.familyUserId,
    is_emergency_contact: payload.isEmergencyContact,
    relationship_type: payload.relationshipType,
  });
}

export async function updateBindingApi(
  bindingId: string,
  payload: { isEmergencyContact?: boolean; relationshipType?: string; status?: string },
) {
  return requestClient.patch(`/bindings/${bindingId}`, {
    is_emergency_contact: payload.isEmergencyContact,
    relationship_type: payload.relationshipType,
    status: payload.status,
  });
}

export async function deleteBindingApi(bindingId: string) {
  return requestClient.delete(`/bindings/${bindingId}`);
}

export async function createHelpRequestApi(payload: {
  actionType: string;
  note?: string;
  notifyCommunity?: boolean;
  notifyFamily?: boolean;
}) {
  return requestClient.post('/elder/help-requests', {
    action_type: payload.actionType,
    note: payload.note,
    notify_community: payload.notifyCommunity ?? true,
    notify_family: payload.notifyFamily ?? true,
  });
}

export async function getAccessibilitySettingsApi() {
  const result = await requestClient.get<any>('/elder/accessibility-settings');
  return {
    fontScale: result.font_scale,
    highContrast: result.high_contrast,
    voiceAssistant: result.voice_assistant,
    voiceSpeed: result.voice_speed,
  } satisfies AccessibilitySettings;
}

export async function updateAccessibilitySettingsApi(payload: AccessibilitySettings) {
  return requestClient.put('/elder/accessibility-settings', {
    font_scale: payload.fontScale,
    high_contrast: payload.highContrast,
    voice_assistant: payload.voiceAssistant,
    voice_speed: payload.voiceSpeed,
  });
}

export async function getElderKnowledgeListApi(category?: string) {
  const rows = await requestClient.get<any[]>('/elder/knowledge', {
    params: { category },
  });
  return rows.map(
    (item): KnowledgeItem => ({
      audience: item.audience,
      category: item.category,
      contentBody: item.content_body,
      id: item.id,
      publishStatus: item.publish_status,
      publishedAt: item.published_at,
      summary: item.summary,
      title: item.title,
    }),
  );
}
