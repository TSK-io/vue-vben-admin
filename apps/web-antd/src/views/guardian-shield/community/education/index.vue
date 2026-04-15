<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Modal,
  Progress,
  Row,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  message,
} from 'ant-design-vue';

import type {
  CommunityEducationContentItem,
  CommunityEducationPlan,
} from '#/api';

import {
  deleteCommunityEducationPlanApi,
  getCommunityEducationLibraryApi,
  getCommunityEducationOverviewApi,
  saveCommunityEducationPlanApi,
} from '#/api';

defineOptions({ name: 'CommunityEducation' });

const loading = ref(false);
const library = ref<CommunityEducationContentItem[]>([]);
const plans = ref<CommunityEducationPlan[]>([]);
const recentFeedback = ref<
  Array<{
    contentTitle: string;
    feedbackNote: string;
    id: string;
    plannedAt: string;
    reachCount: number;
    targetGroup: string;
    visitCount: number;
  }>
>([]);
const modalOpen = ref(false);
const editingPlanId = ref<string>();

const filters = reactive({
  category: '',
  keyword: '',
  status: '',
});

const formState = reactive({
  channel: 'article',
  contentId: '',
  coverageGoal: 100,
  feedbackNote: '',
  plannedAt: '',
  pushScope: 'all',
  reachCount: 0,
  status: 'scheduled' as CommunityEducationPlan['status'],
  targetCommunity: '东湖社区',
  targetGroup: '老人用户',
  visitCount: 0,
});

const heroStats = ref([
  { label: '内容素材', value: 0, suffix: '条' },
  { label: '进行中计划', value: 0, suffix: '项' },
  { label: '已发布内容', value: 0, suffix: '条' },
  { label: '反馈转化率', value: 0, suffix: '%' },
]);

const contentOptions = computed(() =>
  library.value.map((item) => ({
    label: `${item.title} · ${item.category}`,
    value: item.id,
  })),
);

const selectedContent = computed(() =>
  library.value.find((item) => item.id === formState.contentId),
);

