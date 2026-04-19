export async function healthRoutes(app) {
  app.get('/health', async () => {
    return {
      service: 'ai-api-service',
      status: 'ok',
      timestamp: new Date().toISOString()
    };
  });
}
