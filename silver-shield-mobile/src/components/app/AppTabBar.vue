<template>
  <view class="app-tabbar">
    <view class="app-tabbar__inner ss-glass-card">
      <button
        v-for="item in items"
        :key="item.key"
        class="app-tabbar__item"
        :class="{ 'app-tabbar__item--active': item.key === current }"
        @click="go(item.path)"
      >
        <text class="app-tabbar__label">{{ item.label }}</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { openPrimaryTab } from '@/utils/navigation'

type TabKey = 'conversations' | 'contacts' | 'alerts' | 'me'

const props = defineProps<{
  role: 'elder' | 'guardian'
  current: TabKey
}>()

const items = computed(() => {
  if (props.role === 'elder') {
    return [
      { key: 'conversations', label: '会话', path: '/pages/elder/conversations' },
      { key: 'contacts', label: '联系人', path: '/pages/elder/contacts' },
      { key: 'alerts', label: '提醒', path: '/pages/elder/risk-alert' },
      { key: 'me', label: '我的', path: '/pages/elder/settings' },
    ] as const
  }

  return [
    { key: 'conversations', label: '会话', path: '/pages/guardian/conversations' },
    { key: 'contacts', label: '老人', path: '/pages/guardian/elders' },
    { key: 'alerts', label: '提醒', path: '/pages/guardian/risk-list' },
    { key: 'me', label: '我的', path: '/pages/guardian/home' },
  ] as const
})

function go(path: string) {
  openPrimaryTab(path)
}
</script>

<style scoped lang="scss">
.app-tabbar {
  position: sticky;
  bottom: 0;
  z-index: 30;
  margin-top: auto;
  padding-top: 12rpx;
  padding-bottom: calc(18rpx + var(--ss-safe-bottom));
}

.app-tabbar__inner {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10rpx;
  padding: 14rpx;
  border-radius: 30rpx;
}

.app-tabbar__item {
  min-height: 84rpx;
  padding: 0 10rpx;
  border-radius: 22rpx;
  background: transparent;
  color: var(--ss-color-subtext);
  box-shadow: none;
}

.app-tabbar__item--active {
  background: var(--ss-color-surface-soft);
  color: var(--ss-color-text-strong);
}

.app-tabbar__label {
  font-size: var(--ss-font-size-body-sm);
  font-weight: var(--ss-font-weight-semibold);
}
</style>
