<template>
  <view class="app-list-cell ss-list-cell" :class="cellClass" @click="handleClick">
    <view v-if="$slots.leading || avatarText" class="app-list-cell__leading">
      <slot name="leading">
        <view class="app-list-cell__avatar">{{ avatarText }}</view>
      </slot>
    </view>

    <view class="app-list-cell__body">
      <view class="app-list-cell__row">
        <view class="app-list-cell__title-wrap">
          <text class="app-list-cell__title">{{ title }}</text>
          <slot name="titleSuffix" />
        </view>
        <view v-if="$slots.meta || meta" class="app-list-cell__meta">
          <slot name="meta">
            <text class="app-list-cell__meta-text">{{ meta }}</text>
          </slot>
        </view>
      </view>

      <view v-if="description || secondary || $slots.description || $slots.secondary" class="app-list-cell__row app-list-cell__row--sub">
        <view class="app-list-cell__description-wrap">
          <slot name="description">
            <text v-if="description" class="app-list-cell__description">{{ description }}</text>
          </slot>
        </view>
        <view v-if="$slots.secondary || secondary" class="app-list-cell__secondary">
          <slot name="secondary">
            <text class="app-list-cell__secondary-text">{{ secondary }}</text>
          </slot>
        </view>
      </view>

      <slot />
    </view>

    <view v-if="$slots.trailing" class="app-list-cell__trailing">
      <slot name="trailing" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  title: string
  description?: string
  secondary?: string
  meta?: string
  avatarText?: string
  compact?: boolean
  align?: 'start' | 'center'
  clickable?: boolean
}>(), {
  description: '',
  secondary: '',
  meta: '',
  avatarText: '',
  compact: false,
  align: 'center',
  clickable: true,
})

const emit = defineEmits<{
  click: []
}>()

const cellClass = computed(() => ({
  'app-list-cell--compact': props.compact,
  'app-list-cell--start': props.align === 'start',
  'app-list-cell--clickable': props.clickable,
}))

function handleClick() {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped lang="scss">
.app-list-cell {
  border-radius: 26rpx;
}

.app-list-cell--start {
  align-items: flex-start;
}

.app-list-cell--compact {
  padding-top: 22rpx;
  padding-bottom: 22rpx;
}

.app-list-cell--clickable:active {
  transform: scale(0.988);
}

.app-list-cell__leading {
  flex-shrink: 0;
}

.app-list-cell__avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
  color: var(--ss-color-primary);
  font-size: 30rpx;
  font-weight: 700;
}

.app-list-cell__body {
  flex: 1;
  min-width: 0;
}

.app-list-cell__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14rpx;
}

.app-list-cell__row--sub {
  margin-top: 8rpx;
  align-items: flex-start;
}

.app-list-cell__title-wrap,
.app-list-cell__description-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}

.app-list-cell__title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  color: var(--ss-color-text);
}

.app-list-cell__description,
.app-list-cell__secondary-text,
.app-list-cell__meta-text {
  font-size: var(--ss-font-size-caption);
  line-height: 1.55;
  color: var(--ss-color-subtext);
}

.app-list-cell__secondary,
.app-list-cell__meta,
.app-list-cell__trailing {
  flex-shrink: 0;
}

.app-list-cell__trailing {
  display: flex;
  align-items: center;
}
</style>
