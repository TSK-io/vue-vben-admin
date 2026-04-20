<template>
  <view class="topbar">
    <button v-if="showBack" class="back-button" @click="goBack">‹</button>
    <view v-else class="right-slot" />
    <view class="copy-block">
      <text class="title">{{ title }}</text>
      <text v-if="subtitle" class="subtitle">{{ subtitle }}</text>
    </view>
    <view class="right-slot">
      <slot name="right" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { backPage } from '@/utils/navigation'

withDefaults(defineProps<{
  title: string
  subtitle?: string
  showBack?: boolean
}>(), {
  showBack: false,
})

function goBack() {
  backPage()
}
</script>

<style scoped lang="scss">
.topbar {
  display: flex;
  align-items: center;
  gap: 18rpx;
  min-height: 96rpx;
}

.copy-block {
  flex: 1;
  min-width: 0;
}

.title {
  display: block;
  font-size: var(--ss-font-size-title);
  font-weight: 700;
  letter-spacing: var(--ss-letter-spacing-tight);
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}

.back-button {
  width: 72rpx;
  min-width: 72rpx;
  min-height: 72rpx;
  padding: 0;
  border: 1.5rpx solid rgba(148, 163, 184, 0.18);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.72);
  color: var(--ss-color-primary);
  font-size: 40rpx;
  line-height: 1;
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.06);
}

.right-slot {
  width: 72rpx;
  min-width: 72rpx;
}
</style>
