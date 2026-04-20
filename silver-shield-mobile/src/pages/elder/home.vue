<template>
  <view class="page-shell">
    <ss-topbar title="您好，{{ displayName }}" subtitle="常用功能放前面，重要提醒一句话说清楚。" />

    <ss-card>
      <view class="alert-banner" :class="{ danger: hasHighRisk }" @click="openPage('/pages/elder/risk-alert')">
        <view class="banner-main">
          <text class="banner-tag">{{ hasHighRisk ? '重要提醒' : '今日提醒' }}</text>
          <text class="banner-title">{{ topRisk?.title || '今天暂时没有新的风险提醒' }}</text>
          <text class="banner-desc">{{ topRisk?.summary || '遇到转账、验证码、陌生链接，先不要操作，先问家人。' }}</text>
        </view>
        <view class="banner-side">
          <text class="banner-action">{{ hasHighRisk ? '查看提醒' : '查看详情' }}</text>
          <text v-if="hasHighRisk" class="banner-pulse">先别操作</text>
        </view>
      </view>
    </ss-card>

    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" :text="voiceSummary" />

    <ss-card>
      <ss-section-title title="常用操作" subtitle="平时最常用的几件事，都放在这里。" />
      <view class="action-grid">
        <button class="action-button action-primary" @click="chatWithGuardian">给女儿发消息</button>
        <button class="action-button action-soft" @click="callGuardian">给女儿打电话</button>
        <button class="action-button action-warm" @click="openPage('/pages/elder/contacts')">看家人电话</button>
        <button v-if="!store.elderSettings.simplifyMode" class="action-button action-neutral" @click="openPage('/pages/elder/conversations')">看最近消息</button>
        <button class="action-button action-danger" @click="submitSos">一键求助</button>
        <button class="action-button action-muted" @click="openPage('/pages/elder/settings')">页面设置</button>
      </view>
    </ss-card>

    <ss-card>
      <ss-section-title title="今天情况" />
      <view class="summary-list">
        <view class="summary-item">
          <text class="summary-num">{{ contactsCount }}</text>
          <text class="summary-label">常用联系人</text>
        </view>
        <view class="summary-item">
          <text class="summary-num">{{ riskCount }}</text>
          <text class="summary-label">风险提醒</text>
        </view>
        <view class="summary-item">
          <text class="summary-num">{{ sosCount }}</text>
          <text class="summary-label">求助次数</text>
        </view>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
void store.loadUserProfile()
store.setRole('elder')

const displayName = computed(() => store.elderName)
const topRisk = computed(() => store.latestHighRisk)
const hasHighRisk = computed(() => topRisk.value?.level === 'high')
const contactsCount = computed(() => store.contacts.length)
const riskCount = computed(() => store.riskRecords.length)
const sosCount = computed(() => store.sosCount)
const voiceSummary = computed(() => topRisk.value?.summary || '首页可以语音读出提醒内容，听不清时可以点播报。')

async function submitSos() {
  await store.submitSos()
  openPage('/pages/elder/sos-success')
}

function chatWithGuardian() {
  store.selectContact('guardian-li')
  openPage('/pages/elder/chat')
}

function callGuardian() {
  store.selectContact('guardian-li')
  store.startCall('guardian-li', 'elder', 'outgoing')
  openPage('/pages/elder/call')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  background:
    radial-gradient(circle at top right, rgba(255, 226, 181, 0.45), transparent 24%),
    linear-gradient(180deg, #fffaf0 0%, #f2efe6 100%);
}
.alert-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 12rpx 6rpx;
  border-radius: 24rpx;
}
.alert-banner.danger {
  padding: 22rpx;
  background: linear-gradient(135deg, #fff6ea 0%, #ffe7df 100%);
  border: 3rpx solid rgba(185, 28, 28, 0.2);
  box-shadow: var(--ss-shadow-strong);
}
.banner-main {
  flex: 1;
}
.banner-side {
  min-width: 160rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10rpx;
}
.banner-tag {
  display: inline-block;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: #fee2e2;
  color: var(--ss-color-danger);
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
.banner-title {
  display: block;
  margin-top: 14rpx;
  font-size: var(--ss-font-size-title);
  font-weight: 700;
}
.banner-desc {
  display: block;
  margin-top: 10rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.banner-action,
.banner-pulse {
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
.banner-action {
  color: var(--ss-color-primary);
}
.banner-pulse {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #b91c1c;
  color: #fff;
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
  margin-top: 20rpx;
}
.action-button {
  min-height: 144rpx;
  border: none;
  border-radius: 28rpx;
  background: #f3f6ef;
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  line-height: 1.35;
  padding: 12rpx 20rpx;
  box-shadow: 0 12rpx 26rpx rgba(22, 48, 43, 0.08);
}
.action-button.action-primary {
  background: linear-gradient(135deg, #d8fbf2 0%, #bdeee1 100%);
}
.action-button.action-soft {
  background: linear-gradient(135deg, #e6f7ff 0%, #d7ecfb 100%);
}
.action-button.action-warm {
  background: linear-gradient(135deg, #fff4dd 0%, #ffe8b8 100%);
}
.action-button.action-neutral {
  background: linear-gradient(135deg, #f4f4f5 0%, #e8eaee 100%);
}
.action-button.action-danger {
  background: linear-gradient(135deg, #ffe6e3 0%, #ffd5cf 100%);
  color: #991b1b;
}
.action-button.action-muted {
  background: linear-gradient(135deg, #f5f0e6 0%, #ece5d7 100%);
}
.summary-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  margin-top: 16rpx;
}
.summary-item {
  padding: 22rpx 10rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.78);
  text-align: center;
  box-shadow: 0 10rpx 22rpx rgba(22, 48, 43, 0.05);
}
.summary-num {
  display: block;
  font-size: var(--ss-font-size-title);
  font-weight: 700;
  color: var(--ss-color-primary);
}
.summary-label {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.5;
  color: var(--ss-color-subtext);
}
</style>
