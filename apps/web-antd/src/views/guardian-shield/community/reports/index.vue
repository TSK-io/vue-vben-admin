<script lang="ts" setup>
import { onMounted, ref } from 'vue';

import { Card, Col, Row } from 'ant-design-vue';

import { getCommunityReportApi } from '#/api';

defineOptions({ name: 'CommunityReports' });

const report = ref<any>(null);

onMounted(async () => {
  report.value = await getCommunityReportApi();
});
</script>

<template>
  <div class="community-reports-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 统计报表</p>
        <h1>统计报表</h1>
        <p class="description">报表页已接真实统计接口，展示风险分布、工单状态、宣教内容和平均处置时效。</p>
      </div>
    </section>
    <Row :gutter="[16, 16]" class="list-row">
      <Col :lg="8" :span="24"><Card class="report-card" title="风险分布" :bordered="false"><p v-for="item in report?.risk_by_level || []" :key="item.label">{{ item.label }}：{{ item.count }}</p></Card></Col>
      <Col :lg="8" :span="24"><Card class="report-card" title="工单状态" :bordered="false"><p v-for="item in report?.workorder_status || []" :key="item.label">{{ item.label }}：{{ item.count }}</p></Card></Col>
      <Col :lg="8" :span="24"><Card class="report-card" title="宣教内容" :bordered="false"><p v-for="item in report?.education_summary || []" :key="item.label">{{ item.label }}：{{ item.count }}</p></Card></Col>
    </Row>
    <Card class="report-card" :bordered="false" title="处置时效" style="margin-top: 16px">
      <strong class="minutes">{{ report?.disposal_avg_minutes || 0 }} 分钟</strong>
    </Card>
  </div>
</template>

<style scoped>
.community-reports-page { min-height: 100%; padding: 24px; background: linear-gradient(180deg, #f6fbff 0%, #edf4ff 100%); }
.hero-panel,.report-card { border: 1px solid rgba(29,78,216,.14); border-radius: 24px; background: rgba(255,255,255,.96); box-shadow: 0 16px 36px rgba(30,64,175,.08); }
.hero-panel { padding: 28px 30px; }
.eyebrow { margin: 0 0 12px; color: #1d4ed8; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
h1 { margin: 0; color: #1e3a8a; font-size: 34px; }
.description,.report-card p { color: #334155; line-height: 1.8; }
.list-row { margin-top: 18px; }
.minutes { font-size: 32px; color: #1e3a8a; }
@media (max-width: 768px) { .community-reports-page { padding: 16px; } h1 { font-size: 28px; } }
</style>
