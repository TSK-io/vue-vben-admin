import Fastify from 'fastify';
import { getEnv } from '../config/env.js';
import { registerAuthHook } from '../plugins/auth.js';
import { registerRateLimitHook } from '../plugins/rate-limit.js';
import { fraudDetectRoutes } from '../routes/fraud-detect.js';
import { healthRoutes } from '../routes/health.js';

export function createApp() {
  const env = getEnv();
  const app = Fastify({
    logger: {
      level: env.logLevel
    }
  });

  app.setErrorHandler((error, _request, reply) => {
    app.log.error(error);
    reply.code(500).send({
      error: 'Internal Server Error',
      message: 'Unexpected server error.'
    });
  });

  registerAuthHook(app);
  registerRateLimitHook(app);
  app.register(healthRoutes);
  app.register(fraudDetectRoutes);

  return app;
}
