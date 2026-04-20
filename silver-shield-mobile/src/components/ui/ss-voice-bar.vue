<template>
  <view v-if="enabled" class="voice-bar ss-voice-anchor">
    <view class="voice-copy">
      <text class="voice-title">语音播报</text>
      <text class="voice-text">{{ text }}</text>
    </view>
    <button class="voice-button" @click="announce">播报</button>
  </view>
</template>

<script setup lang="ts">
const props = defineProps<{
  enabled: boolean
  text: string
}>()

function announce() {
  uni.showToast({
    title: `正在播报：${props.text.slice(0, 8)}`,
    icon: 'none',
    duration: 1800,
  })
}
</script>

<style scoped lang="scss">
.voice-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 22rpx 24rpx;
  border-radius: 28rpx;
  background: rgba(231, 240, 255, 0.7);
  box-shadow: 0 12rpx 28rpx rgba(37, 99, 235, 0.08);
  backdrop-filter: blur(14rpx);
}

.voice-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.voice-title {
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
  color: var(--ss-color-primary);
}

.voice-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-text);
}

.voice-button {
  min-width: 148rpx;
  border: none;
  border-radius: 22rpx;
  background: linear-gradient(180deg, #60a5fa 0%, var(--ss-color-primary) 100%);
  color: #fff;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
  box-shadow: 0 12rpx 24rpx rgba(37, 99, 235, 0.18);
}
</style>
