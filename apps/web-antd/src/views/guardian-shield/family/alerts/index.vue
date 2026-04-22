<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  Button,
  Card,
  Col,
  List,
  Modal,
  Row,
  Select,
  Space,
  Tag,
  message,
} from 'ant-design-vue';

import { getBindingListApi, getFamilyAlertListApi, sendFamilyReminderApi } from '#/api';
import type { FamilyAlertItem } from '#/api';

defineOptions({ name: 'FamilyAlerts' });

const router = useRouter();

const loading = ref(false);
const alerts = ref<FamilyAlertItem[]>([]);
const total = ref(0);
const elderOptions = ref<Array<{ label: string; value: string }>>([]);
const reminderVisible = ref(false);
const reminderSubmitting = ref(false);
const selectedAlert = ref<FamilyAlertItem | null>(null);
const reminderChannel = ref<'app' | 'sms' | 'voice'>('app');
const reminderText = ref('');

const filters = reactive({
  elderName: undefined as string | undefined,
  page: 1,
  pageSize: 5,
  readStatus: undefined as string | undefined,
  riskLevel: undefined as string | undefined,
  status: undefined as string | undefined,
});

const riskColorMap: Record<FamilyAlertItem['riskLevel'], string> = {
  high: 'red',
  low: 'green',
  medium: 'orange',
};
const riskTextMap: Record<FamilyAlertItem['riskLevel'], string> = {
  high: '高风险',
  low: '低风险',
  medium: '中风险',
};
const sourceTextMap: Record<FamilyAlertItem['sourceType'], string> = {
  call: '通话识别',
  sms: '短信识别',
};
const statusTextMap: Record<FamilyAlertItem['status'], string> = {
  handled: '已处理',
  pending: '待处理',
};
const readTextMap: Record<FamilyAlertItem['readStatus'], string> = {
  read: '已读',
  unread: '未读',
};

const summaryCards = computed(() => [
  {
    title: '通知总数',
    value: `${total.value}`,
    description: '承接来自老年端高风险事件的家庭侧提醒。',
  },
  {
    title: '高风险',
    value: `${alerts.value.filter((item) => item.riskLevel === 'high').length}`,
    description: '优先展示需要立即远程干预的事件。',
  },
  {
    title: '未读提醒',
    value: `${alerts.value.filter((item) => item.readStatus === 'unread').length}`,
    description: '便于家属快速处理新增风险事件。',
  },
  {
    title: '待跟进',
    value: `${alerts.value.filter((item) => item.status === 'pending').length}`,
    description: '后续可继续联动社区和处置反馈。',
  },
]);

