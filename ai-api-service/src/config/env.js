function readEnv(name, fallback = '') {
  return process.env[name]?.trim() || fallback;
}

function readNumber(name, fallback) {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function getEnv() {
  return {
    apiToken: readEnv('API_TOKEN'),
    host: readEnv('HOST', '0.0.0.0'),
    logLevel: readEnv('LOG_LEVEL', 'info'),
    port: readNumber('PORT', 3001),
    rateLimitMaxRequests: readNumber('RATE_LIMIT_MAX_REQUESTS', 30),
    rateLimitWindowMs: readNumber('RATE_LIMIT_WINDOW_MS', 60_000),
    qwenApiKey: readEnv('QWEN_API_KEY'),
    qwenBaseUrl: readEnv('QWEN_BASE_URL'),
    qwenChatPath: readEnv('QWEN_CHAT_PATH', '/chat/completions'),
    qwenModel: readEnv('QWEN_MODEL', 'Qwen2.5-1.5B-Instruct')
  };
}

export function isRemoteQwenEnabled() {
  const env = getEnv();
  return Boolean(env.qwenBaseUrl && env.qwenApiKey);
}

export function isApiTokenEnabled() {
  const env = getEnv();
  return Boolean(env.apiToken);
}
