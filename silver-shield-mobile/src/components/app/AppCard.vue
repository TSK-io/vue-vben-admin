<template>
  <view class="app-card ss-glass-card" :class="cardClass">
    <slot />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  padding?: 'none' | 'sm' | 'md' | 'lg'
  elevated?: boolean
}>(), {
  padding: 'md',
  elevated: false,
})

const cardClass = computed(() => [
  `app-card--${props.padding}`,
  { 'app-card--elevated': props.elevated },
])
</script>

<style scoped lang="scss">
.app-card {
  position: relative;
  overflow: hidden;
}

.app-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 120rpx;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.42), transparent);
  pointer-events: none;
}

.app-card--none {
  padding: 0;
}

.app-card--sm {
  padding: 24rpx;
}

.app-card--md {
  padding: 30rpx;
}

.app-card--lg {
  padding: 36rpx;
}

.app-card--elevated {
  box-shadow: var(--ss-shadow-floating);
}
</style>
