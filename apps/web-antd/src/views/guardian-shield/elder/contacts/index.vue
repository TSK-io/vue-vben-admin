<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';

import { Button, Card, Input, Modal, Space, Tag, message } from 'ant-design-vue';

import { useCommunicationStore } from '#/store';

defineOptions({ name: 'ElderContacts' });

const communicationStore = useCommunicationStore();
const trustedVisible = ref(false);
const blockedVisible = ref(false);
const trustedForm = reactive({
  contactName: '',
  contactPhone: '',
  relationshipType: '朋友',
});
const blockedForm = reactive({
  phone: '',
  reason: '手动标记为可疑号码',
});

function addTrusted() {
  if (!trustedForm.contactName || !trustedForm.contactPhone) {
    message.warning('请填写联系人姓名和电话');
    return;
  }
  communicationStore.addTrustedContact({
    contactName: trustedForm.contactName,
    contactPhone: trustedForm.contactPhone,
    contactRole: 'friend',
    elderPhone: communicationStore.currentUserPhone,
    isEmergencyContact: false,
    relationshipType: trustedForm.relationshipType,
    source: 'manual',
  });
  trustedVisible.value = false;
  trustedForm.contactName = '';
  trustedForm.contactPhone = '';
}

function addBlocked() {
  if (!blockedForm.phone) {
    message.warning('请填写黑名单号码');
    return;
  }
  communicationStore.addBlockedNumber({
    elderPhone: communicationStore.currentUserPhone,
    phone: blockedForm.phone,
    reason: blockedForm.reason,
    source: 'manual',
  });
  blockedVisible.value = false;
  blockedForm.phone = '';
}

onMounted(() => {
  void communicationStore.hydrateBindingContacts();
});
</script>

<template>
  <div class="elder-contacts-page">
    <section class="phone-status">
      <div>
        <span>9:41</span>
        <strong>{{ communicationStore.currentUserPhone }}</strong>
      </div>
      <span>联系人</span>
    </section>

    <main class="contacts-shell">
      <div class="section-head">
        <h1>联系人</h1>
        <Space>
          <Button @click="trustedVisible = true">添加联系人</Button>
          <Button danger @click="blockedVisible = true">加入黑名单</Button>
        </Space>
      </div>

      <Card class="panel-card" :bordered="false" title="安全联系人">
        <div v-if="communicationStore.contacts.length" class="list">
          <div
            v-for="item in communicationStore.contacts"
            :key="item.id"
            class="list-item"
          >
            <div>
              <strong>{{ item.contactName }}</strong>
              <p>{{ item.contactPhone }} · {{ item.relationshipType }}</p>
            </div>
            <Space wrap>
              <Tag>{{ item.source }}</Tag>
              <Tag v-if="item.isEmergencyContact" color="red">紧急联系人</Tag>
            </Space>
          </div>
        </div>
        <p v-else class="empty-text">暂无安全联系人</p>
      </Card>

      <Card class="panel-card" :bordered="false" title="黑名单">
        <div v-if="communicationStore.blacklist.length" class="list">
          <div
            v-for="item in communicationStore.blacklist"
            :key="item.id"
            class="list-item"
          >
            <div>
              <strong>{{ item.phone }}</strong>
              <p>{{ item.reason }}</p>
            </div>
            <Space wrap>
              <Tag color="red">{{ item.source }}</Tag>
              <Button
                size="small"
                @click="communicationStore.removeBlockedNumber(item.id)"
              >
                移除
              </Button>
            </Space>
          </div>
        </div>
        <p v-else class="empty-text">暂无黑名单号码</p>
      </Card>
    </main>

    <nav class="bottom-tabs">
      <RouterLink to="/elder/home">首页</RouterLink>
      <RouterLink to="/elder/phone">电话</RouterLink>
      <RouterLink to="/elder/messages">短信</RouterLink>
      <RouterLink to="/elder/contacts">联系人</RouterLink>
    </nav>

    <Modal
      v-model:open="trustedVisible"
      title="添加安全联系人"
      ok-text="保存"
      cancel-text="取消"
      @ok="addTrusted"
    >
      <Space direction="vertical" style="width: 100%">
        <Input v-model:value="trustedForm.contactName" placeholder="姓名" />
        <Input v-model:value="trustedForm.contactPhone" placeholder="电话号码" />
        <Input v-model:value="trustedForm.relationshipType" placeholder="关系" />
      </Space>
    </Modal>

    <Modal
      v-model:open="blockedVisible"
      title="加入黑名单"
      ok-text="保存"
      cancel-text="取消"
      @ok="addBlocked"
    >
      <Space direction="vertical" style="width: 100%">
        <Input v-model:value="blockedForm.phone" placeholder="电话号码" />
        <Input v-model:value="blockedForm.reason" placeholder="原因" />
      </Space>
    </Modal>
  </div>
</template>

<style scoped>
.elder-contacts-page {
  min-height: 100%;
  padding: 18px 18px 88px;
  color: #172033;
  background: linear-gradient(180deg, #eef7f3 0%, #f8fbff 100%);
}

.phone-status,
.bottom-tabs,
.contacts-shell {
  max-width: 560px;
  margin: 0 auto;
}

.phone-status,
.section-head,
.bottom-tabs,
.list-item {
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

.contacts-shell {
  margin-top: 18px;
}

h1 {
  margin: 0;
  font-size: 34px;
}

.panel-card {
  margin-top: 16px;
  border-radius: 18px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-item {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
}

.list-item p,
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
