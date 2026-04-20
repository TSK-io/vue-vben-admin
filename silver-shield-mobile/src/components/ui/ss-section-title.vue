<template>
  <view class="section-title-wrap">
    <view class="heading-row">
      <view class="copy">
        <text class="section-title">{{ title }}</text>
        <text v-if="subtitle" class="section-subtitle">{{ subtitle }}</text>
      </view>
      <view class="action">
        <slot name="action" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped lang="scss">
.section-title-wrap {
  display: flex;
  flex-direction: column;
}

.heading-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
}

.copy {
  flex: 1;
  min-width: 0;
}

.section-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  letter-spacing: var(--ss-letter-spacing-tight);
  color: var(--ss-color-text);
}

.section-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}

.action {
  flex-shrink: 0;
}
</style>
