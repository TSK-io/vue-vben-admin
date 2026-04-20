<template>
  <view class="page-shell">
    <ss-topbar title="先别操作" subtitle="只告诉你现在该怎么做，不讲复杂分析。" show-back />

    <ss-card v-if="topRisk">
      <view class="hero-alert">
        <text class="risk-badge">重要提醒</text>
        <text class="risk-title">{{ topRisk.title }}</text>
        <text class="risk-summary">{{ topRisk.summary }}</text>
        <view class="strong-warning">
          <text class="warning-title">现在先做这 3 件事</text>
          <text class="warning-step">1. 不转账</text>
          <text class="warning-step">2. 不点陌生链接</text>
          <text class="warning-step">3. 立刻联系家人</text>
        </view>
      </view>
    </ss-card>

    <ss-voice-bar
      :enabled="store.elderSettings.voiceBroadcastReserved"
      :text="topRisk ? `${topRisk.title}。${topRisk.summary}` : '这里可以把提醒读出来。'"
    />

    <ss-card v-if="topRisk">
      <ss-section-title title="简单说" />
      <text class="block-text">{{ topRisk.reason || '这条内容看起来不太安全，先不要继续操作。' }}</text>
    </ss-card>

    <ss-card v-if="topRisk">
      <ss-section-title title="接下来怎么做" />
      <text class="block-text">{{ topRisk.suggestion || '先联系家人，让熟悉的人帮你看一眼。' }}</text>
      <view class="action-group">
        <button class="mini-action primary" @click="goChat">给家人发消息</button>
        <button class="mini-action" @click="goContacts">查看联系人</button>
      </view>
    </ss-card>

    <ss-feedback-state
      v-if="!topRisk"
      empty
      empty-title="当前没有新的风险提醒"
      empty-description="如果收到可疑消息或电话，页面会在这里提醒你先停一下。"
    />

    <button class="cta-button" @click="goChat">联系家人</button>
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
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background:
    radial-gradient(circle at top left, rgba(255, 219, 214, 0.55), transparent 24%),
    #fbf1ee;
}
.hero-alert {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 8rpx;
}
.risk-badge {
  width: fit-content;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: #fee2e2;
  color: #991b1b;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
.risk-title {
  font-size: var(--ss-font-size-title);
  font-weight: 700;
}
.risk-summary,
.block-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.strong-warning {
  margin-top: 8rpx;
  padding: 22rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
  color: #fff;
  box-shadow: var(--ss-shadow-strong);
}
.warning-title {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.warning-step {
  display: block;
  margin-top: 10rpx;
  font-size: var(--ss-font-size-body);
}
.block-meta {
  display: block;
  margin-top: 12rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.action-group {
  display: flex;
  gap: 14rpx;
  margin-top: 18rpx;
}
.mini-action {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: #f5efe4;
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
}
.mini-action.primary {
  background: var(--ss-color-primary);
  color: #fff;
}
.cta-button {
  margin-top: 12rpx;
  border: none;
  border-radius: 20rpx;
  background: var(--ss-color-danger);
  color: #fff;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
</style>
