import { detectFraud } from '../services/fraud-detect-service.js';
import {
  validateBatchPayload,
  validateFraudDetectPayload
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
    return {
      data: result
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

    return {
      data: results
    };
  });
}
