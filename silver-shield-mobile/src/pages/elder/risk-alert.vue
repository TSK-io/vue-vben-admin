<template>
  <view class="ss-page risk-page">
    <ss-topbar title="风险提醒" subtitle="只告诉你先做什么，不让页面变成复杂说明书。" show-back />

    <ss-card v-if="topRisk" class="hero-card">
      <text class="hero-badge">重要提醒</text>
      <text class="hero-title">{{ topRisk.title }}</text>
      <text class="hero-summary">{{ topRisk.summary }}</text>
      <view class="steps-card">
        <text class="steps-title">现在先做这 3 件事</text>
        <text class="steps-item">1. 不转账</text>
        <text class="steps-item">2. 不点陌生链接</text>
        <text class="steps-item">3. 立刻联系家人</text>
      </view>
    </ss-card>

    <ss-voice-bar
      :enabled="store.elderSettings.voiceBroadcastReserved"
      :text="topRisk ? `${topRisk.title}。${topRisk.summary}` : '这里可以把提醒读出来。'"
    />

    <ss-card v-if="topRisk">
      <ss-section-title title="为什么提醒你" />
      <text class="block-text">{{ topRisk.reason || '这条内容看起来不太安全，先不要继续操作。' }}</text>
    </ss-card>

    <ss-card v-if="topRisk">
      <ss-section-title title="下一步" subtitle="先把动作做对，比先看懂分析更重要。" />
      <text class="block-text">{{ topRisk.suggestion || '先联系家人，让熟悉的人帮你看一眼。' }}</text>
      <view class="action-group">
        <button class="ss-primary-button" @click="goChat">给家人发消息</button>
        <button class="ss-secondary-button" @click="goContacts">查看联系人</button>
      </view>
    </ss-card>

    <ss-feedback-state
      v-if="!topRisk"
      empty
      empty-title="当前没有新的风险提醒"
      empty-description="如果收到可疑消息或电话，页面会在这里提醒你先停一下。"
    />

    <button class="ss-danger-button bottom-button" @click="goChat">联系家人</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const topRisk = computed(() => store.latestHighRisk)

function goChat() {
  store.selectContact('guardian-li')
  openPage('/pages/elder/chat')
}

function goContacts() {
  openPage('/pages/elder/contacts')
}
</script>

<style scoped lang="scss">
.hero-card {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.hero-badge {
  width: fit-content;
  padding: 10rpx 18rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(254, 226, 226, 0.96);
  color: #b91c1c;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.hero-title {
  font-size: var(--ss-font-size-hero);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: var(--ss-letter-spacing-tight);
}

.hero-summary,
.block-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}

.steps-card {
  margin-top: 8rpx;
  padding: 24rpx;
  border-radius: 28rpx;
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: var(--ss-shadow-strong);
}

.steps-title {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}

.steps-item {
  display: block;
  margin-top: 10rpx;
  font-size: var(--ss-font-size-body);
}

.action-group {
  display: flex;
  gap: 14rpx;
  margin-top: 18rpx;
}

.action-group button {
  flex: 1;
}

.bottom-button {
  margin-top: auto;
}
</style>
