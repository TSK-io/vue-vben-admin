export function safeJsonParse(value) {
  try {
    return { data: JSON.parse(value), ok: true };
  } catch {
    return { data: null, ok: false };
  }
}
