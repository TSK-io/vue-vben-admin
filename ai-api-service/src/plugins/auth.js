import { getEnv, isApiTokenEnabled } from '../config/env.js';

function extractBearerToken(headerValue) {
  if (!headerValue || typeof headerValue !== 'string') {
    return '';
  }

  const [scheme, token] = headerValue.split(' ');
  if (scheme !== 'Bearer' || !token) {
    return '';
  }

  return token.trim();
}

export function registerAuthHook(app) {
  app.addHook('onRequest', async (request, reply) => {
    if (request.routerPath === '/health' || request.raw.url === '/health') {
      return;
    }

    if (!isApiTokenEnabled()) {
      return;
    }

    const env = getEnv();
    const token = extractBearerToken(request.headers.authorization);

    if (token !== env.apiToken) {
      return reply.code(401).send({
        error: 'Unauthorized',
        message: 'A valid Bearer token is required.'
      });
    }
  });
}
