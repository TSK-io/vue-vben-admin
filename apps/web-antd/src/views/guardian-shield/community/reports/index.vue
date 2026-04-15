<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { CommunityReportView } from '#/api';

import { computed, onMounted, ref } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { Button, Card, Col, Row, Statistic, Table, Tag } from 'ant-design-vue';

import { getCommunityReportViewApi } from '#/api';

defineOptions({ name: 'CommunityReports' });

const loading = ref(false);
const report = ref<CommunityReportView | null>(null);

const riskChartRef = ref<EchartsUIType>();
const workorderChartRef = ref<EchartsUIType>();
const trendChartRef = ref<EchartsUIType>();

const { renderEcharts: renderRiskChart } = useEcharts(riskChartRef);
const { renderEcharts: renderWorkorderChart } = useEcharts(workorderChartRef);
const { renderEcharts: renderTrendChart } = useEcharts(trendChartRef);

const statCards = computed(() => {
  if (!report.value) {
    return [];
  }
  return [
    {
      label: '平均处置时效',
      suffix: '分钟',
      value: report.value.disposalAvgMinutes,
    },
    {
      label: '计划覆盖人数',
      suffix: '人',
      value:
        report.value.educationCoverage.find((item) => item.label === '计划覆盖')
          ?.value || 0,
    },
    {
      label: '实际宣教触达',
      suffix: '人',
      value:
        report.value.educationCoverage.find((item) => item.label === '实际触达')
          ?.value || 0,
    },
    {
      label: '回访反馈人数',
      suffix: '人',
      value:
        report.value.educationCoverage.find((item) => item.label === '到访反馈')
          ?.value || 0,
    },
  ];
});

function setCharts() {
  if (!report.value) {
    return;
  }
  void renderRiskChart({
    color: ['#dc2626', '#f59e0b', '#22c55e'],
    series: [
      {
        data: report.value.riskByLevel.map((item) => ({
          name: item.label,
          value: item.value,
        })),
        radius: ['45%', '72%'],
        type: 'pie',
      },
    ],
    tooltip: { trigger: 'item' },
  });
  void renderWorkorderChart({
    color: ['#2563eb'],
    grid: { bottom: 24, left: 36, right: 16, top: 16 },
    series: [
      {
        barWidth: 26,
        data: report.value.workorderStatus.map((item) => item.value),
        type: 'bar',
      },
    ],
    xAxis: {
      data: report.value.workorderStatus.map((item) => item.label),
      type: 'category',
    },
    yAxis: { type: 'value' },
  });
  void renderTrendChart({
    color: ['#0f766e'],
    grid: { bottom: 24, left: 36, right: 16, top: 16 },
    series: [
      {
        areaStyle: { color: 'rgb(20 184 166 / 18%)' },
        data: report.value.monthlyTrends.map((item) => item.value),
        smooth: true,
        type: 'line',
      },
    ],
    xAxis: {
      data: report.value.monthlyTrends.map((item) => item.label),
      type: 'category',
    },
    yAxis: { type: 'value' },
  });
}

async function loadReport() {
  loading.value = true;
  try {
    report.value = await getCommunityReportViewApi();
    setCharts();
  } finally {
    loading.value = false;
  }
}

function downloadCsv() {
  if (!report.value || typeof window === 'undefined') {
    return;
  }
  const blob = new Blob([`\uFEFF${report.value.exportPayload.csv}`], {
    type: 'text/csv;charset=utf-8;',
  });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = report.value.exportPayload.fileName;
  link.click();
  URL.revokeObjectURL(link.href);
}

function rankColumns(title: string) {
  return [
    {
      customRender: ({ index }: { index: number }) => index + 1,
      key: 'rank',
      title: '排名',
      width: 72,
    },
    {
      dataIndex: 'label',
      key: 'label',
      title,
    },
    {
      dataIndex: 'value',
      key: 'value',
      title: '数值',
      width: 100,
    },
  ];
}

function tagColor(label: string) {
  if (label === 'high') return 'error';
  if (label === 'medium') return 'warning';
  if (label === 'low') return 'success';
  return 'processing';
}

onMounted(async () => {
  await loadReport();
});
</script>

<template>
  <div class="community-reports-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 统计报表</p>
        <h1>统计报表</h1>
        <p class="description">
          已整合风险、工单和宣教数据，支持趋势图、排行图、处置时效、覆盖统计和 CSV 导出。
        </p>
      </div>
      <Button type="primary" @click="downloadCsv">导出报表</Button>
    </section>

    <Row :gutter="[16, 16]" class="stats-row">
      <Col v-for="item in statCards" :key="item.label" :lg="6" :span="24">
        <Card class="stat-card" :bordered="false">
          <Statistic :title="item.label" :value="item.value" :suffix="item.suffix" />
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="charts-row">
      <Col :lg="8" :span="24">
        <Card class="report-card" :bordered="false" title="风险等级分布">
          <EchartsUI ref="riskChartRef" style="height: 280px" />
          <div class="legend-list">
            <span v-for="item in report?.riskByLevel || []" :key="item.label">
              <Tag :color="tagColor(item.label)">{{ item.label }}</Tag>
              {{ item.value }}
            </span>
          </div>
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="report-card" :bordered="false" title="工单状态排行">
          <EchartsUI ref="workorderChartRef" style="height: 280px" />
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="report-card" :bordered="false" title="社区行动趋势">
          <EchartsUI ref="trendChartRef" style="height: 280px" />
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="tables-row">
      <Col :lg="8" :span="24">
        <Card class="report-card" :bordered="false" title="宣教覆盖统计">
          <div class="coverage-list">
            <article
              v-for="item in report?.educationCoverage || []"
              :key="item.label"
              class="coverage-item"
            >
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </article>
          </div>
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="report-card" :bordered="false" title="高频宣教分类排行">
          <Table
            :columns="rankColumns('分类')"
            :data-source="report?.topCategories || []"
            :loading="loading"
            :pagination="false"
            row-key="label"
            size="small"
          />
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="report-card" :bordered="false" title="重点跟进老人排行">
          <Table
            :columns="rankColumns('老人姓名')"
            :data-source="report?.topSeniors || []"
            :loading="loading"
            :pagination="false"
            row-key="label"
            size="small"
          />
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.community-reports-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(191 219 254 / 55%), transparent 30%),
    linear-gradient(180deg, #f8fbff 0%, #eaf2ff 100%);
}

.hero-panel,
.stat-card,
.report-card {
  background: rgb(255 255 255 / 95%);
  border: 1px solid rgb(30 64 175 / 12%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(30 64 175 / 10%);
}

.hero-panel {
  display: flex;
  gap: 16px;
  justify-content: space-between;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #1d4ed8;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #1e3a8a;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  color: #475569;
  line-height: 1.8;
}

.stats-row,
.charts-row,
.tables-row {
  margin-top: 18px;
}

.legend-list,
.coverage-list {
  display: grid;
  gap: 12px;
}

.legend-list {
  margin-top: 12px;
}

.coverage-item {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 16px 18px;
  background: #eff6ff;
  border: 1px solid rgb(96 165 250 / 20%);
  border-radius: 18px;
}

.coverage-item strong {
  color: #1e3a8a;
  font-size: 28px;
}

.coverage-item span {
  color: #64748b;
}

@media (max-width: 768px) {
  .community-reports-page {
    padding: 16px;
  }

  .hero-panel {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
