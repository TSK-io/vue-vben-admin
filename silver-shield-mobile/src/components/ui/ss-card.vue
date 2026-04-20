<template>
  <view class="ss-card">
    <slot />
  </view>
</template>

<style scoped lang="scss">
.ss-card {
  position: relative;
  overflow: hidden;
  background: var(--ss-color-surface);
  border: var(--ss-glass-border);
  border-radius: var(--ss-card-radius);
  box-shadow: var(--ss-shadow-card);
  backdrop-filter: var(--ss-backdrop-blur);
  padding: 30rpx;
}

.ss-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 120rpx;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.42), transparent);
  pointer-events: none;
}
</style>
