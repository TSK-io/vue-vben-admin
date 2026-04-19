import { getEnv } from '../config/env.js';

function getClientKey(request) {
  const forwardedFor = request.headers['x-forwarded-for'];
  if (typeof forwardedFor === 'string' && forwardedFor.trim()) {
    return forwardedFor.split(',')[0].trim();
  }

  return request.ip || request.socket?.remoteAddress || 'unknown';
}

function createMemoryStore() {
  const buckets = new Map();

  return {
    consume(key) {
      const now = Date.now();
      const current = buckets.get(key);

      if (!current || current.resetAt <= now) {
        const env = getEnv();
        const next = {
          count: 1,
          resetAt: now + env.rateLimitWindowMs
        };
        buckets.set(key, next);
        return next;
      }

      current.count += 1;
      return current;
    }
  };
}

export function registerRateLimitHook(app) {
  const store = createMemoryStore();

  app.addHook('onRequest', async (request, reply) => {
    if (request.routerPath === '/health' || request.raw.url === '/health') {
      return;
    }

    const key = getClientKey(request);
    const bucket = store.consume(key);
    const env = getEnv();

    reply.header('X-RateLimit-Limit', env.rateLimitMaxRequests);
    reply.header('X-RateLimit-Remaining', Math.max(env.rateLimitMaxRequests - bucket.count, 0));
    reply.header('X-RateLimit-Reset', bucket.resetAt);

    if (bucket.count > env.rateLimitMaxRequests) {
      return reply.code(429).send({
        error: 'Too Many Requests',
        message: 'Rate limit exceeded. Please retry later.'
      });
    }
  });
}
