import test from 'node:test';
import assert from 'node:assert/strict';

process.env.LOG_LEVEL = 'silent';

const { createApp } = await import('../src/app/create-app.js');

test('GET /health returns service status', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'GET',
    url: '/health'
  });

  assert.equal(response.statusCode, 200);

  const payload = response.json();
  assert.equal(payload.service, 'ai-api-service');
  assert.equal(payload.status, 'ok');

  await app.close();
});

test('POST /api/fraud-detect validates required text', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'POST',
    payload: {},
    url: '/api/fraud-detect'
  });

  assert.equal(response.statusCode, 400);
  assert.equal(response.json().error, 'Bad Request');

  await app.close();
});

test('POST /api/fraud-detect returns structured fraud result', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'POST',
    payload: {
      source: 'test',
      text: '我是平台客服，请立即点击链接并提供短信验证码解除账户冻结。'
    },
    url: '/api/fraud-detect'
  });

  assert.equal(response.statusCode, 200);

  const payload = response.json();
  assert.equal(payload.data.isFraud, true);
  assert.equal(payload.data.model, 'Qwen2.5-1.5B-Instruct');
  assert.ok(Array.isArray(payload.data.evidence));

  await app.close();
});

test('POST /api/fraud-detect/batch returns results for multiple items', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'POST',
    payload: {
      items: [
        { text: '恭喜中奖，请点击链接领取补贴。' },
        { text: '今天天气不错，我们正常开会。' }
      ]
    },
    url: '/api/fraud-detect/batch'
  });

  assert.equal(response.statusCode, 200);
  assert.equal(response.json().data.length, 2);

  await app.close();
});

test('API token protects non-health endpoints when configured', async () => {
  process.env.API_TOKEN = 'secret-token';
  const { createApp: createProtectedApp } = await import(
    `../src/app/create-app.js?auth=${Date.now()}`
  );
  const app = createProtectedApp();

  const unauthorizedResponse = await app.inject({
    method: 'POST',
    payload: { text: '普通文本' },
    url: '/api/fraud-detect'
  });
  assert.equal(unauthorizedResponse.statusCode, 401);

  const authorizedResponse = await app.inject({
    headers: {
      authorization: 'Bearer secret-token'
    },
    method: 'POST',
    payload: { text: '普通文本' },
    url: '/api/fraud-detect'
  });
  assert.equal(authorizedResponse.statusCode, 200);

  await app.close();
  delete process.env.API_TOKEN;
});

test('rate limit rejects requests after threshold', async () => {
  process.env.RATE_LIMIT_MAX_REQUESTS = '2';
  process.env.RATE_LIMIT_WINDOW_MS = '60000';
  const { createApp: createLimitedApp } = await import(
    `../src/app/create-app.js?rate=${Date.now()}`
  );
  const app = createLimitedApp();

  const request = () =>
    app.inject({
      method: 'POST',
      payload: { text: '普通文本' },
      url: '/api/fraud-detect'
    });

  assert.equal((await request()).statusCode, 200);
  assert.equal((await request()).statusCode, 200);

  const limited = await request();
  assert.equal(limited.statusCode, 429);
  assert.equal(limited.json().error, 'Too Many Requests');

  await app.close();
  delete process.env.RATE_LIMIT_MAX_REQUESTS;
  delete process.env.RATE_LIMIT_WINDOW_MS;
});