async function loadAlerts() {
  loading.value = true;
  try {
    const [data, bindings] = await Promise.all([
      getFamilyAlertListApi({
        page: filters.page,
        pageSize: filters.pageSize,
        readStatus: filters.readStatus,
        riskLevel: filters.riskLevel,
        status: filters.status,
      }),
      getBindingListApi(),
    ]);
    elderOptions.value = bindings.map((item: any) => ({
      label: item.elderName,
      value: item.elderName,
    }));
    alerts.value = data.items.filter(
      (item: FamilyAlertItem) =>
        !filters.elderName || item.elderName === filters.elderName,
    );
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function getRiskLabel(level: FamilyAlertItem['riskLevel']) {
  return riskTextMap[level];
}
function getRiskColor(level: FamilyAlertItem['riskLevel']) {
  return riskColorMap[level];
}
function getSourceLabel(type: FamilyAlertItem['sourceType']) {
  return sourceTextMap[type];
}
function getStatusLabel(status: FamilyAlertItem['status']) {
  return statusTextMap[status];
}
function getReadLabel(status: FamilyAlertItem['readStatus']) {
  return readTextMap[status];
}

function handleSearch() {
  filters.page = 1;
  void loadAlerts();
}

function handleReset() {
  filters.elderName = undefined;
  filters.page = 1;
  filters.pageSize = 5;
  filters.readStatus = undefined;
  filters.riskLevel = undefined;
  filters.status = undefined;
  void loadAlerts();
}

function handlePageChange(page: number, pageSize: number) {
  filters.page = page;
  filters.pageSize = pageSize;
  void loadAlerts();
}

function openReminder(item: FamilyAlertItem) {
  selectedAlert.value = item;
  reminderChannel.value = 'app';
  reminderText.value = item.remoteMessage;
  reminderVisible.value = true;
}

async function handleOpenChat(item: FamilyAlertItem) {
  const bindings = await getBindingListApi();
  const target = bindings.find((binding) => binding.elderName === item.elderName);
  if (!target) {
    message.warning('未找到对应老人绑定关系，暂时无法发起聊天');
    return;
  }
  await router.push({
    path: '/chat/index',
    query: {
      source: 'risk-alert',
      userId: target.elderUserId,
    },
  });
}

async function submitReminder() {
  if (!selectedAlert.value || !reminderText.value.trim()) {
    message.warning('请先确认提醒内容');
    return;
  }
  const bindings = await getBindingListApi();
  const target = bindings.find(
    (item) => item.elderName === selectedAlert.value?.elderName,
  );
  if (!target) {
    message.warning('未找到对应绑定关系，暂时无法发送');
    return;
  }
  reminderSubmitting.value = true;
  try {
    await sendFamilyReminderApi({
      channel: reminderChannel.value,
      content: reminderText.value.trim(),
      elderUserId: target.elderUserId,
    });
    message.success('远程提醒已发送');
    reminderVisible.value = false;
  } finally {
    reminderSubmitting.value = false;
  }
}

onMounted(() => {
  void loadAlerts();
});
</script>

<template>
  <div class="family-alerts-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 风险联动</p>
        <h1>风险详情</h1>
        <p class="description">
          当前页面已经接入真实 mock
          风险事件，会展示老人姓名、识别原因、建议动作和推荐提醒文案，帮助家属快速干预。
        </p>
      </div>
      <div class="hero-note">
        <strong>干预建议</strong>
        <span
          >看到高风险事件时，优先电话联系老人，提醒不要转账、不要泄露验证码。</span
        >
      </div>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col
        v-for="item in summaryCards"
        :key="item.title"
        :lg="6"
        :md="12"
        :span="24"
      >
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Select
          v-model:value="filters.elderName"
          allow-clear
          placeholder="老人姓名"
          style="width: 170px"
          :options="elderOptions"
        />
        <Select
          v-model:value="filters.riskLevel"
          allow-clear
          placeholder="风险等级"
          style="width: 150px"
          :options="[
            { label: '高风险', value: 'high' },
            { label: '中风险', value: 'medium' },
            { label: '低风险', value: 'low' },
          ]"
        />
        <Select
          v-model:value="filters.readStatus"
          allow-clear
          placeholder="阅读状态"
          style="width: 150px"
          :options="[
            { label: '未读', value: 'unread' },
            { label: '已读', value: 'read' },
          ]"
        />
        <Select
          v-model:value="filters.status"
          allow-clear
          placeholder="处理状态"
          style="width: 150px"
          :options="[
            { label: '待处理', value: 'pending' },
            { label: '已处理', value: 'handled' },
          ]"
        />
        <Button type="primary" @click="handleSearch">筛选</Button>
        <Button @click="handleReset">重置</Button>
      </Space>
    </Card>

    <Card class="list-card" :bordered="false">
      <List
        :data-source="alerts"
        :loading="loading"
        :locale="{ emptyText: '当前条件下暂无风险事件' }"
        item-layout="vertical"
        :pagination="{
          current: filters.page,
          pageSize: filters.pageSize,
          total,
          onChange: handlePageChange,
        }"
      >
        <template #renderItem="{ item }">
          <List.Item class="alert-item">
            <div class="alert-header">
              <div>
                <h3>{{ item.title }}</h3>
                <p class="subline">
                  {{ item.elderName }} · {{ item.occurredAt }} ·
                  {{ getSourceLabel(item.sourceType) }}
                </p>
              </div>
              <Space wrap>
                <Tag :color="getRiskColor(item.riskLevel)">{{
                  getRiskLabel(item.riskLevel)
                }}</Tag>
                <Tag color="blue">风险分 {{ item.riskScore }}</Tag>
                <Tag>{{ getReadLabel(item.readStatus) }}</Tag>
                <Tag>{{ getStatusLabel(item.status) }}</Tag>
              </Space>
            </div>

            <Row :gutter="[16, 16]">
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">命中原因</p>
                  <p class="info-text">{{ item.hitReason }}</p>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">建议动作</p>
                  <p class="info-text">{{ item.advice }}</p>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card callout-card">
                  <p class="info-label">推荐提醒文案</p>
                  <p class="info-text">{{ item.remoteMessage }}</p>
                  <Space wrap>
                    <Button type="primary" @click="openReminder(item)">
                      发送远程提醒
                    </Button>
                    <Button @click="handleOpenChat(item)">发起聊天</Button>
                  </Space>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">联动建议</p>
                  <p class="info-text">{{ item.contactSuggestion }}</p>
                  <p v-if="item.handledAt" class="handled-at">
                    已于 {{ item.handledAt }} 记录处置结果
                  </p>
                </div>
              </Col>
            </Row>
          </List.Item>
        </template>
      </List>
    </Card>

    <Modal
      v-model:open="reminderVisible"
      title="发送远程提醒"
      ok-text="立即发送"
      cancel-text="取消"
      :confirm-loading="reminderSubmitting"
      @ok="submitReminder"
    >
      <Space direction="vertical" style="width: 100%">
        <p v-if="selectedAlert">
          当前对象：{{ selectedAlert.elderName }} · {{ selectedAlert.title }}
        </p>
        <Select
          v-model:value="reminderChannel"
          :options="[
            { label: '站内提醒', value: 'app' },
            { label: '短信提醒', value: 'sms' },
            { label: '语音提醒', value: 'voice' },
          ]"
        />
        <textarea v-model="reminderText" class="reminder-textarea" rows="5" />
      </Space>
    </Modal>
  </div>
