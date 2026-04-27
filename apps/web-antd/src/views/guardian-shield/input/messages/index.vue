<script lang="ts" setup>
import { computed, reactive, ref } from 'vue';

import { useUserStore } from '@vben/stores';

import { Button, Card, Input, Select, Space, Tag, message } from 'ant-design-vue';

import { lookupPhoneApi } from '#/api';
import { useCommunicationStore } from '#/store';

defineOptions({ name: 'InputMessages' });

const userStore = useUserStore();
const communicationStore = useCommunicationStore();
const sending = ref(false);
const formState = reactive({
  contentText: '您的退款已到账，请立即点击链接并提供验证码完成补偿。',
  sourcePhone: '17099990001',
  targetPhone: '13800001001',
});

const latestEvents = computed(() =>
  communicationStore.events
    .filter((item) => item.scene === 'sms')
    .slice(0, 6),
);

const sourceOptions = [
  { label: '陌生号码 17099990001', value: '17099990001' },
  { label: '诈骗号码 01012345678', value: '01012345678' },
  { label: '安全家属 13900002001', value: '13900002001' },
  { label: '银行客服 95533', value: '95533' },
];

async function sendMessageEvent() {
  if (!formState.sourcePhone || !formState.targetPhone || !formState.contentText) {
    message.warning('请填写发起号码、老人号码和短信内容');
    return;
  }
  sending.value = true;
  try {
    const target = await lookupPhoneApi(formState.targetPhone, 'elder');
    await communicationStore.sendSmsEvent({
      contentText: formState.contentText,
      elderUserId: target.userId,
      operatorUserId: userStore.userInfo?.userId,
      sourcePhone: formState.sourcePhone,
      targetPhone: target.phone,
    });
    message.success('短信已送达老人端');
  } finally {
    sending.value = false;
  }
}

function getRiskColor(level?: string) {
  if (level === 'high') return 'red';
  if (level === 'medium') return 'orange';
  if (level === 'low') return 'green';
  return 'blue';
}
</script>

<template>
  <div class="input-messages-page">
    <section class="workbench">
      <div>
        <p class="eyebrow">输入端</p>
        <h1>短信输入</h1>
      </div>
      <Tag color="blue">operator_user_id: {{ userStore.userInfo?.userId }}</Tag>
    </section>

    <div class="layout-grid">
      <Card class="panel-card" :bordered="false" title="发送短信事件">
        <Space direction="vertical" size="middle" style="width: 100%">
          <Select
            v-model:value="formState.sourcePhone"
            show-search
            :options="sourceOptions"
            placeholder="选择或输入本次发起号码"
          />
          <Input
            v-model:value="formState.targetPhone"
            placeholder="目标老人电话号码"
          />
          <Input.TextArea
            v-model:value="formState.contentText"
            :auto-size="{ minRows: 6, maxRows: 8 }"
            placeholder="短信内容"
          />
          <Button
            block
            size="large"
            type="primary"
            :loading="sending"
            @click="sendMessageEvent"
          >
            发送到老人端
          </Button>
        </Space>
      </Card>

      <Card class="panel-card" :bordered="false" title="最近短信事件">
        <div v-if="latestEvents.length" class="event-list">
          <div v-for="item in latestEvents" :key="item.id" class="event-item">
            <div>
              <strong>{{ item.sourcePhone }} -> {{ item.targetPhone }}</strong>
              <p>{{ item.contentText }}</p>
            </div>
            <Space wrap>
              <Tag>{{ item.trustType }}</Tag>
              <Tag :color="getRiskColor(item.risk?.riskLevel)">
                {{ item.risk?.riskLevel || item.status }}
              </Tag>
            </Space>
          </div>
        </div>
        <p v-else class="empty-text">暂无短信事件</p>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.input-messages-page {
  min-height: 100%;
  padding: 24px;
  background: #f7f8fb;
}

.workbench,
.panel-card {
  border: 1px solid #d7dde8;
  border-radius: 8px;
  background: #fff;
}

.workbench {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 22px;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #3b6ea8;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-size: 26px;
}

.layout-grid {
  display: grid;
  grid-template-columns: minmax(320px, 440px) minmax(0, 1fr);
  gap: 16px;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.event-item p,
.empty-text {
  margin: 8px 0 0;
  color: #667085;
}

@media (max-width: 900px) {
  .layout-grid,
  .workbench,
  .event-item {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
