<template>
  <view class="ss-page ss-page--with-nav ss-page--with-bottom-bar conversations-page">
    <app-nav-bar title="最近消息" subtitle="像 iMessage 一样，只把最近联系的人清楚地列出来。" show-back />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="这里可以读出最近消息和联系人名字。" />

    <app-card class="filter-bar ss-fade-up ss-stagger-1" padding="sm">
      <text class="filter-title">会话</text>
      <view class="segmented">
        <text class="segment active">全部</text>
        <text class="segment">重点</text>
      </view>
    </app-card>

    <ss-feedback-state
      v-if="!sessions.length"
      empty
      empty-title="还没有最近消息"
      empty-description="和家人聊过天以后，这里会显示最近联系的人。"
    />

    <view v-else class="conversation-group ss-list-group ss-fade-up">
      <app-list-cell
        v-for="session in sessions"
        :key="session.contactId"
        class="conversation-cell ss-fade-up"
        :title="session.name"
        :description="session.relation"
        :meta="session.lastMessageTime"
        :avatar-text="session.avatarText"
        @click="openChat(session.contactId)"
      >
        <template #secondary>
          <text class="preview">{{ messageTypeLabel(session.messageType) }}{{ session.lastMessage }}</text>
        </template>
        <template #titleSuffix>
          <text v-if="session.hasRisk" class="ss-chip ss-chip-warn">先确认</text>
        </template>
        <template #trailing>
          <text v-if="session.unreadCount" class="unread">{{ session.unreadCount }}</text>
        </template>
      </app-list-cell>
    </view>

    <app-bottom-action-bar>
      <button class="ss-secondary-button bottom-button" @click="openPage('/pages/elder/home')">回到首页</button>
    </app-bottom-action-bar>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppBottomActionBar from '@/components/app/AppBottomActionBar.vue'
import AppCard from '@/components/app/AppCard.vue'
import AppListCell from '@/components/app/AppListCell.vue'
import AppNavBar from '@/components/app/AppNavBar.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
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
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 20rpx 24rpx;
}

.filter-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}

.segmented {
  display: inline-flex;
  gap: 8rpx;
  padding: 8rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(255, 255, 255, 0.8);
}

.segment {
  min-height: 52rpx;
  padding: 0 22rpx;
  border-radius: var(--ss-pill-radius);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-subtext);
}

.segment.active {
  background: #fff;
  color: var(--ss-color-text);
  font-weight: 700;
  box-shadow: 0 8rpx 18rpx rgba(15, 23, 42, 0.08);
}

.preview {
  font-size: var(--ss-font-size-body);
  color: var(--ss-color-subtext);
  line-height: 1.5;
}

.unread {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42rpx;
  height: 42rpx;
  padding: 0 10rpx;
  border-radius: var(--ss-pill-radius);
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.bottom-button {
  flex: 1;
}
</style>
