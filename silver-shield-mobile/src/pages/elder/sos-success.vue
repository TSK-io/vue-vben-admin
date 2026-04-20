<template>
  <view class="ss-page success-page">
    <ss-card class="result-card ss-pop-in">
      <view class="result-box">
        <view class="result-orb">
          <view class="result-core">✓</view>
        </view>
        <text class="result-title">求助已发送</text>
        <text class="result-desc">系统已经通知李女士和社区协助联系人，请保持电话畅通，不要继续和可疑对象交流。</text>
        <text class="result-meta">本次累计求助次数：{{ store.sosCount }}</text>
        <text v-if="latestSos?.linkedTicketNo" class="result-meta">主业务系统工单：{{ latestSos.linkedTicketNo }}</text>
        <text v-if="latestSos?.latestAction" class="result-meta">{{ latestSos.latestAction }}</text>
        <text v-if="store.mainServiceNotice" class="result-note">{{ store.mainServiceNotice }}</text>
      </view>
      <view class="action-group">
        <button class="primary-btn ss-pressable" @click="openPage('/pages/elder/chat')">立即给家属发消息</button>
        <button class="secondary-btn ss-pressable" @click="openPage('/pages/elder/home')">返回首页</button>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import SsCard from '@/components/ui/ss-card.vue'
import { computed } from 'vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const latestSos = computed(() => store.selectedSosAlert || store.activeSosAlerts[0])
</script>

<style scoped lang="scss">
.success-page {
  justify-content: center;
}
.result-card {
  background: rgba(255, 255, 255, 0.92);
}
.result-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16rpx;
}
.result-orb {
  width: 144rpx;
  height: 144rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle, rgba(220, 252, 231, 0.96) 0%, rgba(255, 255, 255, 0.9) 68%);
}
.result-core {
  width: 92rpx;
  height: 92rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #34d399 0%, #16a34a 100%);
  color: #fff;
  font-size: 46rpx;
  font-weight: 800;
  box-shadow: 0 18rpx 40rpx rgba(22, 163, 74, 0.24);
}
.result-title {
  font-size: 44rpx;
  font-weight: 700;
  color: var(--ss-color-text);
}
.result-desc,
.result-meta {
  font-size: 28rpx;
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.result-note {
  font-size: 24rpx;
  line-height: 1.6;
  color: #0f766e;
}
.action-group {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-top: 28rpx;
}
.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 700;
}
.primary-btn {
  background: linear-gradient(180deg, #3f9bff 0%, var(--ss-color-primary) 100%);
  color: #fff;
}
.secondary-btn {
  background: rgba(247, 248, 250, 0.98);
  color: var(--ss-color-text);
}
</style>
