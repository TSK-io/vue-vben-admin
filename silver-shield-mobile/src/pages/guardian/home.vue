<template>
  <view class="ss-page ss-page--with-nav ss-page--with-tabbar">
    <ss-topbar title="我的" :subtitle="store.profile?.welcomeText || '账号信息、守护总览和常用操作放在这里。'" />

    <ss-card>
      <text class="card-title">当前登录信息</text>
      <text class="meta-item">姓名：{{ store.guardianName }}</text>
      <text class="meta-item">身份：子女 / 守护人</text>
      <text class="meta-item">手机号：{{ store.profile?.phone || '未加载' }}</text>
    </ss-card>

    <ss-card>
      <text class="card-title">今日重点</text>
      <view class="summary-grid">
        <view class="summary-item danger" @click="openPage('/pages/guardian/risk-list')">
          <text class="summary-num">{{ highRiskCount }}</text>
          <text class="summary-label">高风险待处理</text>
        </view>
        <view class="summary-item" @click="openPage('/pages/guardian/elders')">
          <text class="summary-num">{{ elderCount }}</text>
          <text class="summary-label">监护老人</text>
        </view>
        <view class="summary-item warm" @click="scrollToSos">
          <text class="summary-num">{{ pendingSosCount }}</text>
          <text class="summary-label">待回访求助</text>
        </view>
      </view>
    </ss-card>

    <ss-card>
      <ss-section-title title="风险趋势统计" subtitle="根据聊天、链接和通话复盘结果生成近几日走势。" />
      <view class="trend-list">
        <view v-for="point in riskTrendPoints" :key="point.label" class="trend-item">
          <text class="trend-label">{{ point.label }}</text>
          <text class="trend-meta">高 {{ point.high }} / 中 {{ point.medium }} / 低 {{ point.low }}</text>
        </view>
      </view>
    </ss-card>

    <ss-card>
      <ss-section-title title="常用操作" subtitle="从我的页进入通话记录、社区协同和远程提醒。" />
      <view class="action-grid">
        <button class="action-button" @click="openPage('/pages/guardian/elders')">老人列表</button>
        <button class="action-button" @click="openPage('/pages/guardian/risk-list')">风险通知</button>
        <button class="action-button accent" @click="openPage('/pages/guardian/conversations')">与老人聊天</button>
        <button class="action-button" @click="openCallRecords">通话记录</button>
        <button class="action-button soft" @click="sendQuickReminder">发送远程提醒</button>
        <button class="action-button warm" @click="openPage('/pages/guardian/community')">社区协同</button>
      </view>
    </ss-card>

    <ss-card v-if="topRisk">
      <ss-section-title title="最新风险" subtitle="优先联系老人，确认是否仍在与可疑对象接触。" />
      <view class="focus-block" @click="openRiskDetail(topRisk.id)">
        <text class="focus-tag">{{ topRisk.level.toUpperCase() }}</text>
        <text class="focus-title">{{ topRisk.title }}</text>
        <text class="focus-text">{{ topRisk.summary }}</text>
      </view>
    </ss-card>

    <ss-card v-if="latestSos" id="sos-card">
      <ss-section-title title="求助提醒" subtitle="收到求助后优先回访，再协调社区协助。" />
      <view class="focus-block warm-block">
        <text class="focus-title">{{ latestSos.elderName }} 发起了求助</text>
        <text class="focus-text">{{ latestSos.summary }}</text>
        <text class="focus-meta">{{ latestSos.time }} · 当前状态：{{ sosStatusText }}</text>
      </view>
      <view class="inline-actions">
        <button class="mini-btn" @click="openSosDetail">查看详情</button>
        <button class="mini-btn" @click="callLatestSosElder">立即通话</button>
        <button class="mini-btn secondary" @click="markSosHandled">标记处理中</button>
      </view>
    </ss-card>

    <button class="logout-button" @click="logout">退出登录</button>

    <app-tab-bar role="guardian" current="me" />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppTabBar from '@/components/app/AppTabBar.vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import { openPage, relaunchTo } from '@/utils/navigation'

const store = useAppStore()
void store.loadUserProfile()
store.setRole('guardian')

