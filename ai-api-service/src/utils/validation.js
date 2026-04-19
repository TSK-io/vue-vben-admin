const MAX_TEXT_LENGTH = 5000;
const MAX_REVIEW_NOTE_LENGTH = 1000;

export function validateFraudDetectPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return {
      error: 'Request body must be a JSON object.'
    };
  }

  const text = typeof payload.text === 'string' ? payload.text.trim() : '';
  const scene = typeof payload.scene === 'string' ? payload.scene.trim() : 'generic';
  const source = typeof payload.source === 'string' ? payload.source.trim() : 'unknown';

  if (!text) {
    return {
      error: '`text` is required and must be a non-empty string.'
    };
  }

  if (text.length > MAX_TEXT_LENGTH) {
    return {
      error: `\`text\` must be no longer than ${MAX_TEXT_LENGTH} characters.`
    };
  }

  return {
    value: {
      scene: scene || 'generic',
      source: source || 'unknown',
      text
    }
  };
}

export function validateBatchPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return {
      error: 'Request body must be a JSON object.'
    };
  }

  if (!Array.isArray(payload.items) || payload.items.length === 0) {
    return {
      error: '`items` is required and must be a non-empty array.'
    };
  }

  if (payload.items.length > 20) {
    return {
      error: '`items` must contain at most 20 entries.'
    };
  }

  const normalized = [];

  for (const item of payload.items) {
    const result = validateFraudDetectPayload(item);
    if (result.error) {
      return result;
    }
    normalized.push(result.value);
  }

  return { value: normalized };
}

export function validateChatLogPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return { error: 'Request body must be a JSON object.' };
  }

  if (!Array.isArray(payload.messages) || payload.messages.length === 0) {
    return { error: '`messages` is required and must be a non-empty array.' };
  }

  if (payload.messages.length > 50) {
    return { error: '`messages` must contain at most 50 entries.' };
  }

  const messages = [];
  for (const message of payload.messages) {
    if (!message || typeof message !== 'object' || Array.isArray(message)) {
      return { error: 'Each message must be a JSON object.' };
    }

    const role = typeof message.role === 'string' ? message.role.trim() : 'unknown';
    const text = typeof message.text === 'string' ? message.text.trim() : '';

    if (!text) {
      return { error: 'Each message must include a non-empty `text` string.' };
    }

    if (text.length > MAX_TEXT_LENGTH) {
      return { error: `Each message text must be no longer than ${MAX_TEXT_LENGTH} characters.` };
    }

    messages.push({ role: role || 'unknown', text });
  }

  return {
    value: {
      messages,
      source: typeof payload.source === 'string' ? payload.source.trim() || 'unknown' : 'unknown'
    }
  };
}

export function validateLinkPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return { error: 'Request body must be a JSON object.' };
  }

  const link = typeof payload.link === 'string' ? payload.link.trim() : '';
  if (!link) {
    return { error: '`link` is required and must be a non-empty string.' };
  }

  return { value: { link } };
}

export function validateReviewPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return { error: 'Request body must be a JSON object.' };
  }

  const targetId = typeof payload.targetId === 'string' ? payload.targetId.trim() : '';
  const reviewer = typeof payload.reviewer === 'string' ? payload.reviewer.trim() : '';
  const decision = typeof payload.decision === 'string' ? payload.decision.trim() : '';
  const note = typeof payload.note === 'string' ? payload.note.trim() : '';

  if (!targetId) {
    return { error: '`targetId` is required.' };
  }

  if (!reviewer) {
    return { error: '`reviewer` is required.' };
  }

  if (!['confirmed-fraud', 'confirmed-safe', 'needs-follow-up'].includes(decision)) {
    return { error: '`decision` must be one of confirmed-fraud, confirmed-safe, needs-follow-up.' };
  }

  if (note.length > MAX_REVIEW_NOTE_LENGTH) {
    return { error: `\`note\` must be no longer than ${MAX_REVIEW_NOTE_LENGTH} characters.` };
  }

  return {
    value: {
      decision,
      note,
      reviewer,
      targetId
    }
  };
}
