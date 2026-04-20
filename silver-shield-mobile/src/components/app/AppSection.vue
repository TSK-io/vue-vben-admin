<template>
  <view class="app-section">
    <view v-if="title || subtitle || $slots.action" class="app-section__head">
      <view class="app-section__copy">
        <text v-if="eyebrow" class="app-section__eyebrow">{{ eyebrow }}</text>
        <text v-if="title" class="app-section__title">{{ title }}</text>
        <text v-if="subtitle" class="app-section__subtitle">{{ subtitle }}</text>
      </view>
      <view v-if="$slots.action" class="app-section__action">
        <slot name="action" />
      </view>
    </view>
    <slot />
  </view>
</template>

<script setup lang="ts">
defineProps<{
  eyebrow?: string
  title?: string
  subtitle?: string
}>()
</script>

<style scoped lang="scss">
.app-section {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.app-section__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
}

.app-section__copy {
  flex: 1;
  min-width: 0;
}

.app-section__eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 44rpx;
  padding: 0 16rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(255, 255, 255, 0.62);
  color: var(--ss-color-primary);
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.app-section__title {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  letter-spacing: var(--ss-letter-spacing-tight);
  color: var(--ss-color-text);
}

.app-section__eyebrow + .app-section__title {
  margin-top: 16rpx;
}

.app-section__subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}

.app-section__action {
  flex-shrink: 0;
}
</style>
