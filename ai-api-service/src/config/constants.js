export const RISK_LEVELS = ['low', 'medium', 'high'];
export const PROMPT_VERSION = 'fraud-detect/v1';

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

export const LINK_RISK_PATTERNS = [
  {
    points: 3,
    reason: '链接使用 IP 地址而不是常规域名。',
    test: (url) => /^\d{1,3}(\.\d{1,3}){3}$/.test(url.hostname)
  },
  {
    points: 3,
    reason: '链接使用非常规短链接服务，存在跳转隐藏风险。',
    test: (url) => ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl'].includes(url.hostname)
  },
  {
    points: 2,
    reason: '链接包含登录、验证、重置密码等高风险诱导路径。',
    test: (url) => /(login|verify|reset|secure|wallet|bank|pay)/i.test(url.pathname)
  },
  {
    points: 2,
    reason: '链接包含可疑查询参数，常用于钓鱼跳转或伪造回调。',
    test: (url) => /(redirect|callback|token|verify|account)/i.test(url.search)
  },
  {
    points: 2,
    reason: '链接使用非 HTTPS 协议。',
    test: (url) => url.protocol !== 'https:'
  },
  {
    points: 2,
    reason: '链接域名包含高风险关键词。',
    test: (url) => /(gift|bonus|reward|wallet|support|notice|security|bank)/i.test(url.hostname)
  }
];
