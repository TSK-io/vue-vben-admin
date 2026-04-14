import { eventHandler } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  useResponseSuccess,
} from '~/utils/response';

const MOCK_COMMUNITY_OVERVIEW = {
  stats: [
    {
      description: '辖区内已建档并接入平台的老人基础档案。',
      key: 'seniors',
      trend: '较上月新增 12 位',
      value: '128 位',
    },
    {
      description: '今日需要社区重点介入的高风险事件。',
      key: 'highRisk',
      trend: '其中 2 条已自动生成工单',
      value: '3 条',
    },
    {
      description: '连续告警、独居或高龄等重点关注对象。',
      key: 'focus',
      trend: '较昨日新增 1 位',
      value: '17 位',
    },
    {
      description: '当前尚未办结的回访与处置任务。',
      key: 'workorders',
      trend: '待办 2 条，处理中 1 条',
      value: '3 条',
    },
  ],
  riskTrend: [
    { date: '04-08', highRisk: 1, visits: 1 },
    { date: '04-09', highRisk: 0, visits: 2 },
    { date: '04-10', highRisk: 2, visits: 2 },
    { date: '04-11', highRisk: 1, visits: 1 },
    { date: '04-12', highRisk: 1, visits: 3 },
    { date: '04-13', highRisk: 2, visits: 2 },
    { date: '04-14', highRisk: 3, visits: 2 },
  ],
  focusSeniors: [
    {
      disposalAdvice: '建议今日完成电话回访，必要时安排上门宣教。',
      elderName: '王阿姨',
      id: 'COM-6001',
      lastAlertAt: '2026-04-14 09:12',
      riskLevel: 'high',
      tags: ['高频告警', '独居'],
    },
    {
      disposalAdvice: '已联系家属，建议补充线下走访记录并关注后续来电。',
      elderName: '周奶奶',
      id: 'COM-6002',
      lastAlertAt: '2026-04-14 08:45',
      riskLevel: 'high',
      tags: ['连续两日告警', '需复访'],
    },
    {
      disposalAdvice: '本周内安排一次防诈宣教回访，降低重复验证码风险。',
      elderName: '孙大爷',
      id: 'COM-6003',
      lastAlertAt: '2026-04-13 18:20',
      riskLevel: 'medium',
      tags: ['退款场景', '已提醒'],
    },
  ],
  todoWorkorders: [
    {
      assignee: '网格员 李萍',
      elderName: '王阿姨',
      id: 'WO-7001',
      priority: 'high',
      reason: '高风险短信待上门核查',
      status: 'todo',
    },
    {
      assignee: '社区民警 周强',
      elderName: '周奶奶',
      id: 'WO-7002',
      priority: 'high',
      reason: '疑似冒充公检法来电，需联合处置',
      status: 'processing',
    },
    {
      assignee: '社工 陈晨',
      elderName: '孙大爷',
      id: 'WO-7003',
      priority: 'medium',
      reason: '复盘近期退款验证码风险并补充宣教',
      status: 'todo',
    },
  ],
};

export default eventHandler(async (event) => {
  const userinfo = verifyAccessToken(event);
  if (!userinfo) {
    return unAuthorizedResponse(event);
  }

  await sleep(250);

  return useResponseSuccess(MOCK_COMMUNITY_OVERVIEW);
});
