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
  assert.equal(response.json().data.items.length, 2);

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

test('falls back to rules when remote Qwen returns non-JSON content', async () => {
  process.env.QWEN_BASE_URL = 'https://example.test';
  process.env.QWEN_API_KEY = 'demo-key';

  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        choices: [
          {
            message: {
              content: 'this is not json'
            }
          }
        ]
      }),
      {
        headers: {
          'Content-Type': 'application/json'
        },
        status: 200
      }
    );

  const { createApp: createFallbackApp } = await import(
    `../src/app/create-app.js?fallback=${Date.now()}`
  );
  const app = createFallbackApp();

  const response = await app.inject({
    method: 'POST',
    payload: {
      text: '我是平台客服，请点击链接并提供验证码完成解冻。'
    },
    url: '/api/fraud-detect'
  });

  assert.equal(response.statusCode, 200);
  const payload = response.json();
  assert.equal(payload.data.fallbackUsed, true);
  assert.equal(payload.data.provider, 'rules-fallback');
  assert.equal(payload.data.providerReason, 'Remote Qwen response was not valid JSON.');

  await app.close();
  globalThis.fetch = originalFetch;
  delete process.env.QWEN_BASE_URL;
  delete process.env.QWEN_API_KEY;
});

test('POST /api/fraud-detect/chat-log analyzes chat records', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'POST',
    payload: {
      messages: [
        { role: 'user', text: '你好' },
        { role: 'agent', text: '我是平台客服，请点击链接并提供验证码完成解冻。' }
      ]
    },
    url: '/api/fraud-detect/chat-log'
  });

  assert.equal(response.statusCode, 200);
  assert.equal(response.json().data.suspiciousCount, 1);

  await app.close();
});

test('POST /api/fraud-detect/link analyzes suspicious links', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'POST',
    payload: {
      link: 'http://198.51.100.12/login?redirect=bank'
    },
    url: '/api/fraud-detect/link'
  });

  assert.equal(response.statusCode, 200);
  assert.equal(response.json().data.isFraud, true);

  await app.close();
});

test('POST /api/review stores a manual review record', async () => {
  const app = createApp();
  const response = await app.inject({
    method: 'POST',
    payload: {
      decision: 'needs-follow-up',
      note: '需要二次核验',
      reviewer: 'tester',
      targetId: 'trace-123'
    },
    url: '/api/review'
  });

  assert.equal(response.statusCode, 201);
  assert.equal(response.json().data.reviewer, 'tester');

  await app.close();
});
