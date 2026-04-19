import { randomUUID } from 'node:crypto';
import { getPromptVersion } from '../prompts/version.js';
import { writeAuditLog } from '../services/audit-log-service.js';
import { analyzeChatLog } from '../services/chat-log-service.js';
import { detectFraud } from '../services/fraud-detect-service.js';
import { analyzeLinkRisk } from '../services/link-risk-service.js';
import {
  validateBatchPayload,
  validateChatLogPayload,
  validateFraudDetectPayload,
  validateLinkPayload,
  validateReviewPayload
} from '../utils/validation.js';

function sendValidationError(reply, message) {
  return reply.code(400).send({
    error: 'Bad Request',
    message
  });
}

export async function fraudDetectRoutes(app) {
  app.post('/api/fraud-detect', async (request, reply) => {
    const parsed = validateFraudDetectPayload(request.body);
    if (parsed.error) {
      return sendValidationError(reply, parsed.error);
    }

    const result = await detectFraud(parsed.value);
    const traceId = randomUUID();
    await writeAuditLog({
      createdAt: new Date().toISOString(),
      route: '/api/fraud-detect',
      riskLevel: result.riskLevel,
      traceId,
      type: 'fraud-detect'
    });
    return {
      data: {
        traceId,
        ...result
      }
    };
  });

  app.post('/api/fraud-detect/batch', async (request, reply) => {
    const parsed = validateBatchPayload(request.body);
    if (parsed.error) {
      return sendValidationError(reply, parsed.error);
    }

    const results = [];
    for (const item of parsed.value) {
      results.push(await detectFraud(item));
    }

    const traceId = randomUUID();
    await writeAuditLog({
      createdAt: new Date().toISOString(),
      route: '/api/fraud-detect/batch',
      suspiciousCount: results.filter((item) => item.isFraud).length,
      traceId,
      type: 'fraud-detect-batch'
    });

    return {
      data: {
        items: results,
        promptVersion: getPromptVersion(),
        traceId
      }
    };
  });

  app.post('/api/fraud-detect/chat-log', async (request, reply) => {
    const parsed = validateChatLogPayload(request.body);
    if (parsed.error) {
      return sendValidationError(reply, parsed.error);
    }

    const result = await analyzeChatLog(parsed.value);
    const traceId = randomUUID();
    await writeAuditLog({
      createdAt: new Date().toISOString(),
      route: '/api/fraud-detect/chat-log',
      suspiciousCount: result.suspiciousCount,
      traceId,
      type: 'chat-log-analysis'
    });

    return {
      data: {
        promptVersion: getPromptVersion(),
        traceId,
        ...result
      }
    };
  });

  app.post('/api/fraud-detect/link', async (request, reply) => {
    const parsed = validateLinkPayload(request.body);
    if (parsed.error) {
      return sendValidationError(reply, parsed.error);
    }

    const result = analyzeLinkRisk(parsed.value.link);
    const traceId = randomUUID();
    await writeAuditLog({
      createdAt: new Date().toISOString(),
      normalizedLink: result.normalizedLink,
      route: '/api/fraud-detect/link',
      riskLevel: result.riskLevel,
      traceId,
      type: 'link-risk-analysis'
    });

    return {
      data: {
        decisionMode: 'rules-only',
        promptVersion: getPromptVersion(),
        traceId,
        ...result
      }
    };
  });

  app.post('/api/review', async (request, reply) => {
    const parsed = validateReviewPayload(request.body);
    if (parsed.error) {
      return sendValidationError(reply, parsed.error);
    }

    const reviewId = randomUUID();
    await writeAuditLog({
      createdAt: new Date().toISOString(),
      reviewId,
      ...parsed.value,
      type: 'manual-review'
    });

    return reply.code(201).send({
      data: {
        createdAt: new Date().toISOString(),
        reviewId,
        ...parsed.value
      }
    });
  });
}
