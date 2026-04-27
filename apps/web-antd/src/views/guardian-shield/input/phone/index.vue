<script lang="ts" setup>
import { computed, reactive, ref } from 'vue';

import { useUserStore } from '@vben/stores';

import { Button, Card, Input, Select, Space, Tag, message } from 'ant-design-vue';

import { lookupPhoneApi } from '#/api';
import { useCommunicationStore } from '#/store';

defineOptions({ name: 'InputPhone' });

const userStore = useUserStore();
const communicationStore = useCommunicationStore();
const creating = ref(false);
const formState = reactive({
  sourcePhone: '01012345678',
  targetPhone: '13800001001',
});

const recentCalls = computed(() =>
  communicationStore.events
    .filter((item) => item.scene === 'call')
    .slice(0, 8),
);

const sourceOptions = [
  { label: '诈骗来电 01012345678', value: '01012345678' },
  { label: '陌生手机 17099990001', value: '17099990001' },
  { label: '安全家属 13900002001', value: '13900002001' },
  { label: '社区号码 13700003001', value: '13700003001' },
];

async function createIncomingCall() {
  if (!formState.sourcePhone || !formState.targetPhone) {
    message.warning('请填写发起号码和老人号码');
    return;
  }
  creating.value = true;
  try {
    const target = await lookupPhoneApi(formState.targetPhone, 'elder');
    const event = communicationStore.createCallEvent({
      elderUserId: target.userId,
      operatorUserId: userStore.userInfo?.userId,
      sourcePhone: formState.sourcePhone,
      targetPhone: target.phone,
    });
    if (event.status === 'intercepted') {
      message.warning('该号码已在老人黑名单中，本次来电已按拦截处理');
      return;
    }
    message.success('来电事件已推送到老人端');
  } finally {
    creating.value = false;
  }
}
</script>

<template>
  <div class="input-phone-page">
    <section class="workbench">
      <div>
        <p class="eyebrow">输入端</p>
        <h1>电话输入</h1>
      </div>
      <Tag color="geekblue">Web 电话剧情入口</Tag>
    </section>

    <div class="layout-grid">
      <Card class="panel-card" :bordered="false" title="发起来电事件">
        <Space direction="vertical" size="middle" style="width: 100%">
          <Select
            v-model:value="formState.sourcePhone"
            show-search
            :options="sourceOptions"
            placeholder="选择本次发起号码"
          />
          <Input
            v-model:value="formState.targetPhone"
            placeholder="目标老人电话号码"
          />
          <Button
            block
            size="large"
            type="primary"
            :loading="creating"
            @click="createIncomingCall"
          >
            推送陌生来电
          </Button>
        </Space>
      </Card>

      <Card class="panel-card" :bordered="false" title="最近电话事件">
        <div v-if="recentCalls.length" class="event-list">
          <div v-for="item in recentCalls" :key="item.id" class="event-item">
            <div>
              <strong>{{ item.sourcePhone }} -> {{ item.targetPhone }}</strong>
              <p>{{ item.createdAt }}</p>
            </div>
            <Space wrap>
              <Tag>{{ item.trustType }}</Tag>
              <Tag :color="item.status === 'intercepted' ? 'red' : 'blue'">
                {{ item.status }}
              </Tag>
            </Space>
          </div>
        </div>
        <p v-else class="empty-text">暂无电话事件</p>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.input-phone-page {
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
