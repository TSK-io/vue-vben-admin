import { LINK_RISK_PATTERNS, RULE_THRESHOLDS } from '../config/constants.js';

function normalizeLink(link) {
  const value = typeof link === 'string' ? link.trim() : '';
  if (!value) return '';

  if (/^https?:\/\//i.test(value)) {
    return value;
  }

  return `https://${value}`;
}

export function analyzeLinkRisk(link) {
  const normalized = normalizeLink(link);

  if (!normalized) {
    return {
      evidence: [],
      isFraud: false,
      normalizedLink: '',
      reason: '未提供有效链接。',
      riskLevel: 'low',
      score: 0,
      suggestion: '请提供需要分析的链接地址。'
    };
  }

  let url;
  try {
    url = new URL(normalized);
  } catch {
    return {
      evidence: [link],
      isFraud: true,
      normalizedLink: normalized,
      reason: '链接格式异常，存在伪造或混淆风险。',
      riskLevel: 'medium',
      score: 5,
      suggestion: '请勿访问该链接，优先通过官方渠道核验地址。'
    };
  }

  const hits = LINK_RISK_PATTERNS.filter((rule) => rule.test(url));
  const score = hits.reduce((sum, item) => sum + item.points, 0);
  const evidence = hits.map((item) => item.reason);

  let riskLevel = 'low';
  if (score >= RULE_THRESHOLDS.high) {
    riskLevel = 'high';
  } else if (score >= RULE_THRESHOLDS.medium) {
    riskLevel = 'medium';
  }

  return {
    evidence,
    isFraud: riskLevel !== 'low',
    normalizedLink: url.toString(),
    reason: hits[0]?.reason || '未发现明显高风险链接特征。',
    riskLevel,
    score,
    suggestion:
      riskLevel === 'low'
        ? '当前未发现明显高风险特征，但仍建议结合发送方身份谨慎访问。'
        : '请勿直接访问该链接，建议通过官方 App 或官网手动输入地址核验。'
  };
}
