<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import { Button, Card, Col, Input, Row, Select, Space, Tag } from 'ant-design-vue';

import { getCommunitySeniorListApi } from '#/api';

defineOptions({ name: 'CommunitySeniors' });

const filters = reactive({ keyword: '', riskLevel: undefined as string | undefined });
const rows = ref<any[]>([]);

const filteredRows = computed(() => rows.value);

async function loadRows() {
  const result = await getCommunitySeniorListApi({
    keyword: filters.keyword || undefined,
    page: 1,
    pageSize: 20,
    riskLevel: filters.riskLevel,
  });
  rows.value = result.items;
}

function resetFilters() {
  filters.keyword = '';
  filters.riskLevel = undefined;
  void loadRows();
}

function getRiskMeta(level: 'high' | 'low' | 'medium') {
  if (level === 'high') return { color: 'red', text: '高风险' };
  if (level === 'medium') return { color: 'orange', text: '中风险' };
  return { color: 'green', text: '低风险' };
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="community-seniors-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 重点对象</p>
        <h1>重点老人</h1>
        <p class="description">当前页面已接真实社区重点老人接口，可按关键词和风险等级筛选。</p>
      </div>
      <div class="hero-note">
        <strong>工作提示</strong>
        <span>高风险对象优先电话回访，必要时联动家属和社区民警。</span>
      </div>
    </section>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Input v-model:value="filters.keyword" allow-clear placeholder="搜索老人、标签或回访状态" style="width: 260px" @press-enter="loadRows" />
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

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in filteredRows" :key="item.id" :lg="12" :span="24">
        <Card class="senior-card" :bordered="false">
          <div class="card-head">
            <div>
              <h3>{{ item.elderName }}</h3>
              <p>{{ item.id }} · {{ item.followUpStatus }}</p>
            </div>
            <Tag :color="getRiskMeta(item.riskLevel).color">{{ getRiskMeta(item.riskLevel).text }}</Tag>
          </div>
          <div class="tag-row">
            <Tag v-for="tag in item.labels" :key="tag" color="blue">{{ tag }}</Tag>
          </div>
          <div class="info-block">
            <p class="label">协同信息</p>
            <p class="value">{{ item.collaboration }}</p>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.community-seniors-page { min-height: 100%; padding: 24px; background: linear-gradient(180deg, #f6fffb 0%, #edfff7 100%); }
.hero-panel,.filter-card,.senior-card { border: 1px solid rgba(16,185,129,.14); border-radius: 24px; background: rgba(255,255,255,.96); box-shadow: 0 16px 36px rgba(6,95,70,.08); }
.hero-panel { display: flex; justify-content: space-between; gap: 20px; padding: 28px 30px; }
.eyebrow { margin: 0 0 12px; color: #059669; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
h1 { margin: 0; color: #065f46; font-size: 34px; }
.description,.hero-note,.value,.card-head p { color: #047857; line-height: 1.8; }
.hero-note { max-width: 280px; padding: 18px; border-radius: 20px; background: #ecfdf5; }
.filter-card,.list-row { margin-top: 18px; }
.card-head { display: flex; justify-content: space-between; gap: 16px; }
.tag-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.info-block { margin-top: 16px; padding: 18px; border-radius: 18px; background: #f0fdf4; }
.label { margin: 0; color: #047857; font-weight: 700; }
@media (max-width: 768px) { .community-seniors-page { padding: 16px; } .hero-panel,.card-head { flex-direction: column; } h1 { font-size: 28px; } }
</style>
