<template>
  <view class="ss-page">
    <ss-topbar title="最近通话" subtitle="只看最近联系过谁，结果一眼能看懂。" show-back />

    <ss-feedback-state
      v-if="!records.length"
      empty
      empty-title="还没有通话记录"
      empty-description="打过电话以后，这里会自动显示最近的通话。"
    />

    <ss-card v-for="record in records" :key="record.id" class="ss-fade-up">
      <view class="record-card">
        <view class="top-row">
          <text class="name">{{ record.contactName }}</text>
          <text class="summary-tag" :class="record.status">{{ statusLabel(record.status) }}</text>
        </view>
        <text class="meta">{{ directionLabel(record.direction) }} · {{ record.startedAt }}</text>
        <text class="meta">通话时长 {{ record.durationLabel }}</text>
        <text class="summary">{{ summaryLabel(record) }}</text>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import type { CallDirection, CallRecord, CallStatus } from '@/types/app'

const store = useAppStore()
const records = computed(() => store.elderCallRecords)

function directionLabel(direction: CallDirection) {
  return direction === 'incoming' ? '呼入' : '呼出'
}

function statusLabel(status: CallStatus) {
  const map: Record<string, string> = {
    ended: '已完成',
    failed: '异常中断',
    missed: '未接通',
    rejected: '已拒接',
  }

  return map[status] || status
}

function summaryLabel(record: CallRecord) {
  if (record.status === 'missed') {
    return '这次没有接通，可以稍后再打。'
  }

  if (record.status === 'failed') {
    return '通话中断了，建议换个时间再联系。'
  }

  return record.summaryText || '这次通话已结束。'
}
</script>

<style scoped lang="scss">
.meta,
.summary {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.record-card {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}
.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.summary-tag {
  width: fit-content;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #eef2f7;
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-text);
}
.summary-tag.ended {
  background: #dff7f2;
  color: var(--ss-color-primary);
}
.summary-tag.missed,
.summary-tag.failed,
.summary-tag.rejected {
  background: #fff0d2;
  color: #8a5a00;
}
</style>
