import { eventHandler, getQuery } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  usePageResponseSuccess,
} from '~/utils/response';

interface CommunityWorkorderItem {
  assignee: string;
  createdAt: string;
  elderName: string;
  followUpAction: string;
  id: string;
  latestProgress: string;
  priority: 'high' | 'low' | 'medium';
  riskLevel: 'high' | 'low' | 'medium';
  sourceType: 'call' | 'sms';
  status: 'archived' | 'done' | 'processing' | 'todo';
  title: string;
}

const MOCK_COMMUNITY_WORKORDERS: CommunityWorkorderItem[] = [
  {
    assignee: '网格员 李萍',
    createdAt: '2026-04-14 09:18',
    elderName: '王阿姨',
    followUpAction: '建议 2 小时内电话回访，如未接通则安排上门核查。',
    id: 'WO-7001',
    latestProgress: '系统自动生成工单，等待社区受理。',
    priority: 'high',
    riskLevel: 'high',
    sourceType: 'sms',
    status: 'todo',
    title: '疑似冒充医保短信待核查',
  },
  {
    assignee: '社区民警 周强',
    createdAt: '2026-04-14 08:49',
    elderName: '周奶奶',
    followUpAction: '与家属联合回访，核实是否存在转账或泄露身份信息。',
    id: 'WO-7002',
    latestProgress: '已电话联系家属，正在安排联合处置。',
    priority: 'high',
    riskLevel: 'high',
    sourceType: 'call',
    status: 'processing',
    title: '疑似冒充公检法来电联动处置',
  },
  {
    assignee: '社工 陈晨',
    createdAt: '2026-04-13 18:30',
    elderName: '孙大爷',
    followUpAction: '补充一次防诈宣教，提示退款与验证码类骗局。',
    id: 'WO-7003',
    latestProgress: '已完成首次回访，待录入宣教结果。',
    priority: 'medium',
    riskLevel: 'medium',
    sourceType: 'sms',
    status: 'processing',
    title: '退款验证码风险复访',
  },
  {
    assignee: '网格员 赵敏',
    createdAt: '2026-04-12 16:45',
    elderName: '赵桂兰',
    followUpAction: '本周内完成二次电话确认，视情况决定是否归档。',
    id: 'WO-7004',
    latestProgress: '家属已确认无转账行为，待归档。',
    priority: 'low',
    riskLevel: 'low',
    sourceType: 'call',
    status: 'done',
    title: '熟人冒充来电回访',
  },
  {
    assignee: '社工 郑琪',
    createdAt: '2026-04-11 14:35',
    elderName: '孙大爷',
    followUpAction: '补录处置记录并沉淀为宣教案例。',
    id: 'WO-7005',
    latestProgress: '回访完成并归档，进入案例库整理阶段。',
    priority: 'medium',
    riskLevel: 'medium',
    sourceType: 'sms',
    status: 'archived',
    title: '中奖返利短信归档',
  },
];

function normalizeQueryValue(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default eventHandler(async (event) => {
  const userinfo = verifyAccessToken(event);
  if (!userinfo) {
    return unAuthorizedResponse(event);
  }

  await sleep(300);

  const query = getQuery(event);
  const page = Math.max(
    1,
    Number.parseInt(normalizeQueryValue(query.page) || '1', 10) || 1,
  );
  const pageSize = Math.min(
    20,
    Math.max(
      1,
      Number.parseInt(normalizeQueryValue(query.pageSize) || '5', 10) || 5,
    ),
  );
  const keyword = (normalizeQueryValue(query.keyword) || '').toLowerCase();
  const priority = normalizeQueryValue(query.priority);
  const status = normalizeQueryValue(query.status);

  let listData = structuredClone(MOCK_COMMUNITY_WORKORDERS);

  if (keyword) {
    listData = listData.filter((item) =>
      [item.id, item.title, item.elderName, item.assignee].some((field) =>
        field.toLowerCase().includes(keyword),
      ),
    );
  }

  if (priority) {
    listData = listData.filter((item) => item.priority === priority);
  }

  if (status) {
    listData = listData.filter((item) => item.status === status);
  }

  return usePageResponseSuccess(String(page), String(pageSize), listData);
});
