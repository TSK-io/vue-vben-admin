<template>
  <view class="ss-page home-page">
    <ss-topbar :title="`您好，${displayName}`" subtitle="把重要的人和重要的事放在最前面。" />

    <view class="hero ss-glass-card ss-fade-up ss-stagger-1">
      <view class="hero-copy">
        <text class="eyebrow">今天优先看这里</text>
        <text class="hero-title">{{ topRisk ? topRisk.title : '今天整体平稳，可以安心联系家人' }}</text>
        <text class="hero-desc">{{ topRisk?.summary || '最近会话、风险提醒和求助入口都已经放到首页，少找一步。' }}</text>
      </view>
      <view class="hero-side">
        <text class="hero-pill" :class="hasHighRisk ? 'danger' : 'safe'">{{ hasHighRisk ? '高风险提醒' : '状态平稳' }}</text>
        <button class="hero-action ss-pressable" @click="openPage('/pages/elder/risk-alert')">{{ hasHighRisk ? '立即查看' : '查看提醒' }}</button>
      </view>
    </view>

    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" :text="voiceSummary" />

    <ss-card class="section-card ss-fade-up ss-stagger-2">
      <ss-section-title title="最近会话" subtitle="先看最近联系的人，减少来回找入口。">
        <template #action>
          <text class="action-link" @click="openPage('/pages/elder/conversations')">全部</text>
        </template>
      </ss-section-title>
      <view v-if="recentSessions.length" class="recent-list">
        <view v-for="session in recentSessions" :key="session.contactId" class="recent-item ss-pressable" @click="openChat(session.contactId)">
          <view class="recent-avatar">{{ session.avatarText }}</view>
          <view class="recent-main">
            <view class="recent-row">
              <text class="recent-name">{{ session.name }}</text>
              <text v-if="session.hasRisk" class="ss-chip ss-chip-warn">先确认</text>
            </view>
            <text class="recent-preview">{{ messageTypeLabel(session.messageType) }}{{ session.lastMessage }}</text>
          </view>
          <view class="recent-side">
            <text class="recent-time">{{ session.lastMessageTime }}</text>
            <text v-if="session.unreadCount" class="recent-unread">{{ session.unreadCount }}</text>
          </view>
        </view>
      </view>
      <view v-else class="empty-inline">
        <text class="empty-inline-text">和家人聊过天以后，这里会自动显示最近消息。</text>
      </view>
    </ss-card>

    <ss-card class="section-card ss-fade-up ss-stagger-3">
      <ss-section-title title="常用操作" subtitle="常用功能只保留 4 个最关键入口。" />
      <view class="quick-grid">
        <button class="quick-button primary ss-pressable" @click="chatWithGuardian">
          <text class="quick-title">发消息</text>
          <text class="quick-desc">直接联系女儿</text>
        </button>
        <button class="quick-button soft ss-pressable" @click="callGuardian">
          <text class="quick-title">打电话</text>
          <text class="quick-desc">一键语音联系</text>
        </button>
        <button class="quick-button warm ss-pressable" @click="openPage('/pages/elder/contacts')">
          <text class="quick-title">联系人</text>
          <text class="quick-desc">查看家人电话</text>
        </button>
        <button class="quick-button danger ss-pressable ss-pulse-soft" @click="submitSos">
          <text class="quick-title">一键求助</text>
          <text class="quick-desc">紧急情况快速求助</text>
        </button>
      </view>
    </ss-card>

    <view class="summary-row ss-fade-up ss-stagger-4">
      <view class="summary-card ss-glass-card">
        <text class="summary-value">{{ contactsCount }}</text>
        <text class="summary-label">联系人</text>
      </view>
      <view class="summary-card ss-glass-card">
        <text class="summary-value">{{ riskCount }}</text>
        <text class="summary-label">提醒</text>
      </view>
      <view class="summary-card ss-glass-card">
        <text class="summary-value">{{ sosCount }}</text>
        <text class="summary-label">求助</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'
import type { MessageType } from '@/types/app'

const store = useAppStore()
void store.loadUserProfile()
store.setRole('elder')

