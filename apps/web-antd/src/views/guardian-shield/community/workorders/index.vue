<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import { Button, Card, Col, Empty, Input, List, Row, Select, Space, Tag } from 'ant-design-vue';

import { getCommunityWorkorderListApi } from '#/api';
import type { CommunityWorkorderListItem } from '#/api';

defineOptions({ name: 'CommunityWorkorders' });

const loading = ref(false);
const rows = ref<CommunityWorkorderListItem[]>([]);
const total = ref(0);

const filters = reactive({
  keyword: '',
  page: 1,
  pageSize: 5,
  priority: undefined as string | undefined,
  status: undefined as string | undefined,
});

const priorityMap: Record<
  CommunityWorkorderListItem['priority'],
  { color: string; text: string }
> = {
  high: { color: 'red', text: '高优先级' },
  low: { color: 'green', text: '低优先级' },
  medium: { color: 'orange', text: '中优先级' },
};

const riskMap: Record<
  CommunityWorkorderListItem['riskLevel'],
  { color: string; text: string }
> = {
  high: { color: 'red', text: '高风险' },
  low: { color: 'green', text: '低风险' },
  medium: { color: 'orange', text: '中风险' },
};

const sourceTextMap: Record<CommunityWorkorderListItem['sourceType'], string> = {
  call: '通话识别',
  sms: '短信识别',
};

const statusTextMap: Record<CommunityWorkorderListItem['status'], string> = {
  archived: '已归档',
  done: '待归档',
  processing: '处理中',
  todo: '待受理',
};

const summaryCards = computed(() => [
  {
    description: '当前筛选条件下的工单总数。',
    title: '工单总数',
    value: `${total.value}`,
  },
  {
    description: '优先需要社区立即介入的事件。',
    title: '高优先级',
    value: `${rows.value.filter((item) => item.priority === 'high').length}`,
  },
  {
    description: '仍在电话回访、联动核查或宣教中的工单。',
    title: '处理中',
    value: `${rows.value.filter((item) => item.status === 'processing').length}`,
  },
  {
    description: '已完成处置、等待归档沉淀的事件。',
    title: '待归档',
    value: `${rows.value.filter((item) => item.status === 'done').length}`,
  },
]);

function getPriorityMeta(priority: CommunityWorkorderListItem['priority']) {
  return priorityMap[priority];
}

function getRiskMeta(riskLevel: CommunityWorkorderListItem['riskLevel']) {
  return riskMap[riskLevel];
}

function getSourceLabel(sourceType: CommunityWorkorderListItem['sourceType']) {
  return sourceTextMap[sourceType];
}

function getStatusLabel(status: CommunityWorkorderListItem['status']) {
  return statusTextMap[status];
}

