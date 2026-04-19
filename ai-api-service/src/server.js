import { getEnv } from './config/env.js';
import { createApp } from './app/create-app.js';

const app = createApp();
const env = getEnv();

try {
  await app.listen({
    host: env.host,
    port: env.port
  });
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
