<template>
  <view class="app-bottom-action-bar">
    <view class="app-bottom-action-bar__inner ss-glass-card">
      <slot />
    </view>
  </view>
</template>

<style scoped lang="scss">
.app-bottom-action-bar {
  position: sticky;
  bottom: 0;
  z-index: 20;
  margin-top: auto;
  padding-top: 12rpx;
  padding-bottom: var(--ss-bottom-bar-padding);
}

.app-bottom-action-bar__inner {
  display: flex;
  align-items: center;
  gap: 16rpx;
  min-height: var(--ss-bottom-action-height);
  padding: 16rpx 18rpx;
  border-radius: var(--ss-bottom-bar-radius);
}
</style>
