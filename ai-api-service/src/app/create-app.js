import Fastify from 'fastify';
import { env } from '../config/env.js';
import { fraudDetectRoutes } from '../routes/fraud-detect.js';
import { healthRoutes } from '../routes/health.js';

export function createApp() {
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

  app.register(healthRoutes);
  app.register(fraudDetectRoutes);

  return app;
}
