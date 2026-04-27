<script lang="ts" setup>
import { computed, onMounted } from 'vue';

import { Button, Card, Modal, Space, Tag } from 'ant-design-vue';

import { useCommunicationStore } from '#/store';

defineOptions({ name: 'ElderMessages' });

const communicationStore = useCommunicationStore();

const messages = computed(() => communicationStore.messageEvents);
const activeRisk = computed(() =>
  communicationStore.riskPopupQueue.find((item) => item.scene === 'sms'),
);

function getRiskColor(level?: string) {
  if (level === 'high') return 'red';
  if (level === 'medium') return 'orange';
  if (level === 'low') return 'green';
  return 'blue';
}

onMounted(() => {
  void communicationStore.hydrateBindingContacts();
});
</script>

<template>
  <div class="elder-messages-page">
    <section class="phone-status">
      <div>
        <span>9:41</span>
        <strong>{{ communicationStore.currentUserPhone }}</strong>
      </div>
      <span>短信</span>
    </section>

    <main class="message-shell">
      <h1>短信</h1>
      <div v-if="messages.length" class="thread-list">
        <article v-for="item in messages" :key="item.id" class="thread-card">
          <div class="thread-head">
            <div>
              <strong>{{ item.sourcePhone }}</strong>
              <p>{{ item.createdAt }}</p>
            </div>
            <Space wrap>
              <Tag>{{ item.trustType }}</Tag>
              <Tag :color="getRiskColor(item.risk?.riskLevel)">
                {{ item.risk?.riskLevel || item.status }}
              </Tag>
            </Space>
          </div>
          <p class="message-text">{{ item.contentText }}</p>
          <div v-if="item.risk" class="risk-card">
            <strong>{{ item.risk.reasonDetail }}</strong>
            <p>{{ item.risk.suggestionAction }}</p>
          </div>
        </article>
      </div>
      <Card v-else class="empty-card" :bordered="false">
        暂无短信
      </Card>
    </main>

    <nav class="bottom-tabs">
      <RouterLink to="/elder/home">首页</RouterLink>
      <RouterLink to="/elder/phone">电话</RouterLink>
      <RouterLink to="/elder/messages">短信</RouterLink>
      <RouterLink to="/elder/contacts">联系人</RouterLink>
    </nav>

    <Modal
      :open="!!activeRisk"
      centered
      title="疑似诈骗短信"
      ok-text="知道了"
      cancel-text="关闭"
      @ok="activeRisk && communicationStore.clearRiskPopup(activeRisk.id)"
    >
      <p class="modal-warning">请不要点击链接，不要提供验证码，已通知家属。</p>
      <p>{{ activeRisk?.risk?.reasonDetail }}</p>
      <p>{{ activeRisk?.risk?.suggestionAction }}</p>
      <Button
        v-if="activeRisk"
        danger
        block
        @click="communicationStore.clearRiskPopup(activeRisk.id)"
      >
        我已知道，不继续操作
      </Button>
    </Modal>
  </div>
</template>

<style scoped>
.elder-messages-page {
  min-height: 100%;
  padding: 18px 18px 88px;
  color: #172033;
  background: linear-gradient(180deg, #eef7f3 0%, #f8fbff 100%);
}

.phone-status,
.bottom-tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 520px;
  margin: 0 auto;
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

.message-shell {
  max-width: 520px;
  margin: 18px auto 0;
}

h1 {
  margin: 0 0 16px;
  font-size: 34px;
}

.thread-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.thread-card,
.empty-card,
.risk-card {
  border-radius: 18px;
  background: #fff;
}

.thread-card {
  padding: 18px;
  box-shadow: 0 12px 28px rgb(15 23 42 / 8%);
}

.thread-head {
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.thread-head p,
.risk-card p {
  margin: 8px 0 0;
  color: #64748b;
}

.message-text {
  margin: 16px 0 0;
  font-size: 18px;
  line-height: 1.8;
}

.risk-card {
  padding: 14px;
  margin-top: 14px;
  background: #fff7ed;
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

.modal-warning {
  color: #b91c1c;
  font-size: 18px;
  font-weight: 700;
}
</style>