const topRisk = computed(() => store.latestHighRisk)
const highRiskCount = computed(() => store.pendingHighRiskCount)
const elderCount = computed(() => store.guardianElders.length)
const pendingSosCount = computed(() => store.activeSosAlerts.length)
const riskTrendPoints = computed(() => store.riskTrendPoints)
const latestSos = computed(() => store.activeSosAlerts[0])
const sosStatusText = computed(() => {
  if (!latestSos.value) {
    return '无'
  }

  return latestSos.value.status === 'pending' ? '待处理' : '处理中'
})

function logout() {
  store.logout()
  relaunchTo('/pages/auth/login')
}

function sendQuickReminder() {
  const elder = store.guardianElders[0]
  if (!elder) {
    return
  }

  store.selectElder(elder.id)
  store.sendRemoteReminder('看到陌生链接先别点，先发给我确认。')
  uni.showToast({
    title: '已发送远程提醒',
    icon: 'success',
  })
}

function openRiskDetail(riskId: string) {
  store.selectRisk(riskId)
  openPage('/pages/guardian/risk-detail')
}

function openSosChat() {
  if (!latestSos.value) {
    return
  }

  store.selectElder(latestSos.value.elderId)
  openPage('/pages/guardian/chat')
}

function openSosDetail() {
  if (!latestSos.value) {
    return
  }

  store.selectSosAlert(latestSos.value.id)
  openPage('/pages/guardian/sos-detail')
}

function callLatestSosElder() {
  if (!latestSos.value) {
    return
  }

  store.selectElder(latestSos.value.elderId)
  store.startCall(latestSos.value.elderId, 'guardian', 'outgoing')
  openPage('/pages/guardian/call')
}

function openCallRecords() {
  openPage('/pages/guardian/call-records')
}

function markSosHandled() {
  if (!latestSos.value) {
    return
  }

  store.markSosHandled(latestSos.value.id)
  uni.showToast({
    title: '已标记处理中',
    icon: 'success',
  })
}

function scrollToSos() {
  uni.pageScrollTo({
    selector: '#sos-card',
    duration: 200,
  })
}
</script>

<style scoped lang="scss">
.card-title {
  display: block;
  margin-bottom: 18rpx;
  font-size: 32rpx;
  font-weight: 700;
}
.meta-item {
  display: block;
  margin-top: 8rpx;
  font-size: 27rpx;
  color: var(--ss-color-subtext);
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}
.summary-item {
  padding: 20rpx 12rpx;
  border-radius: 22rpx;
  background: var(--ss-color-surface-soft);
  text-align: center;
}
.summary-item.danger {
  background: var(--ss-color-danger-bg);
}
.summary-item.warm {
  background: var(--ss-color-warning-bg);
}
.summary-num {
  display: block;
  font-size: 42rpx;
  font-weight: 700;
  color: var(--ss-color-primary);
}
.summary-label {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: var(--ss-color-subtext);
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  margin-top: 18rpx;
}
.action-button {
  border: none;
  border-radius: 22rpx;
  background: var(--ss-color-surface-soft);
  color: var(--ss-color-text);
  font-size: 28rpx;
  font-weight: 700;
}
.action-button.accent {
  background: rgba(236, 242, 250, 0.96);
}
.action-button.soft {
  background: rgba(245, 242, 235, 0.98);
}
.action-button.warm {
  background: var(--ss-color-warning-bg);
  color: var(--ss-color-warning-fg);
}
.trend-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-top: 16rpx;
}
.trend-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 18rpx 20rpx;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.9);
}
.trend-label {
  font-size: 26rpx;
  font-weight: 700;
}
.trend-meta {
  font-size: 24rpx;
  color: var(--ss-color-subtext);
}
.focus-block {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.warm-block {
  padding: 6rpx 0;
}
.focus-tag {
  width: fit-content;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  background: var(--ss-color-danger-bg);
  color: var(--ss-color-danger-fg);
  font-size: 22rpx;
}
.focus-title {
  font-size: 32rpx;
  font-weight: 700;
}
.focus-text,
.focus-meta {
  font-size: 26rpx;
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.inline-actions {
  display: flex;
  gap: 14rpx;
  margin-top: 18rpx;
}
.mini-btn {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: 26rpx;
}
.mini-btn.secondary {
  background: var(--ss-color-surface-muted);
  color: var(--ss-color-text);
}
.logout-button {
  border: none;
  border-radius: 20rpx;
  background: var(--ss-color-surface-muted);
  color: var(--ss-color-text);
  font-size: 30rpx;
}
</style>