async function loadRows() {
  loading.value = true;
  try {
    const data = await getCommunityWorkorderListApi({
      keyword: filters.keyword || undefined,
      page: filters.page,
      pageSize: filters.pageSize,
      priority: filters.priority,
      status: filters.status,
    });
    rows.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  filters.page = 1;
  void loadRows();
}

function handleReset() {
  filters.keyword = '';
  filters.page = 1;
  filters.pageSize = 5;
  filters.priority = undefined;
  filters.status = undefined;
  void loadRows();
}

function handlePageChange(page: number, pageSize: number) {
  filters.page = page;
  filters.pageSize = pageSize;
  void loadRows();
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="community-workorders-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 协同处置</p>
        <h1>风险工单</h1>
        <p class="description">
          当前页面已经接入真实 mock 工单数据，可按关键词、优先级和状态筛选，便于社区快速查看待受理、处理中和待归档事件。
        </p>
      </div>
      <div class="hero-note">
        <strong>处置提醒</strong>
        <span>高风险工单优先联系家属并核实老人状态，关键节点同步留痕。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="6" :md="12" :span="24">
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Input
          v-model:value="filters.keyword"
          allow-clear
          placeholder="搜索工单编号、标题、老人或处理人"
          style="width: 280px"
          @press-enter="handleSearch"
        />
        <Select
          v-model:value="filters.priority"
          allow-clear
          placeholder="优先级"
          style="width: 150px"
          :options="[
            { label: '高优先级', value: 'high' },
            { label: '中优先级', value: 'medium' },
            { label: '低优先级', value: 'low' },
          ]"
        />
        <Select
          v-model:value="filters.status"
          allow-clear
          placeholder="状态"
          style="width: 150px"
          :options="[
            { label: '待受理', value: 'todo' },
            { label: '处理中', value: 'processing' },
            { label: '待归档', value: 'done' },
            { label: '已归档', value: 'archived' },
          ]"
        />
        <Button type="primary" @click="handleSearch">查询</Button>
        <Button @click="handleReset">重置</Button>
      </Space>
    </Card>

    <Card class="list-card" :bordered="false">
      <List
        v-if="rows.length"
        :data-source="rows"
        :loading="loading"
        :pagination="{
          current: filters.page,
          pageSize: filters.pageSize,
          total,
          onChange: handlePageChange,
        }"
      >
        <template #renderItem="{ item }">
          <List.Item class="workorder-item">
            <div class="workorder-header">
              <div>
                <h3>{{ item.title }}</h3>
                <p class="subline">
                  {{ item.id }} · {{ item.elderName }} · {{ item.assignee }} · {{ item.createdAt }}
                </p>
              </div>
              <Space wrap>
                <Tag :color="getPriorityMeta(item.priority).color">
                  {{ getPriorityMeta(item.priority).text }}
                </Tag>
                <Tag :color="getRiskMeta(item.riskLevel).color">
                  {{ getRiskMeta(item.riskLevel).text }}
                </Tag>
                <Tag color="blue">{{ getSourceLabel(item.sourceType) }}</Tag>
                <Tag>{{ getStatusLabel(item.status) }}</Tag>
              </Space>
            </div>

            <Row :gutter="[16, 16]">
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">最新进展</p>
                  <p class="info-text">{{ item.latestProgress }}</p>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card action-card">
                  <p class="info-label">建议动作</p>
                  <p class="info-text">{{ item.followUpAction }}</p>
                </div>
              </Col>
            </Row>
          </List.Item>
        </template>
      </List>
      <Empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE" description="当前条件下暂无工单" />
    </Card>
  </div>
</template>

<style scoped>
.community-workorders-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(194, 65, 12, 0.14), transparent 28%),
    linear-gradient(180deg, #fffaf7 0%, #fff1e8 100%);
}

.hero-panel,
.summary-card,
.filter-card,
.list-card,
.info-card {
  border: 1px solid rgba(253, 186, 116, 0.75);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18px 40px rgba(194, 65, 12, 0.08);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #c2410c;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #7c2d12;
  font-size: 30px;
}

.description,
.summary-desc,
.subline,
.info-text {
  color: #7c5e4f;
  line-height: 1.75;
}

.hero-note {
  max-width: 320px;
  padding: 18px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #fed7aa 0%, #ffedd5 100%);
  color: #9a3412;
}

.hero-note strong,
.summary-value,
.workorder-header h3 {
  display: block;
  color: #7c2d12;
}

.summary-row {
  margin-bottom: 16px;
}

.summary-title {
  margin: 0;
  color: #9a3412;
}

.summary-value {
  margin-top: 18px;
  font-size: 30px;
}

.summary-desc {
  margin: 12px 0 0;
}

.filter-card {
  margin-bottom: 16px;
}

.workorder-item {
  padding: 8px 0;
}

.workorder-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.workorder-header h3 {
  margin: 0;
  font-size: 18px;
}

.subline {
  margin: 8px 0 0;
}

.info-card {
  height: 100%;
  padding: 18px 20px;
}

.action-card {
  background: linear-gradient(135deg, #fff7ed 0%, #fffbeb 100%);
}

.info-label {
  margin: 0;
  color: #9a3412;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.info-text {
  margin: 10px 0 0;
}

@media (max-width: 992px) {
  .hero-panel,
  .workorder-header {
    flex-direction: column;
  }

  .hero-note {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .community-workorders-page {
    padding: 16px;
  }

  .hero-panel {
    padding: 22px;
  }

  h1 {
    font-size: 26px;
  }
}
</style>
