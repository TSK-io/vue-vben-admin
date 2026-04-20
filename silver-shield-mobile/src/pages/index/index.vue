<template>
  <view class="page-shell">
    <view class="hero">
      <text class="eyebrow">Silver Shield Mobile</text>
      <text class="title">先登录，再按角色进入对应首页</text>
      <text class="subtitle">
        这一版已经把登录与角色分流、老年端首页、联系人、聊天、风险提醒、求助和适老化设置串起来了。
      </text>
    </view>

    <ss-card>
      <view class="section-head">
        <text class="section-title">当前状态</text>
        <text class="section-desc">{{ statusText }}</text>
      </view>
      <view class="action-list">
        <button class="primary-button" @click="goPrimaryAction">{{ primaryActionText }}</button>
        <button v-if="store.isLoggedIn" class="secondary-button" @click="logoutAndLoginAgain">退出并重新登录</button>
      </view>
    </ss-card>

    <ss-card>
      <view class="section-head">
        <text class="section-title">本轮已完成</text>
      </view>
      <view class="decision-list">
        <text class="decision-item">登录页：支持账号、密码、角色选择。</text>
        <text class="decision-item">角色分流：根据登录角色进入老人端或守护人端。</text>
        <text class="decision-item">登录态持久化：通过本地存储恢复角色与用户信息。</text>
        <text class="decision-item">老年端 MVP：首页、联系人、聊天、风险提醒、求助反馈、适老化设置。</text>
        <text class="decision-item">子女端 MVP：守护总览、老人列表、风险通知、风险详情、与老人聊天、求助提醒、远程提醒。</text>
        <text class="decision-item">聊天能力：双方会话列表、文本消息双向演示、时间与状态展示、图片/链接消息预留。</text>
        <text class="decision-item">AI 识别：文本、聊天记录、链接识别均已接入，支持风险高亮、原因、建议与失败兜底。</text>
        <text class="decision-item">求助联动：老人端求助会生成主业务系统工单，守护人可查看详情并回写处理状态。</text>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import { useAppStore } from '@/store/app'
import { navigateToRoleHome, relaunchTo } from '@/utils/navigation'

const store = useAppStore()

const statusText = computed(() => {
  if (!store.isLoggedIn) {
    return '当前未登录，请先进入登录页。'
  }

  return `已使用${store.currentRole === 'elder' ? '老年用户端' : '守护人端'}身份登录，用户：${store.profile?.name || '未加载'}`
})

const primaryActionText = computed(() => store.isLoggedIn ? '继续进入首页' : '进入登录页')

function goPrimaryAction() {
  if (store.isLoggedIn) {
    navigateToRoleHome(store.currentRole, true)
    return
  }

  relaunchTo('/pages/auth/login')
}

function logoutAndLoginAgain() {
  store.logout()
  relaunchTo('/pages/auth/login')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: calc(42rpx + var(--ss-safe-top)) 28rpx 48rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.hero {
  padding: 12rpx 8rpx 0;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}
.eyebrow {
  font-size: var(--ss-font-size-caption);
  letter-spacing: 4rpx;
  color: var(--ss-color-primary);
  font-weight: var(--ss-font-weight-semibold);
}
.title {
  font-size: var(--ss-font-size-hero);
  line-height: 1.2;
  font-weight: var(--ss-font-weight-bold);
  color: var(--ss-color-text-strong);
  letter-spacing: var(--ss-letter-spacing-tight);
}
.subtitle {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.section-head {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 20rpx;
}
.section-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: var(--ss-font-weight-semibold);
  color: var(--ss-color-text-strong);
}
.section-desc {
  font-size: var(--ss-font-size-body-sm);
  color: var(--ss-color-subtext);
}
.action-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.primary-button,
.secondary-button {
  width: 100%;
  font-size: var(--ss-font-size-body);
  font-weight: var(--ss-font-weight-semibold);
}
.primary-button {
  background: var(--ss-color-primary);
  color: #fff;
}
.secondary-button {
  background: rgba(255, 255, 255, 0.92);
  border: var(--ss-hairline);
  color: var(--ss-color-text);
}
.decision-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}
.decision-item {
  font-size: var(--ss-font-size-body-sm);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
</style>
