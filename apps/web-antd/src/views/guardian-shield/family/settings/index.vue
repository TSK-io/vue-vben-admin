<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Modal,
  Row,
  Select,
  Space,
  Table,
  message,
} from 'ant-design-vue';

import {
  createFamilyReminderTemplateApi,
  getBindingListApi,
  getFamilyReminderReceiptsApi,
  getFamilyReminderTemplatesApi,
  sendFamilyReminderApi,
  updateFamilyReminderTemplateApi,
} from '#/api';
import type { FamilyReminderReceiptItem, FamilyReminderTemplateItem } from '#/api';

defineOptions({ name: 'FamilySettings' });

const selectedElderId = ref<string>();
const reminderText = ref('');
const sendChannel = ref<'app' | 'sms' | 'voice'>('app');
const sending = ref(false);
const bindings = ref<any[]>([]);
const templates = ref<FamilyReminderTemplateItem[]>([]);
const receipts = ref<FamilyReminderReceiptItem[]>([]);
const editorVisible = ref(false);
const editingId = ref<string>();
const formState = reactive<Omit<FamilyReminderTemplateItem, 'id'>>({
  channel: 'app',
  code: '',
  content: '',
  isDefault: false,
  name: '',
  notes: '',
  status: 'enabled',
});

const elderOptions = computed(() =>
  bindings.value.map((item) => ({
    label: item.elderName,
    value: item.elderUserId,
  })),
);

async function loadBindings() {
  bindings.value = await getBindingListApi();
  selectedElderId.value = bindings.value[0]?.elderUserId;
}

async function loadTemplates() {
  templates.value = await getFamilyReminderTemplatesApi();
}

async function loadReceipts() {
  receipts.value = await getFamilyReminderReceiptsApi();
}

function useTemplate(item: FamilyReminderTemplateItem) {
  reminderText.value = item.content;
  sendChannel.value = item.channel as 'app' | 'sms' | 'voice';
}

function openCreateTemplate() {
  editingId.value = undefined;
  Object.assign(formState, {
    channel: 'app',
    code: '',
    content: '',
    isDefault: false,
    name: '',
    notes: '',
    status: 'enabled',
  });
  editorVisible.value = true;
}

function openEditTemplate(item: FamilyReminderTemplateItem) {
  editingId.value = item.id;
  Object.assign(formState, item);
  editorVisible.value = true;
}

async function submitTemplate() {
  if (editingId.value) {
    await updateFamilyReminderTemplateApi(editingId.value, formState);
    message.success('模板已更新');
  } else {
    await createFamilyReminderTemplateApi(formState);
    message.success('模板已新增');
  }
  editorVisible.value = false;
  await loadTemplates();
}

async function submitReminder() {
  if (!selectedElderId.value || !reminderText.value.trim()) {
    message.warning('请选择老人并填写提醒内容');
    return;
  }
  sending.value = true;
  try {
    await sendFamilyReminderApi({
      channel: sendChannel.value,
      content: reminderText.value.trim(),
      elderUserId: selectedElderId.value,
    });
    message.success('远程提醒已发送');
    reminderText.value = '';
    await loadReceipts();
  } finally {
    sending.value = false;
  }
}

onMounted(() => {
  void Promise.all([loadBindings(), loadTemplates(), loadReceipts()]);
});
</script>

<template>
  <div class="family-settings-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 监护设置</p>
        <h1>监护设置</h1>
        <p class="description">
          已支持模板新增编辑、真实发送和发送回执，常用文案可以直接沉淀复用。
        </p>
      </div>
      <div class="hero-note">
        <strong>建议</strong>
        <span>看到高风险事件时，优先使用简短明确的提醒文案。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="10" :span="24">
        <Card class="setting-card" :bordered="false" title="发送远程提醒">
          <Space direction="vertical" style="width: 100%">
            <Select
              v-model:value="selectedElderId"
              :options="elderOptions"
              placeholder="选择老人"
            />
            <Select
              v-model:value="sendChannel"
              :options="[
                { label: '站内提醒', value: 'app' },
                { label: '短信提醒', value: 'sms' },
                { label: '语音提醒', value: 'voice' },
              ]"
            />
            <Input.TextArea
              v-model:value="reminderText"
              :rows="5"
              placeholder="请输入提醒内容"
            />
            <Button type="primary" :loading="sending" @click="submitReminder">
              发送提醒
            </Button>
          </Space>
        </Card>
      </Col>
      <Col :lg="14" :span="24">
        <Card class="template-card" :bordered="false" title="常用提醒模板">
          <template #extra>
            <Button size="small" @click="openCreateTemplate">新增模板</Button>
          </template>
          <Space direction="vertical" style="width: 100%">
            <div
              v-for="item in templates"
              :key="item.id"
              class="template-item"
            >
              <div class="template-head">
                <span>{{ item.name }}</span>
                <Space>
                  <Button size="small" @click="useTemplate(item)">使用</Button>
                  <Button size="small" @click="openEditTemplate(item)">编辑</Button>
                </Space>
              </div>
              <p>{{ item.content }}</p>
            </div>
          </Space>
        </Card>
      </Col>
    </Row>

    <Card class="receipt-card" :bordered="false" title="发送回执">
      <Table
        :data-source="receipts"
        :columns="[
          { title: '老人', dataIndex: 'elderName', key: 'elderName' },
          { title: '渠道', dataIndex: 'channel', key: 'channel' },
          { title: '内容', dataIndex: 'content', key: 'content' },
          { title: '发送时间', dataIndex: 'sentAt', key: 'sentAt' },
          { title: '状态', dataIndex: 'receiptStatus', key: 'receiptStatus' },
        ]"
        :pagination="false"
        row-key="notificationId"
      />
    </Card>

    <Modal
      v-model:open="editorVisible"
      title="提醒模板"
      ok-text="保存"
      cancel-text="关闭"
      @ok="submitTemplate"
    >
      <Form layout="vertical">
        <Form.Item label="模板编码">
          <Input v-model:value="formState.code" />
        </Form.Item>
        <Form.Item label="模板名称">
          <Input v-model:value="formState.name" />
        </Form.Item>
        <Form.Item label="发送渠道">
          <Select
            v-model:value="formState.channel"
            :options="[
              { label: '站内提醒', value: 'app' },
              { label: '短信提醒', value: 'sms' },
              { label: '语音提醒', value: 'voice' },
            ]"
          />
        </Form.Item>
        <Form.Item label="模板内容">
          <Input.TextArea v-model:value="formState.content" :rows="4" />
        </Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.family-settings-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #fff8fa 0%, #fff1f5 100%);
}

.hero-panel,
.setting-card,
.template-card,
.receipt-card {
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

.description,
.hero-note,
.template-item p {
  line-height: 1.8;
  color: #9f1239;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  background: #fff1f2;
  border-radius: 20px;
}

.content-row,
.receipt-card {
  margin-top: 18px;
}

.template-item {
  padding: 16px;
  background: #fff7f9;
  border-radius: 18px;
}

.template-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #881337;
}

@media (max-width: 768px) {
  .family-settings-page {
    padding: 16px;
  }

  .hero-panel,
  .template-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