async function loadData() {
  loading.value = true;
  try {
    library.value = await getCommunityEducationLibraryApi(filters);
    const overview = await getCommunityEducationOverviewApi();
    plans.value = overview.plans;
    recentFeedback.value = overview.recentFeedback;
    heroStats.value = [
      { label: '内容素材', value: overview.contentCount, suffix: '条' },
      { label: '进行中计划', value: overview.activeCount, suffix: '项' },
      { label: '已发布内容', value: overview.publishedCount, suffix: '条' },
      { label: '反馈转化率', value: overview.feedbackRate, suffix: '%' },
    ];
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  editingPlanId.value = undefined;
  Object.assign(formState, {
    channel: 'article',
    contentId: library.value[0]?.id || '',
    coverageGoal: 100,
    feedbackNote: '',
    plannedAt: new Date(Date.now() + 86400000).toISOString().slice(0, 16),
    pushScope: 'all',
    reachCount: 0,
    status: 'scheduled',
    targetCommunity: '东湖社区',
    targetGroup: '老人用户',
    visitCount: 0,
  });
}

function openCreate() {
  resetForm();
  modalOpen.value = true;
}

function openEdit(plan: CommunityEducationPlan) {
  editingPlanId.value = plan.id;
  Object.assign(formState, {
    channel: plan.channel,
    contentId: plan.contentId,
    coverageGoal: plan.coverageGoal,
    feedbackNote: plan.feedbackNote,
    plannedAt: plan.plannedAt.slice(0, 16),
    pushScope: plan.pushScope,
    reachCount: plan.reachCount,
    status: plan.status,
    targetCommunity: plan.targetCommunity,
    targetGroup: plan.targetGroup,
    visitCount: plan.visitCount,
  });
  modalOpen.value = true;
}

async function submitPlan() {
  if (!formState.contentId) {
    message.warning('请先选择宣教内容');
    return;
  }
  await saveCommunityEducationPlanApi({
    channel: formState.channel,
    contentId: formState.contentId,
    contentTitle: selectedContent.value?.title || '未命名内容',
    coverageGoal: Number(formState.coverageGoal || 0),
    feedbackNote: formState.feedbackNote,
    id: editingPlanId.value,
    plannedAt: new Date(formState.plannedAt).toISOString(),
    pushScope: formState.pushScope,
    reachCount: Number(formState.reachCount || 0),
    status: formState.status,
    targetCommunity: formState.targetCommunity,
    targetGroup: formState.targetGroup,
    visitCount: Number(formState.visitCount || 0),
  });
  message.success(editingPlanId.value ? '宣教计划已更新' : '宣教计划已创建');
  modalOpen.value = false;
  await loadData();
}

async function removePlan(planId: string) {
  await deleteCommunityEducationPlanApi(planId);
  message.success('计划已删除');
  await loadData();
}

function getPlanProgress(plan: CommunityEducationPlan) {
  if (plan.coverageGoal <= 0) {
    return 0;
  }
  return Math.min(100, Math.round((plan.reachCount / plan.coverageGoal) * 100));
}

onMounted(async () => {
  await loadData();
  if (!formState.contentId && library.value.length > 0) {
    formState.contentId = library.value[0]?.id || '';
  }
});
</script>

<template>
  <div class="community-education-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 宣教管理</p>
        <h1>宣教管理</h1>
        <p class="description">
          已接后台内容库，支持社区按人群和计划时间安排宣教投放，并沉淀触达与走访反馈。
        </p>
      </div>
      <Button type="primary" @click="openCreate">新建宣传计划</Button>
    </section>

    <Row :gutter="[16, 16]" class="stats-row">
      <Col v-for="item in heroStats" :key="item.label" :lg="6" :span="24">
        <Card class="stat-card" :bordered="false">
          <Statistic :title="item.label" :value="item.value" :suffix="item.suffix" />
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="14" :span="24">
        <Card class="content-card" :bordered="false" title="宣教内容库">
          <Space wrap class="toolbar">
            <Input
              v-model:value="filters.keyword"
              allow-clear
              placeholder="搜索标题、摘要或分类"
              style="width: 220px"
            />
            <Select
              v-model:value="filters.category"
              allow-clear
              placeholder="分类"
              style="width: 160px"
              :options="
                [...new Set(library.map((item) => item.category))].map((item) => ({
                  label: item,
                  value: item,
                }))
              "
            />
            <Select
              v-model:value="filters.status"
              allow-clear
              placeholder="状态"
              style="width: 140px"
              :options="[
                { label: '草稿', value: 'draft' },
                { label: '已发布', value: 'published' },
              ]"
            />
            <Button @click="loadData">筛选</Button>
          </Space>

          <div class="library-list">
            <article v-for="item in library" :key="item.id" class="library-item">
              <div class="library-head">
                <div>
                  <h3>{{ item.title }}</h3>
                  <p>{{ item.summary }}</p>
                </div>
                <Space wrap>
                  <Tag color="blue">{{ item.category }}</Tag>
                  <Tag color="green">{{ item.audience }}</Tag>
                  <Tag :color="item.status === 'published' ? 'success' : 'warning'">
                    {{ item.status }}
                  </Tag>
                </Space>
              </div>
              <div class="library-meta">
                <span>投放渠道：{{ item.channel }}</span>
                <span>更新时间：{{ item.updatedAt }}</span>
              </div>
            </article>
          </div>
        </Card>
      </Col>

      <Col :lg="10" :span="24">
        <Card class="content-card" :bordered="false" title="效果反馈">
          <div class="feedback-list">
            <article
              v-for="item in recentFeedback"
              :key="item.id"
              class="feedback-item"
            >
              <div class="feedback-top">
                <strong>{{ item.contentTitle }}</strong>
                <span>{{ item.targetGroup }}</span>
              </div>
              <p>{{ item.feedbackNote }}</p>
              <div class="feedback-meta">
                <span>触达 {{ item.reachCount }} 人</span>
                <span>走访 {{ item.visitCount }} 人</span>
                <span>{{ item.plannedAt.slice(0, 10) }}</span>
              </div>
            </article>
          </div>
        </Card>
      </Col>
    </Row>

    <Card class="content-card" :bordered="false" title="宣传计划排期">
      <Table
        :columns="[
          { title: '宣传内容', dataIndex: 'contentTitle', key: 'contentTitle' },
          { title: '对象', dataIndex: 'targetGroup', key: 'targetGroup' },
          { title: '范围', dataIndex: 'pushScope', key: 'pushScope' },
          { title: '计划时间', dataIndex: 'plannedAt', key: 'plannedAt' },
          { title: '进度', key: 'progress', width: 220 },
          { title: '状态', dataIndex: 'status', key: 'status' },
          { title: '操作', key: 'action', width: 150 },
        ]"
        :data-source="plans"
        :loading="loading"
        :pagination="{ pageSize: 5 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'plannedAt'">
            {{ record.plannedAt.replace('T', ' ').slice(0, 16) }}
          </template>
          <template v-else-if="column.key === 'progress'">
            <Progress
              :percent="getPlanProgress(record as CommunityEducationPlan)"
              size="small"
            />
          </template>
          <template v-else-if="column.key === 'status'">
            <Tag
              :color="
                record.status === 'published'
                  ? 'success'
                  : record.status === 'scheduled'
                    ? 'processing'
                    : record.status === 'draft'
                      ? 'warning'
                      : 'default'
              "
            >
              {{ record.status }}
            </Tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <Space>
              <Button
                size="small"
                @click="openEdit(record as CommunityEducationPlan)"
              >
                编辑
              </Button>
              <Button danger size="small" @click="removePlan(record.id)">删除</Button>
            </Space>
          </template>
        </template>
      </Table>
    </Card>

    <Modal
      v-model:open="modalOpen"
      :title="editingPlanId ? '编辑宣传计划' : '新建宣传计划'"
      ok-text="保存"
      cancel-text="取消"
      @ok="submitPlan"
    >
      <Form layout="vertical">
        <Form.Item label="宣教内容">
          <Select v-model:value="formState.contentId" :options="contentOptions" />
        </Form.Item>
        <Form.Item label="目标人群">
          <Select
            v-model:value="formState.targetGroup"
            :options="[
              { label: '老人用户', value: '老人用户' },
              { label: '子女家属', value: '子女家属' },
              { label: '网格员/志愿者', value: '网格员/志愿者' },
            ]"
          />
        </Form.Item>
        <Form.Item label="推送范围">
          <Select
            v-model:value="formState.pushScope"
            :options="[
              { label: '全辖区', value: 'all' },
              { label: '高风险对象', value: 'high-risk' },
              { label: '中风险对象', value: 'medium-risk' },
            ]"
          />
        </Form.Item>
        <Form.Item label="计划时间">
          <Input v-model:value="formState.plannedAt" type="datetime-local" />
        </Form.Item>
        <Form.Item label="投放渠道">
          <Select
            v-model:value="formState.channel"
            :options="[
              { label: '图文文章', value: 'article' },
              { label: 'App 推送', value: 'app' },
              { label: '线下宣讲', value: 'offline' },
            ]"
          />
        </Form.Item>
        <Form.Item label="覆盖目标人数">
          <Input v-model:value="formState.coverageGoal" type="number" />
        </Form.Item>
        <Form.Item label="当前触达人数">
          <Input v-model:value="formState.reachCount" type="number" />
        </Form.Item>
        <Form.Item label="回访人数">
          <Input v-model:value="formState.visitCount" type="number" />
        </Form.Item>
        <Form.Item label="计划状态">
          <Select
            v-model:value="formState.status"
            :options="[
              { label: '草稿', value: 'draft' },
              { label: '已排期', value: 'scheduled' },
              { label: '已发布', value: 'published' },
              { label: '已取消', value: 'cancelled' },
            ]"
          />
        </Form.Item>
        <Form.Item label="反馈摘要">
          <Input.TextArea v-model:value="formState.feedbackNote" :rows="4" />
        </Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.community-education-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgb(217 249 157 / 55%), transparent 30%),
    linear-gradient(180deg, #f7fee7 0%, #ecfccb 100%);
}

.hero-panel,
.stat-card,
.content-card {
  background: rgb(255 255 255 / 94%);
  border: 1px solid rgb(77 124 15 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 34px rgb(77 124 15 / 10%);
}

.hero-panel {
  display: flex;
  gap: 16px;
  justify-content: space-between;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #4d7c0f;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #365314;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  color: #4b5563;
  line-height: 1.8;
}

.stats-row,
.content-row {
  margin-top: 18px;
}

.toolbar {
  margin-bottom: 16px;
}

.library-list,
.feedback-list {
  display: grid;
  gap: 14px;
}

.library-item,
.feedback-item {
  padding: 16px 18px;
  background: #f7fee7;
  border: 1px solid rgb(132 204 22 / 20%);
  border-radius: 18px;
}

.library-head,
.feedback-top,
.library-meta,
.feedback-meta {
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.library-head h3,
.feedback-top strong {
  margin: 0;
  color: #365314;
}

.library-head p,
.feedback-item p {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.7;
}

.library-meta,
.feedback-meta,
.feedback-top span {
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .community-education-page {
    padding: 16px;
  }

  .hero-panel,
  .library-head,
  .feedback-top,
  .library-meta,
  .feedback-meta {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