const displayName = computed(() => store.elderName)
const topRisk = computed(() => store.latestHighRisk)
const hasHighRisk = computed(() => topRisk.value?.level === 'high')
const contactsCount = computed(() => store.contacts.length)
const riskCount = computed(() => store.riskRecords.length)
const sosCount = computed(() => store.sosCount)
const recentSessions = computed(() => store.chatSessions.filter((item) => !item.contactId.startsWith('elder-')).slice(0, 3))
const voiceSummary = computed(() => topRisk.value?.summary || '首页可以直接查看最近消息、风险提醒和一键求助。')

async function submitSos() {
  await store.submitSos()
  openPage('/pages/elder/sos-success')
}

function chatWithGuardian() {
  store.selectContact('guardian-li')
  openPage('/pages/elder/chat')
}

function callGuardian() {
  store.selectContact('guardian-li')
  store.startCall('guardian-li', 'elder', 'outgoing')
  openPage('/pages/elder/call')
}

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
.home-page {
  position: relative;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24rpx;
  padding: 34rpx 30rpx;
  background: rgba(255, 255, 255, 0.88);
}

.hero-copy {
  flex: 1;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 44rpx;
  padding: 0 16rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(255, 255, 255, 0.6);
  color: var(--ss-color-primary);
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.hero-title {
  display: block;
  margin-top: 16rpx;
  font-size: var(--ss-font-size-hero);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: var(--ss-letter-spacing-tight);
}

.hero-desc {
  display: block;
  margin-top: 14rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}

.hero-side {
  display: flex;
  min-width: 176rpx;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16rpx;
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 52rpx;
  padding: 0 18rpx;
  border-radius: var(--ss-pill-radius);
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.hero-pill.safe {
  background: rgba(220, 252, 231, 0.95);
  color: var(--ss-color-success);
}

.hero-pill.danger {
  background: rgba(254, 226, 226, 0.95);
  color: #b91c1c;
}

.hero-action {
  min-width: 156rpx;
  border: none;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.84);
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}

.section-card {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.action-link {
  color: var(--ss-color-primary);
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 24rpx;
  border-radius: 26rpx;
  background: rgba(255, 255, 255, 0.9);
  transition: transform var(--ss-duration-fast) var(--ss-ease-standard), box-shadow var(--ss-duration-fast) var(--ss-ease-standard);
}

.recent-avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
  color: var(--ss-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
}

.recent-main {
  flex: 1;
  min-width: 0;
}

.recent-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}

.recent-name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}

.recent-preview,
.recent-time {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.55;
  color: var(--ss-color-subtext);
}

.recent-side {
  min-width: 110rpx;
  text-align: right;
}

.recent-unread {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 40rpx;
  height: 40rpx;
  margin-top: 10rpx;
  padding: 0 10rpx;
  border-radius: var(--ss-pill-radius);
  background: var(--ss-color-danger);
  color: #fff;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.empty-inline {
  padding: 28rpx 0 4rpx;
}

.empty-inline-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.quick-button {
  min-height: 164rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 10rpx;
  padding: 24rpx;
  border: none;
  border-radius: 30rpx;
  text-align: left;
}

.quick-button.primary {
  background: linear-gradient(180deg, #ffffff 0%, #edf6ff 100%);
}

.quick-button.soft {
  background: linear-gradient(180deg, #ffffff 0%, #f2f8ff 100%);
}

.quick-button.warm {
  background: linear-gradient(180deg, #ffffff 0%, #fff4dc 100%);
}

.quick-button.danger {
  background: linear-gradient(180deg, #fff7f7 0%, #ffe5e5 100%);
}

.quick-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  color: var(--ss-color-text);
}

.quick-desc {
  font-size: var(--ss-font-size-caption);
  line-height: 1.5;
  color: var(--ss-color-subtext);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
}

.summary-card {
  padding: 26rpx 12rpx;
  text-align: center;
}

.summary-value {
  display: block;
  font-size: var(--ss-font-size-title);
  font-weight: 800;
  color: var(--ss-color-primary);
}

.summary-label {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-subtext);
}
</style>
