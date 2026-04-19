import {
  FRAUD_CATEGORY_LABELS,
  RULE_THRESHOLDS
} from '../config/constants.js';

const RULES = [
  {
    category: 'impersonation-support',
    points: 3,
    patterns: ['客服', '官方', '平台工作人员', '账户异常', '账户冻结', '解除限制'],
    reason: '文本出现冒充客服或平台官方处理问题的话术。'
  },
  {
    category: 'task-rebate',
    points: 3,
    patterns: ['刷单', '返利', '做任务', '垫付', '佣金', '兼职轻松赚钱'],
    reason: '文本出现刷单返利或垫资任务相关诱导。'
  },
  {
    category: 'fake-investment',
    points: 3,
    patterns: ['内幕消息', '稳赚不赔', '高收益', '带单', '投资群', '数字货币投资'],
    reason: '文本出现高收益投资或带单诱导。'
  },
  {
    category: 'prize-subsidy',
    points: 2,
    patterns: ['中奖', '补贴', '领取奖金', '领取补助', '奖学金到账', '免费领取'],
    reason: '文本出现中奖或补贴诱导。'
  },
  {
    category: 'phishing-link',
    points: 3,
    patterns: ['http://', 'https://', '点击链接', '登录验证', '立即验证', '专属链接'],
    reason: '文本含有可疑链接或点击验证诱导。'
  },
  {
    category: 'verification-code',
    points: 3,
    patterns: ['验证码', '短信码', '动态码', '报给我', '发我验证码'],
    reason: '文本存在索取验证码的风险信号。'
  },
  {
    category: 'transfer-request',
    points: 3,
    patterns: ['转账', '汇款', '打款', '先付款', '保证金', '解冻金'],
    reason: '文本存在资金转移或先付款要求。'
  },
  {
    category: 'download-app',
    points: 2,
    patterns: ['下载 App', '安装软件', '屏幕共享', '远程协助', '会议软件', '安装链接'],
    reason: '文本诱导下载陌生软件或开启远程协助。'
  },
  {
    category: 'identity-collection',
    points: 2,
    patterns: ['身份证', '银行卡', '卡号', '人脸识别', '实名信息', '支付密码'],
    reason: '文本要求提交敏感身份或支付信息。'
  }
];

function collectMatches(text, patterns) {
  return patterns.filter((pattern) => text.includes(pattern));
}

export function analyzeTextWithRules(text) {
  const matchedRules = [];

  for (const rule of RULES) {
    const matches = collectMatches(text, rule.patterns);
    if (matches.length > 0) {
      matchedRules.push({
        ...rule,
        matches
      });
    }
  }

  const score = matchedRules.reduce((sum, rule) => sum + rule.points, 0);
  const topRule = matchedRules.sort((a, b) => b.points - a.points)[0];
  const evidence = [...new Set(matchedRules.flatMap((rule) => rule.matches))].slice(0, 6);

  let riskLevel = 'low';
  if (score >= RULE_THRESHOLDS.high) {
    riskLevel = 'high';
  } else if (score >= RULE_THRESHOLDS.medium) {
    riskLevel = 'medium';
  }

  const isFraud = matchedRules.length > 0 && riskLevel !== 'low'
    ? true
    : matchedRules.some((rule) =>
        ['verification-code', 'transfer-request', 'fake-investment'].includes(rule.category)
      );

  const category = topRule?.category || 'safe';

  const reason = topRule
    ? topRule.reason
    : '未命中明显诈骗关键词或高风险规则。';

  const suggestion = isFraud
    ? '请勿转账、勿点击陌生链接、勿透露验证码，必要时联系官方渠道核实。'
    : '当前未发现明显诈骗特征，但仍建议结合上下文保持警惕。';

  return {
    category,
    categoryLabel: FRAUD_CATEGORY_LABELS[category],
    evidence,
    isFraud,
    reason,
    riskLevel,
    score,
    suggestion
  };
}
