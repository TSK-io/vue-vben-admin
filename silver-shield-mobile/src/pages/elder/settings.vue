<template>
  <view class="ss-page ss-page--with-nav settings-page">
    <app-nav-bar title="设置" subtitle="参考 iOS Settings，用分组列表来放常用开关。" show-back />

    <app-card class="intro-card ss-fade-up ss-stagger-1">
      <text class="intro-title">适老化与 Apple 风格一起保留</text>
      <text class="intro-desc">页面会更轻、更清楚，但不会为了好看牺牲字号、对比度和点击面积。</text>
    </app-card>

    <app-section class="group" title="显示" subtitle="先把阅读体验和识别效率相关的设置放在一起。">
      <view class="ss-list-group ss-fade-up ss-stagger-2">
        <view class="ss-list-cell setting-cell">
          <view class="setting-copy">
            <text class="setting-title">字体大小</text>
            <text class="setting-desc">看着吃力时，直接切成更大的字。</text>
          </view>
          <view class="font-segmented">
            <button class="font-chip ss-pressable" :class="{ active: settings.fontScale === 'large' }" @click="setFontScale('large')">标准</button>
            <button class="font-chip ss-pressable" :class="{ active: settings.fontScale === 'x-large' }" @click="setFontScale('x-large')">更大</button>
          </view>
        </view>
        <view class="ss-list-cell setting-cell">
          <view class="setting-copy">
            <text class="setting-title">颜色更清楚</text>
            <text class="setting-desc">重要信息会更醒目，更容易一眼看到。</text>
          </view>
          <switch :checked="settings.contrastMode" color="#2563eb" @change="toggleContrast" />
        </view>
      </view>
    </app-section>

    <app-section class="group" title="首页与提醒" subtitle="影响首页结构、提醒方式和老人使用负担。">
      <view class="ss-list-group ss-fade-up ss-stagger-3">
        <view class="ss-list-cell setting-cell">
          <view class="setting-copy">
            <text class="setting-title">首页更简单</text>
            <text class="setting-desc">打开后，首页只留最常用的入口，少走几步。</text>
          </view>
          <switch :checked="settings.simplifyMode" color="#2563eb" @change="toggleSimplifyMode" />
        </view>
        <view class="ss-list-cell setting-cell">
          <view class="setting-copy">
            <text class="setting-title">语音播报</text>
            <text class="setting-desc">看不清时，可以点按钮让页面读出来。</text>
          </view>
          <switch :checked="settings.voiceBroadcastReserved" color="#2563eb" @change="toggleVoiceReserved" />
        </view>
      </view>
    </app-section>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppCard from '@/components/app/AppCard.vue'
import AppNavBar from '@/components/app/AppNavBar.vue'
import AppSection from '@/components/app/AppSection.vue'
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
.intro-card {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.intro-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}

.intro-desc {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}

.group {
  gap: 14rpx;
}

.setting-cell {
  justify-content: space-between;
}

.setting-copy {
  flex: 1;
  min-width: 0;
}

.setting-title {
  display: block;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}

.setting-desc {
  display: block;
  margin-top: 6rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}

.font-segmented {
  display: inline-flex;
  gap: 8rpx;
  padding: 8rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(241, 245, 249, 0.95);
}

.font-chip {
  min-width: 100rpx;
  min-height: 54rpx;
  padding: 0 18rpx;
  border: none;
  border-radius: var(--ss-pill-radius);
  background: transparent;
  color: var(--ss-color-subtext);
  font-size: var(--ss-font-size-caption);
}

.font-chip.active {
  background: #fff;
  color: var(--ss-color-text);
  font-weight: 700;
  box-shadow: 0 8rpx 18rpx rgba(15, 23, 42, 0.08);
}
</style>
