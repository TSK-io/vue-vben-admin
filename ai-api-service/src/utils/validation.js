const MAX_TEXT_LENGTH = 5000;

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
