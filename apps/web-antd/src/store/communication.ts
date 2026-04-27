import type {
  BlockedNumber,
  CommunicationEvent,
  PhoneTrustType,
  RiskDecision,
  TrustedContact,
} from '#/types/guardian-phone';

import { computed, ref } from 'vue';

import { useUserStore } from '@vben/stores';

import { message } from 'ant-design-vue';
import { defineStore } from 'pinia';

import { getBindingListApi, recognizeSmsApi } from '#/api';

const EVENTS_KEY = 'guardian-shield:communication-events';
const CONTACTS_KEY = 'guardian-shield:phone-contacts';
const BLACKLIST_KEY = 'guardian-shield:phone-blacklist';
const CHANNEL_NAME = 'guardian-shield-communication';

function nowIso() {
  return new Date().toISOString();
}

function makeId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function normalizePhone(phone: string) {
  return phone.replace(/\s|-/g, '').trim();
}

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback;
  const raw = window.localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson<T>(key: string, value: T) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export const useCommunicationStore = defineStore('communication', () => {
  const userStore = useUserStore();
  const events = ref<CommunicationEvent[]>(readJson(EVENTS_KEY, []));
  const contacts = ref<TrustedContact[]>(readJson(CONTACTS_KEY, []));
  const blacklist = ref<BlockedNumber[]>(readJson(BLACKLIST_KEY, []));
  const riskPopupQueue = ref<CommunicationEvent[]>([]);
  const recognizingIds = ref<string[]>([]);
  const channel =
    typeof window === 'undefined' || !('BroadcastChannel' in window)
      ? null
      : new BroadcastChannel(CHANNEL_NAME);

  const currentUserPhone = computed(
    () => userStore.userInfo?.desc || '',
  );
  const currentUserId = computed(() => userStore.userInfo?.userId || '');

  const incomingEvents = computed(() =>
    events.value
      .filter((item) => item.targetPhone === currentUserPhone.value)
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt)),
  );

  const messageEvents = computed(() =>
    incomingEvents.value.filter((item) => item.scene === 'sms'),
  );

  const callEvents = computed(() =>
    incomingEvents.value.filter((item) => item.scene === 'call'),
  );

  function persist() {
    writeJson(EVENTS_KEY, events.value);
    writeJson(CONTACTS_KEY, contacts.value);
    writeJson(BLACKLIST_KEY, blacklist.value);
  }

  function broadcast(type: string) {
    persist();
    channel?.postMessage({ type, updatedAt: nowIso() });
  }

  function reloadFromStorage() {
    events.value = readJson(EVENTS_KEY, []);
    contacts.value = readJson(CONTACTS_KEY, []);
    blacklist.value = readJson(BLACKLIST_KEY, []);
  }

  channel?.addEventListener('message', () => {
    reloadFromStorage();
  });

  function isTrustedPhone(elderPhone: string, phone: string) {
    const normalized = normalizePhone(phone);
    return contacts.value.some(
      (item) =>
        item.elderPhone === elderPhone &&
        normalizePhone(item.contactPhone) === normalized,
    );
  }

  function isBlockedPhone(elderPhone: string, phone: string) {
    const normalized = normalizePhone(phone);
    return blacklist.value.some(
      (item) =>
        item.elderPhone === elderPhone && normalizePhone(item.phone) === normalized,
    );
  }

  function getTrustType(
    elderPhone: string,
    sourcePhone: string,
  ): PhoneTrustType {
    const normalized = normalizePhone(sourcePhone);
    if (normalized === normalizePhone(elderPhone)) return 'self';
    if (isBlockedPhone(elderPhone, sourcePhone)) return 'blacklisted';
    if (isTrustedPhone(elderPhone, sourcePhone)) return 'trusted';
    return 'unknown';
  }

  function upsertEvent(next: CommunicationEvent) {
    const index = events.value.findIndex((item) => item.id === next.id);
    if (index >= 0) {
      events.value[index] = next;
    } else {
      events.value.unshift(next);
    }
    broadcast('events:update');
  }

  function addTrustedContact(contact: Omit<TrustedContact, 'id'>) {
    const exists = contacts.value.some(
      (item) =>
        item.elderPhone === contact.elderPhone &&
        normalizePhone(item.contactPhone) === normalizePhone(contact.contactPhone),
    );
    if (exists) return;
    contacts.value.unshift({ ...contact, id: makeId('contact') });
    broadcast('contacts:update');
  }

  function addBlockedNumber(
    blocked: Omit<BlockedNumber, 'createdAt' | 'id'>,
  ) {
    const exists = isBlockedPhone(blocked.elderPhone, blocked.phone);
    if (exists) return;
    blacklist.value.unshift({
      ...blocked,
      createdAt: nowIso(),
      id: makeId('blocked'),
    });
    broadcast('blacklist:update');
  }

  function removeBlockedNumber(id: string) {
    blacklist.value = blacklist.value.filter((item) => item.id !== id);
    broadcast('blacklist:update');
  }

  function handleRiskDecision(eventId: string, risk: RiskDecision) {
    const target = events.value.find((item) => item.id === eventId);
    if (!target) return;
    const next = {
      ...target,
      risk,
      status: 'delivered' as const,
      updatedAt: nowIso(),
    };
    upsertEvent(next);
    if (risk.riskLevel === 'high') {
      addBlockedNumber({
        elderPhone: target.targetPhone,
        phone: target.sourcePhone,
        reason: risk.reasonDetail,
        riskEventId: target.id,
        source: 'auto-risk',
      });
      riskPopupQueue.value.push({ ...next, risk: { ...risk, autoBlocked: true } });
      message.error('疑似诈骗风险，已加入老人端黑名单。');
      return;
    }
    if (risk.riskLevel === 'medium') {
      riskPopupQueue.value.push(next);
      message.warning('发现可疑风险，请提醒老人谨慎处理。');
    }
  }

  async function sendSmsEvent(payload: {
    contentText: string;
    elderUserId: string;
    operatorUserId?: string;
    sourcePhone: string;
    targetPhone: string;
  }) {
    const sourcePhone = normalizePhone(payload.sourcePhone);
    const targetPhone = normalizePhone(payload.targetPhone);
    const trustType = getTrustType(targetPhone, sourcePhone);
    const event: CommunicationEvent = {
      contentText: payload.contentText,
      createdAt: nowIso(),
      elderUserId: payload.elderUserId,
      id: makeId('sms'),
      operatorUserId: payload.operatorUserId || currentUserId.value,
      scene: 'sms',
      sourcePhone,
      status: trustType === 'blacklisted' ? 'intercepted' : 'delivered',
      targetPhone,
      trustType,
      updatedAt: nowIso(),
    };
    upsertEvent(event);

    if (trustType !== 'unknown') {
      return event;
    }

    recognizingIds.value.push(event.id);
    try {
      const risk = await recognizeSmsApi({
        elderUserId: payload.elderUserId,
        messageText: payload.contentText,
        occurredAt: event.createdAt,
        sender: sourcePhone,
      });
      handleRiskDecision(event.id, risk);
    } finally {
      recognizingIds.value = recognizingIds.value.filter((id) => id !== event.id);
    }
    return events.value.find((item) => item.id === event.id) || event;
  }

  function createCallEvent(payload: {
    callSessionId?: string;
    elderUserId: string;
    operatorUserId?: string;
    sourcePhone: string;
    targetPhone: string;
  }) {
    const sourcePhone = normalizePhone(payload.sourcePhone);
    const targetPhone = normalizePhone(payload.targetPhone);
    const trustType = getTrustType(targetPhone, sourcePhone);
    const event: CommunicationEvent = {
      callSessionId: payload.callSessionId,
      createdAt: nowIso(),
      elderUserId: payload.elderUserId,
      id: makeId('call'),
      operatorUserId: payload.operatorUserId || currentUserId.value,
      scene: 'call',
      sourcePhone,
      status: trustType === 'blacklisted' ? 'intercepted' : 'ringing',
      targetPhone,
      trustType,
      updatedAt: nowIso(),
    };
    upsertEvent(event);
    return event;
  }

  async function hydrateBindingContacts() {
    const phone = currentUserPhone.value;
    if (!phone) return;
    const bindings = await getBindingListApi();
    bindings.forEach((item) => {
      const guessedPhoneMap: Record<string, string> = {
        'u-family-001': '13900002001',
        'u-family-002': '13900002002',
      };
      const contactPhone = guessedPhoneMap[item.familyUserId];
      if (!contactPhone) return;
      addTrustedContact({
        contactName: item.familyName,
        contactPhone,
        contactRole: 'family',
        elderPhone: phone,
        isEmergencyContact: item.isEmergencyContact,
        relationshipType: item.relationshipType,
        source: 'binding',
      });
    });
  }

  function clearRiskPopup(eventId: string) {
    riskPopupQueue.value = riskPopupQueue.value.filter(
      (item) => item.id !== eventId,
    );
  }

  function resetDemoState() {
    events.value = [];
    blacklist.value = [];
    riskPopupQueue.value = [];
    persist();
    broadcast('demo:reset');
  }

  return {
    addBlockedNumber,
    addTrustedContact,
    blacklist,
    callEvents,
    clearRiskPopup,
    contacts,
    createCallEvent,
    currentUserPhone,
    events,
    getTrustType,
    handleRiskDecision,
    hydrateBindingContacts,
    incomingEvents,
    isBlockedPhone,
    isTrustedPhone,
    messageEvents,
    recognizingIds,
    removeBlockedNumber,
    resetDemoState,
    riskPopupQueue,
    sendSmsEvent,
    upsertEvent,
  };
});
