<template>
  <view class="page-shell">
    <ss-topbar title="最近消息" subtitle="只保留最近联系的人，点一下直接进入聊天。" show-back />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="这里可以读出最近消息和联系人名字。" />

    <view class="page-note">
      <text class="page-note-text">陌生内容看不懂时，不要急着回，先点开家人的聊天。</text>
    </view>

    <ss-feedback-state
      v-if="!sessions.length"
      empty
      empty-title="还没有最近消息"
      empty-description="和家人聊过天以后，这里会显示最近联系的人。"
    />

    <ss-card v-for="session in sessions" :key="session.contactId">
      <view class="session-row" @click="openChat(session.contactId)">
        <view class="avatar">{{ session.avatarText }}</view>
        <view class="session-main">
          <view class="name-row">
            <text class="name">{{ session.name }}</text>
            <text v-if="session.hasRisk" class="risk-tag">先确认</text>
          </view>
          <text class="relation">{{ session.relation }}</text>
          <text class="preview">{{ messageTypeLabel(session.messageType) }}{{ session.lastMessage }}</text>
        </view>
        <view class="session-side">
          <text class="time">{{ session.lastMessageTime }}</text>
          <text v-if="session.unreadCount" class="unread">{{ session.unreadCount }}</text>
        </view>
      </view>
    </ss-card>

    <button class="back-home-btn" @click="openPage('/pages/elder/home')">回到首页</button>
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
import type { MessageType } from '@/types/app'

const store = useAppStore()
const sessions = computed(() => store.chatSessions.filter((item) => !item.contactId.startsWith('elder-')))

function openChat(contactId: string) {
  store.selectContact(contactId)
  openPage('/pages/elder/chat')
}

function messageTypeLabel(type: MessageType) {
  if (type === 'image') {
    return '[图片] '
  }

  if (type === 'link') {
    return '[链接] '
  }

  return ''
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
    radial-gradient(circle at top left, rgba(255, 233, 193, 0.45), transparent 24%),
    #f7f3e9;
}
.page-note {
  padding: 20rpx 24rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.82);
}
.page-note-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.session-row {
  display: flex;
  gap: 18rpx;
  align-items: flex-start;
}
.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: #dff7f2;
  color: var(--ss-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
}
.session-main {
  flex: 1;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}
.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.risk-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: var(--ss-font-size-caption);
}
.risk-tag {
  background: #fff0d2;
  color: #8a5a00;
}
.relation,
.preview,
.time {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.session-side {
  min-width: 110rpx;
  text-align: right;
}
.unread {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36rpx;
  height: 36rpx;
  margin-top: 12rpx;
  padding: 0 10rpx;
  border-radius: 999rpx;
  background: var(--ss-color-danger);
  color: #fff;
  font-size: var(--ss-font-size-caption);
}
.back-home-btn {
  border: none;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.84);
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
  box-shadow: 0 12rpx 24rpx rgba(22, 48, 43, 0.06);
}
</style>
