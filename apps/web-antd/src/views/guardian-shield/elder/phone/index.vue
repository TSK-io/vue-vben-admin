<script lang="ts" setup>
import { computed } from 'vue';

import { Button, Card, Space, Tag, message } from 'ant-design-vue';

import { recognizeCallTextApi } from '#/api';
import { useCommunicationStore } from '#/store';

defineOptions({ name: 'ElderPhone' });

const communicationStore = useCommunicationStore();

const calls = computed(() => communicationStore.callEvents);
const ringingCall = computed(() =>
  calls.value.find((item) => item.status === 'ringing'),
);

function updateCallStatus(id: string, status: 'ended' | 'intercepted') {
  const target = communicationStore.events.find((item) => item.id === id);
  if (!target) return;
  communicationStore.upsertEvent({
    ...target,
    status,
    updatedAt: new Date().toISOString(),
  });
}

async function finishCallWithDemoText(id: string) {
  const target = communicationStore.events.find((item) => item.id === id);
  if (!target) return;
  updateCallStatus(id, 'ended');
  const risk = await recognizeCallTextApi({
    callerNumber: target.sourcePhone,
    durationSeconds: 90,
    elderUserId: target.elderUserId,
    occurredAt: target.createdAt,
    transcriptText:
      '这里是警方专线，请配合调查，把资金转到指定账户，不要告诉家人。',
  });
  communicationStore.handleRiskDecision(id, risk);
  message.success('通话已结束并完成风险识别');
}
</script>

<template>
  <div class="elder-phone-page">
    <section class="phone-status">
      <div>
        <span>9:41</span>
        <strong>{{ communicationStore.currentUserPhone }}</strong>
      </div>
      <span>电话</span>
    </section>

    <main class="phone-shell">
      <div v-if="ringingCall" class="incoming-screen">
        <p>陌生来电</p>
        <h1>{{ ringingCall.sourcePhone }}</h1>
        <Tag :color="ringingCall.trustType === 'unknown' ? 'orange' : 'blue'">
          {{ ringingCall.trustType }}
        </Tag>
        <div class="call-actions">
          <Button danger shape="round" size="large" @click="updateCallStatus(ringingCall.id, 'ended')">
            拒接
          </Button>
          <Button
            type="primary"
            shape="round"
            size="large"
            @click="finishCallWithDemoText(ringingCall.id)"
          >
            接听并结束
          </Button>
        </div>
      </div>

      <template v-else>
        <h1>电话</h1>
        <Card class="dial-card" :bordered="false">
          <p class="dial-number">{{ communicationStore.currentUserPhone || '未读取号码' }}</p>
          <p>当前没有来电</p>
        </Card>
      </template>

      <Card class="history-card" :bordered="false" title="最近通话">
        <div v-if="calls.length" class="call-list">
          <div v-for="item in calls" :key="item.id" class="call-item">
            <div>
              <strong>{{ item.sourcePhone }}</strong>
              <p>{{ item.createdAt }}</p>
            </div>
            <Space wrap>
              <Tag>{{ item.trustType }}</Tag>
              <Tag :color="item.risk?.riskLevel === 'high' ? 'red' : 'blue'">
                {{ item.risk?.riskLevel || item.status }}
              </Tag>
            </Space>
          </div>
        </div>
        <p v-else class="empty-text">暂无通话记录</p>
      </Card>
    </main>

    <nav class="bottom-tabs">
      <RouterLink to="/elder/home">首页</RouterLink>
      <RouterLink to="/elder/phone">电话</RouterLink>
      <RouterLink to="/elder/messages">短信</RouterLink>
      <RouterLink to="/elder/contacts">联系人</RouterLink>
    </nav>
  </div>
</template>

<style scoped>
.elder-phone-page {
  min-height: 100%;
  padding: 18px 18px 88px;
  color: #172033;
  background: linear-gradient(180deg, #e9f3ff 0%, #f8fbff 100%);
}

.phone-status,
.bottom-tabs,
.phone-shell {
  max-width: 560px;
  margin: 0 auto;
}

.phone-status,
.bottom-tabs,
.call-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.phone-status {
  padding: 12px 16px;
  border-radius: 20px;
  background: #ffffffcc;
}

.phone-status div {
  display: flex;
  gap: 12px;
}

.phone-shell {
  margin-top: 18px;
}

h1 {
  margin: 0 0 16px;
  font-size: 34px;
}

.incoming-screen,
.dial-card,
.history-card {
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 14px 32px rgb(15 23 42 / 8%);
}

.incoming-screen {
  padding: 34px 22px;
  text-align: center;
}

.incoming-screen h1 {
  font-size: 40px;
}

.call-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 28px;
}

.dial-number {
  font-size: 28px;
  font-weight: 800;
}

.history-card {
  margin-top: 16px;
}

.call-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.call-item {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
}

.call-item p,
.empty-text {
  margin: 8px 0 0;
  color: #64748b;
}

.bottom-tabs {
  position: fixed;
  right: 18px;
  bottom: 18px;
  left: 18px;
  padding: 12px 18px;
  border-radius: 24px;
  background: #ffffffee;
  box-shadow: 0 16px 34px rgb(15 23 42 / 14%);
}

.bottom-tabs a {
  color: #475569;
  font-weight: 700;
}
</style>