</template>

<style scoped>
.family-alerts-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(185 28 28 / 12%), transparent 28%),
    linear-gradient(180deg, #fff8f8 0%, #fff1f2 100%);
}

.hero-panel,
.summary-card,
.filter-card,
.list-card,
.info-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(244 63 94 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(127 29 29 / 8%);
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
  color: #be123c;
  letter-spacing: 0.08em;
}

h1,
h3 {
  margin: 0;
  color: #881337;
}

.description,
.summary-desc,
.info-text,
.subline,
.handled-at {
  color: #7f1d1d;
}

.description {
  max-width: 760px;
  margin-top: 16px;
  line-height: 1.8;
}

.hero-note {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 320px;
  padding: 18px;
  line-height: 1.8;
  color: #9f1239;
  background: #fff1f2;
  border-radius: 20px;
}

.summary-row,
.filter-card,
.list-card {
  margin-top: 18px;
}

.summary-title {
  margin: 0;
  color: #9f1239;
}

.summary-value {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  color: #881337;
}

.summary-desc,
.subline,
.handled-at {
  margin-top: 10px;
  line-height: 1.7;
}

.alert-item {
  padding: 6px 0 20px;
}

.alert-header {
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 16px;
}

.info-card {
  height: 100%;
  padding: 18px;
}

.info-label {
  margin: 0;
  font-weight: 700;
  color: #be123c;
}

.callout-card {
  background: #fff1f2;
}

.reminder-textarea {
  width: 100%;
  padding: 12px;
  font: inherit;
  color: #7f1d1d;
  resize: vertical;
  background: #fff7f8;
  border: 1px solid rgb(244 63 94 / 18%);
  border-radius: 14px;
}

@media (max-width: 768px) {
  .family-alerts-page {
    padding: 16px;
  }

  .hero-panel,
  .alert-header {
    flex-direction: column;
  }
}
</style>
