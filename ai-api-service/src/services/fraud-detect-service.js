import { getEnv } from '../config/env.js';
import { FRAUD_CATEGORIES, RISK_LEVELS } from '../config/constants.js';
import { analyzeTextWithRules } from './fraud-rules.js';
import { detectFraudWithQwen } from './qwen-client.js';

function normalizeModelResult(modelResult, ruleResult) {
  const riskLevel = RISK_LEVELS.includes(modelResult?.riskLevel)
    ? modelResult.riskLevel
    : ruleResult.riskLevel;

  const category = FRAUD_CATEGORIES.includes(modelResult?.category)
    ? modelResult.category
    : ruleResult.category;

  const evidence = Array.isArray(modelResult?.evidence)
    ? modelResult.evidence.filter((item) => typeof item === 'string').slice(0, 6)
    : ruleResult.evidence;

  return {
    category,
    evidence: evidence.length > 0 ? evidence : ruleResult.evidence,
    isFraud:
      typeof modelResult?.isFraud === 'boolean' ? modelResult.isFraud : ruleResult.isFraud,
    reason:
      typeof modelResult?.reason === 'string' && modelResult.reason.trim()
        ? modelResult.reason.trim()
        : ruleResult.reason,
    riskLevel,
    suggestion:
      typeof modelResult?.suggestion === 'string' && modelResult.suggestion.trim()
        ? modelResult.suggestion.trim()
        : ruleResult.suggestion
  };
}

export async function detectFraud(input) {
  const env = getEnv();
  const ruleResult = analyzeTextWithRules(input.text);
  const qwenResult = await detectFraudWithQwen(input);

  if (qwenResult.available) {
    return {
      ...normalizeModelResult(qwenResult.data, ruleResult),
      fallbackUsed: false,
      model: env.qwenModel,
      provider: 'qwen'
    };
  }

  return {
    ...ruleResult,
    fallbackUsed: true,
    model: env.qwenModel,
    provider: 'rules-fallback',
      providerReason: qwenResult.reason
  };
}
