export const RISK_LEVELS = ['low', 'medium', 'high'];

export const FRAUD_CATEGORIES = [
  'impersonation-support',
  'task-rebate',
  'fake-investment',
  'prize-subsidy',
  'phishing-link',
  'verification-code',
  'transfer-request',
  'download-app',
  'identity-collection',
  'safe'
];

export const FRAUD_CATEGORY_LABELS = {
  'download-app': '诱导下载陌生 App',
  'fake-investment': '虚假投资理财',
  'identity-collection': '敏感身份信息收集',
  'impersonation-support': '冒充客服或官方',
  'phishing-link': '钓鱼链接',
  'prize-subsidy': '中奖或补贴诱导',
  safe: '未发现明显诈骗特征',
  'task-rebate': '刷单返利',
  'transfer-request': '转账催促',
  'verification-code': '索取验证码'
};

export const RULE_THRESHOLDS = {
  high: 7,
  medium: 4
};
