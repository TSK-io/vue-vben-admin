<template>
  <view class="page-shell">
    <ss-topbar title="家人和熟人" subtitle="常联系的人放前面，点一下就能发消息或打电话。" show-back />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="这里可以语音读出联系人姓名和关系，方便慢慢看。" />
    <ss-feedback-state
      v-if="!contacts.length"
      empty
      empty-title="联系人列表暂时为空"
      empty-description="稍后添加家人联系人后，就能从这里直接联系。"
    />

    <ss-card v-for="contact in contacts" :key="contact.id">
      <view class="contact-row">
        <view class="avatar">{{ contact.avatarText }}</view>
        <view class="contact-main">
          <view class="name-row">
            <text class="name">{{ contact.name }}</text>
            <text v-if="contact.tag" class="tag">{{ contact.tag }}</text>
            <text v-if="contact.isPriority" class="tag priority">常联系</text>
            <text v-if="contact.isBlacklisted" class="tag danger">谨慎联系</text>
            <text v-if="contact.suspiciousLevel && contact.suspiciousLevel !== 'none'" class="tag warm">先确认</text>
          </view>
          <text class="relation">{{ contact.relation }}</text>
          <text class="note">{{ contact.note }}</text>
        </view>
      </view>
      <view class="action-row">
        <button class="mini-btn" @click="chatWith(contact.id)">发消息</button>
        <button class="mini-btn secondary" @click="startCall(contact.id)">打电话</button>
      </view>
    </ss-card>

    <button class="record-button" @click="openPage('/pages/elder/call-records')">最近通话</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const contacts = computed(() => store.contacts)

function chatWith(contactId: string) {
  store.selectContact(contactId)
  openPage('/pages/elder/chat')
}

function startCall(contactId: string) {
  store.selectContact(contactId)
  store.startCall(contactId, 'elder', 'outgoing')
  openPage('/pages/elder/call')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background:
    radial-gradient(circle at top left, rgba(223, 247, 242, 0.55), transparent 26%),
    #f7f3e9;
}
.contact-row {
  display: flex;
  gap: 18rpx;
}
.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #dff7f2 0%, #c7ece3 100%);
  color: var(--ss-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
}
.contact-main {
  flex: 1;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: #fff0d2;
  color: #8a5a00;
  font-size: var(--ss-font-size-caption);
}
.tag.priority {
  background: #dff7f2;
  color: var(--ss-color-primary);
}
.tag.warm {
  background: #fff0d2;
  color: #8a5a00;
}
.tag.danger {
  background: #fee2e2;
  color: #991b1b;
}
.relation,
.note {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.action-row {
  display: flex;
  gap: 14rpx;
  margin-top: 20rpx;
}
.mini-btn {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-body);
}
.mini-btn.secondary {
  background: #eef2f7;
  color: var(--ss-color-text);
}
.record-button {
  border: none;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.85);
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
  box-shadow: 0 12rpx 24rpx rgba(22, 48, 43, 0.06);
}
</style>
