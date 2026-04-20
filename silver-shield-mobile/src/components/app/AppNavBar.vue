<template>
  <view class="app-nav" :class="[`app-nav--${align}`]">
    <view class="app-nav__status-spacer" />
    <view class="app-nav__main">
      <button v-if="showBack" class="app-nav__button" @click="goBack">‹</button>
      <view v-else class="app-nav__placeholder" />

      <view class="app-nav__copy">
        <text class="app-nav__title">{{ title }}</text>
        <text v-if="subtitle" class="app-nav__subtitle">{{ subtitle }}</text>
      </view>

      <view class="app-nav__right">
        <slot name="right" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { backPage } from '@/utils/navigation'

withDefaults(defineProps<{
  title: string
  subtitle?: string
  showBack?: boolean
  align?: 'start' | 'center'
}>(), {
  subtitle: '',
  showBack: false,
  align: 'start',
})

function goBack() {
  backPage()
}
</script>

<style scoped lang="scss">
.app-nav {
  position: relative;
  z-index: 2;
}

.app-nav__status-spacer {
  height: var(--ss-safe-top);
}

.app-nav__main {
  min-height: var(--ss-nav-height);
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.app-nav__copy {
  flex: 1;
  min-width: 0;
}

.app-nav--center .app-nav__copy {
  text-align: center;
}

.app-nav__title {
  display: block;
  font-size: var(--ss-font-size-title);
  font-weight: var(--ss-font-weight-bold);
  letter-spacing: var(--ss-letter-spacing-tight);
  color: var(--ss-color-text-strong);
}

.app-nav__subtitle {
  display: block;
  margin-top: 6rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}

.app-nav__button,
.app-nav__placeholder,
.app-nav__right {
  width: 72rpx;
  min-width: 72rpx;
}

.app-nav__button {
  min-height: 72rpx;
  padding: 0;
  border: var(--ss-hairline);
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.9);
  color: var(--ss-color-primary);
  font-size: 36rpx;
  line-height: 1;
  box-shadow: var(--ss-shadow-soft);
}

.app-nav__right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>
