import { env, isRemoteQwenEnabled } from '../config/env.js';
import { buildFraudDetectionPrompt } from '../prompts/fraud-detect.js';
import { safeJsonParse } from '../utils/json.js';

function getChatUrl() {
  return new URL(env.qwenChatPath, env.qwenBaseUrl).toString();
}

export async function detectFraudWithQwen(input) {
  if (!isRemoteQwenEnabled()) {
    return {
      available: false,
      reason: 'Remote Qwen endpoint is not configured.'
    };
  }

  const response = await fetch(getChatUrl(), {
    body: JSON.stringify({
      messages: [
        {
          content: '你是一个严格输出 JSON 的诈骗识别模型。',
          role: 'system'
        },
        {
          content: buildFraudDetectionPrompt(input),
          role: 'user'
        }
      ],
      model: env.qwenModel,
      temperature: 0.2
    }),
    headers: {
      Authorization: `Bearer ${env.qwenApiKey}`,
      'Content-Type': 'application/json'
    },
    method: 'POST'
  });

  if (!response.ok) {
    return {
      available: false,
      reason: `Remote Qwen request failed with status ${response.status}.`
    };
  }

  const data = await response.json();
  const content = data?.choices?.[0]?.message?.content;

  if (typeof content !== 'string' || !content.trim()) {
    return {
      available: false,
      reason: 'Remote Qwen response did not contain message content.'
    };
  }

  const parsed = safeJsonParse(content.trim());

  if (!parsed.ok || !parsed.data || typeof parsed.data !== 'object') {
    return {
      available: false,
      reason: 'Remote Qwen response was not valid JSON.'
    };
  }

  return {
    available: true,
    data: parsed.data
  };
}
