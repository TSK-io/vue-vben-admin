<template>
  <view class="page-shell">
    <ss-topbar title="页面设置" subtitle="只保留老人真正会用到的几个开关。" show-back />

    <ss-card>
      <ss-section-title title="字要更大吗" subtitle="看着吃力时，直接切成更大的字。" />
      <view class="option-row">
        <button class="option-btn" :class="{ active: settings.fontScale === 'large' }" @click="setFontScale('large')">已经够大</button>
        <button class="option-btn" :class="{ active: settings.fontScale === 'x-large' }" @click="setFontScale('x-large')">再大一点</button>
      </view>
    </ss-card>

    <view class="setting-card">
      <view class="setting-copy">
        <text class="setting-title">首页更简单</text>
        <text class="setting-desc">打开后，首页只留最常用的入口，少走几步。</text>
      </view>
      <switch :checked="settings.simplifyMode" color="#0f766e" @change="toggleSimplifyMode" />
    </view>

    <view class="setting-card">
      <view class="setting-copy">
        <text class="setting-title">颜色更清楚</text>
        <text class="setting-desc">重要信息会更醒目，更容易一眼看到。</text>
      </view>
      <switch :checked="settings.contrastMode" color="#0f766e" @change="toggleContrast" />
    </view>

    <view class="setting-card">
      <view class="setting-copy">
        <text class="setting-title">打开语音播报</text>
        <text class="setting-desc">看不清时，可以点按钮让页面读出来。</text>
      </view>
      <switch :checked="settings.voiceBroadcastReserved" color="#0f766e" @change="toggleVoiceReserved" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import type { ElderSettings } from '@/types/app'

const store = useAppStore()
const settings = computed(() => store.elderSettings)

function setFontScale(fontScale: ElderSettings['fontScale']) {
  store.updateElderSettings({ fontScale })
}

function toggleContrast(event: Event) {
  store.updateElderSettings({ contrastMode: getSwitchValue(event) })
}

function toggleVoiceReserved(event: Event) {
  store.updateElderSettings({ voiceBroadcastReserved: getSwitchValue(event) })
}

function toggleSimplifyMode(event: Event) {
  store.updateElderSettings({ simplifyMode: getSwitchValue(event) })
}

function getSwitchValue(event: Event) {
  const detail = event as Event & { detail?: { value?: boolean } }
  const target = event.target as HTMLInputElement | null

  return typeof detail.detail?.value === 'boolean'
    ? detail.detail.value
    : Boolean(target?.checked)
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
    radial-gradient(circle at top right, rgba(223, 247, 242, 0.45), transparent 24%),
    #f5f3eb;
}
.option-row {
  display: flex;
  gap: 14rpx;
  margin-top: 18rpx;
}
.option-btn {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: #eef2f7;
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
}
.option-btn.active {
  background: var(--ss-color-primary);
  color: #fff;
}
.setting-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  padding: 28rpx 26rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 12rpx 24rpx rgba(22, 48, 43, 0.06);
}
.setting-copy {
  flex: 1;
}
.setting-title {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  color: var(--ss-color-text);
}
.setting-desc {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
</style>
