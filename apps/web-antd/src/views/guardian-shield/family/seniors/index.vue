<script lang="ts" setup>
import type { FamilySeniorListItem } from '#/api';

import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Empty,
  Input,
  Row,
  Select,
  Space,
  Tag,
} from 'ant-design-vue';

import { getFamilySeniorListApi } from '#/api';

defineOptions({ name: 'FamilySeniors' });

const filters = reactive({
  keyword: '',
  riskLevel: undefined as string | undefined,
});

const loading = ref(false);
const rows = ref<FamilySeniorListItem[]>([]);
const summary = computed(() => ({
  highRiskCount: rows.value.filter((item) => item.riskLevel === 'high').length,
  total: rows.value.length,
}));

function resetFilters() {
  filters.keyword = '';
  filters.riskLevel = undefined;
  void loadRows();
}

async function loadRows() {
  loading.value = true;
  try {
    const data = await getFamilySeniorListApi({
      keyword: filters.keyword || undefined,
      riskLevel: filters.riskLevel,
    });
    rows.value = data.items;
  } finally {
    loading.value = false;
  }
}

function getRiskMeta(level: FamilySeniorListItem['riskLevel']) {
  if (level === 'high') return { color: 'red', text: '高风险' };
  if (level === 'medium') return { color: 'orange', text: '中风险' };
  return { color: 'green', text: '低风险' };
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="family-seniors-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 监护对象</p>
        <h1>老人列表</h1>
        <p class="description">
          这里集中查看已绑定老人、当前风险状态和最近一次告警，方便家属快速确认谁需要优先联系。
        </p>
      </div>
      <div class="hero-note">
        <strong>当前关注</strong>
        <span>
          当前共 {{ summary.total }} 位绑定老人，其中 {{ summary.highRiskCount }}
          位为高风险，建议优先联系。
        </span>
      </div>
    </section>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Input
          v-model:value="filters.keyword"
          allow-clear
          placeholder="搜索老人姓名、关系或最近告警"
          style="width: 260px"
          @press-enter="loadRows"
        />
        <Select
          v-model:value="filters.riskLevel"
          allow-clear
          placeholder="风险等级"
          style="width: 160px"
          :options="[
            { label: '高风险', value: 'high' },
            { label: '中风险', value: 'medium' },
            { label: '低风险', value: 'low' },
          ]"
        />
        <Button type="primary" @click="loadRows">查询</Button>
        <Button @click="resetFilters">重置</Button>
      </Space>
    </Card>

    <Row v-if="rows.length" :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="12" :span="24">
        <Card class="senior-card" :bordered="false" :loading="loading">
          <div class="card-head">
            <div>
              <h3>{{ item.elderName }}</h3>
              <p>{{ item.relation }} · {{ item.bindStatus }} · {{ item.id }}</p>
            </div>
            <Tag :color="getRiskMeta(item.riskLevel).color">
              {{ getRiskMeta(item.riskLevel).text }}
            </Tag>
          </div>
          <div class="info-block">
            <p class="label">最近告警</p>
            <p class="value">{{ item.latestAlertTitle }}</p>
            <p class="subline">{{ item.lastAlert }}</p>
          </div>
          <div class="info-block warning">
            <p class="label">风险状态</p>
            <p class="value">{{ item.riskSummary }}</p>
          </div>
        </Card>
      </Col>
    </Row>
    <Card v-else class="filter-card" :bordered="false" :loading="loading">
      <Empty description="当前筛选条件下暂无绑定老人或风险数据" />
    </Card>
  </div>
</template>

<style scoped>
.family-seniors-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(220 38 38 / 10%), transparent 28%),
    linear-gradient(180deg, #fff8f8 0%, #fff1f2 100%);
}

.hero-panel,
.filter-card,
.senior-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(244 63 94 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(136 19 55 / 8%);
}

.hero-panel {
  display: flex;
  gap: 20px;
  justify-content: space-between;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #e11d48;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #881337;
}

.description {
  margin: 16px 0 0;
  line-height: 1.8;
  color: #9f1239;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  line-height: 1.8;
  color: #9f1239;
  background: #fff1f2;
  border-radius: 20px;
}

.filter-card,
.list-row {
  margin-top: 18px;
}

.card-head {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.card-head h3 {
  margin: 0;
  color: #881337;
}

.card-head p,
.subline {
  margin: 8px 0 0;
  color: #9f1239;
}

.info-block {
  padding: 18px;
  margin-top: 16px;
  background: #fff7f8;
  border-radius: 18px;
}

.warning {
  background: #fff1f2;
}

.label {
  margin: 0;
  font-weight: 700;
  color: #be123c;
}

.value {
  margin: 10px 0 0;
  font-size: 17px;
  line-height: 1.8;
  color: #881337;
}

@media (max-width: 768px) {
  .family-seniors-page {
    padding: 16px;
  }

  .hero-panel,
  .card-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
