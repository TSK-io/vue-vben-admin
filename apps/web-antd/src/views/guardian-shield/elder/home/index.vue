<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import PortalPage from '../../shared/portal-page.vue';

import { getBindingListApi, getRiskAlertListApi, getRiskEventViewApi } from '#/api';

const alerts = ref<any[]>([]);
const bindings = ref<any[]>([]);
const riskEvents = ref<any[]>([]);

const heroStats = computed(() => {
  const highRiskCount = alerts.value.filter((item) => item.riskLevel === 'high').length;
  const pendingCount = riskEvents.value.filter((item) => item.status === 'pending').length;
  return [
    {
      title: '今日风险提醒',
      description: `${alerts.value.length} 条提醒，包含 ${highRiskCount} 条高风险事件。`,
    },
    {
      title: '紧急联系人',
      description: `已绑定 ${bindings.value.length} 位家属联系人。`,
    },
    {
      title: '闭环进度',
      description: `${pendingCount} 条事件待继续跟进，已支持查看通知与工单联动。`,
    },
  ];
});

const sections = computed(() => {
  const latestEvent = riskEvents.value[0];
  return [
    {
      title: '风险提醒',
      description: latestEvent
        ? `${latestEvent.alertTitle}，已通知 ${latestEvent.notifiedCount} 次，关联工单 ${latestEvent.workorderCount} 个。`
        : '用更大字号和更少信息密度展示结果，方便快速理解。',
    },
    {
      title: '一键求助',
      description: '求助后可同步通知家属与社区，形成真实留痕。',
    },
    {
      title: '亲属绑定',
      description: `当前可直接查看 ${bindings.value.length} 条真实绑定关系与授权状态。`,
    },
  ];
});

async function loadPageData() {
  const [alertData, bindingData, eventData] = await Promise.all([
    getRiskAlertListApi({ page: 1, pageSize: 10 }),
    getBindingListApi(),
    getRiskEventViewApi(),
  ]);
  alerts.value = alertData.items;
  bindings.value = bindingData;
  riskEvents.value = eventData;
}

onMounted(() => {
  void loadPageData();
});
</script>

<template>
  <PortalPage
    accent="#d97706"
    description="面向老年用户的首页先聚焦三件事：看懂风险、快速求助、及时联系家人。当前版本已联通真实风险提醒、绑定关系和闭环事件统计。"
    role="老年端首页"
    title="守护桑榆，让提醒更简单"
    :hero-stats="heroStats"
    :sections="sections"
  />
</template>
