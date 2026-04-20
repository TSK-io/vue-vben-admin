<template>
  <view class="ss-page ss-page--with-nav ss-page--with-tabbar settings-page">
    <app-nav-bar title="我的" subtitle="账号信息、适老化设置和提醒方式统一放在这里。" />

    <app-card class="intro-card ss-fade-up ss-stagger-1">
      <text class="intro-title">{{ profileName }}</text>
      <text class="intro-desc">把账号信息、阅读体验和提醒方式放在一个固定入口，减少来回找页面。</text>
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
          <switch :checked="settings.contrastMode" :color="switchColor" @change="toggleContrast" />
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
          <switch :checked="settings.simplifyMode" :color="switchColor" @change="toggleSimplifyMode" />
        </view>
        <view class="ss-list-cell setting-cell">
          <view class="setting-copy">
            <text class="setting-title">语音播报</text>
            <text class="setting-desc">看不清时，可以点按钮让页面读出来。</text>
          </view>
          <switch :checked="settings.voiceBroadcastReserved" :color="switchColor" @change="toggleVoiceReserved" />
        </view>
      </view>
    </app-section>

    <app-card class="intro-card ss-fade-up ss-stagger-4">
      <text class="intro-title">账号</text>
      <text class="intro-desc">手机号：{{ store.profile?.phone || '未加载' }}</text>
      <button class="ss-secondary-button logout-button" @click="logout">退出登录</button>
    </app-card>

    <app-tab-bar role="elder" current="me" />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppCard from '@/components/app/AppCard.vue'
import AppNavBar from '@/components/app/AppNavBar.vue'
import AppSection from '@/components/app/AppSection.vue'
import AppTabBar from '@/components/app/AppTabBar.vue'
import { useAppStore } from '@/store/app'
import { relaunchTo } from '@/utils/navigation'
import type { ElderSettings } from '@/types/app'

const store = useAppStore()
const settings = computed(() => store.elderSettings)
const switchColor = 'var(--ss-color-primary)'
const profileName = computed(() => store.profile?.name || '当前账号')

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

function logout() {
  store.logout()
  relaunchTo('/pages/auth/login')
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
  background: var(--ss-color-surface-soft);
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
  background: rgba(255, 255, 255, 0.96);
  color: var(--ss-color-text);
  font-weight: 700;
  box-shadow: var(--ss-shadow-soft);
}

.logout-button {
  margin-top: 8rpx;
}
</style>
