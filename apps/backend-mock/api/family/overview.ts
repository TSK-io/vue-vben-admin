import { eventHandler } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  useResponseSuccess,
} from '~/utils/response';

const MOCK_FAMILY_OVERVIEW = {
  stats: [
    {
      description: '当前已绑定 3 位老人，其中 1 位需要重点关注。',
      key: 'seniors',
      trend: '较上周新增 1 位重点对象',
      value: '3 位',
    },
    {
      description: '近 7 日识别到的风险事件总量。',
      key: 'alerts',
      trend: '较上周下降 12%',
      value: '8 条',
    },
    {
      description: '需要优先电话确认的高风险提醒。',
      key: 'highRisk',
      trend: '其中 2 条仍待家属确认',
      value: '3 条',
    },
    {
      description: '系统与人工提醒后仍需跟进的事件。',
      key: 'pending',
      trend: '包含 1 条社区联动事件',
      value: '2 条',
    },
  ],
  alertTrend: [
    { date: '04-08', total: 1 },
    { date: '04-09', total: 0 },
    { date: '04-10', total: 2 },
    { date: '04-11', total: 1 },
    { date: '04-12', total: 1 },
    { date: '04-13', total: 1 },
    { date: '04-14', total: 2 },
  ],
  riskDistribution: [
    { count: 3, label: '高风险' },
    { count: 3, label: '中风险' },
    { count: 2, label: '低风险' },
  ],
  focusList: [
    {
      currentStatus: '待电话确认',
      elderName: '王阿姨',
      id: 'FOV-5001',
      lastAlertAt: '2026-04-14 09:12',
      riskLevel: 'high',
      riskSummary:
        '收到疑似冒充医保短信，系统建议立即电话联系并提醒不要点击链接。',
    },
    {
      currentStatus: '社区回访中',
      elderName: '周奶奶',
      id: 'FOV-5002',
      lastAlertAt: '2026-04-14 08:45',
      riskLevel: 'high',
      riskSummary: '来电命中“公检法调查”“安全账户”话术，已同步社区值守专员。',
    },
    {
      currentStatus: '已稳定观察',
      elderName: '孙大爷',
      id: 'FOV-5003',
      lastAlertAt: '2026-04-13 18:20',
      riskLevel: 'medium',
      riskSummary: '遇到退款验证码套取场景，已完成解释提醒，建议继续观察一周。',
    },
  ],
};

export default eventHandler(async (event) => {
  const userinfo = verifyAccessToken(event);
  if (!userinfo) {
    return unAuthorizedResponse(event);
  }

  await sleep(250);

  return useResponseSuccess(MOCK_FAMILY_OVERVIEW);
});
