<template>
  <view class="page-shell">
    <view class="orb orb--left" />
    <view class="orb orb--right" />

    <view class="hero">
      <text class="eyebrow">SILVER SHIELD</text>
      <text class="title">更安静、更可信的沟通入口</text>
      <text class="subtitle">登录后进入熟悉的联系人与会话，不让风险提醒抢走聊天本身的主角位置。</text>
    </view>

    <ss-card class="login-card">
      <view class="login-card__head">
        <text class="login-card__title">登录账号</text>
        <text class="login-card__desc">演示阶段先使用本地账号，后续再替换成真实登录接口。</text>
      </view>

      <ss-section-title title="选择身份" subtitle="不同身份会进入不同的消息与守护视图。" />
      <view class="role-switch">
        <button
          v-for="role in roles"
          :key="role.value"
          class="role-chip"
          :class="{ active: form.role === role.value }"
          @click="form.role = role.value"
        >
          <text class="role-chip__label">{{ role.label }}</text>
          <text class="role-chip__meta">{{ role.value === 'elder' ? '会话与求助' : '守护与提醒' }}</text>
        </button>
      </view>

      <view class="form-list">
        <view class="form-item">
          <text class="label">账号</text>
          <input v-model="form.account" class="input" placeholder="输入账号，例如 elder_demo" />
        </view>
        <view class="form-item">
          <text class="label">密码</text>
          <input v-model="form.password" class="input" password placeholder="输入密码，演示环境默认 111" />
        </view>
      </view>

      <text v-if="store.loginError" class="error-text">{{ store.loginError }}</text>

      <button class="ss-primary-button submit-button" @click="submitLogin">登录并进入首页</button>
      <text class="hint-text">老人端可用 `elder_demo`，守护人端可用 `family_demo`。</text>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import { useAppStore } from '@/store/app'
import { navigateToRoleHome } from '@/utils/navigation'
import type { LoginForm, UserRole } from '@/types/app'

const store = useAppStore()

const roles: Array<{ label: string; value: UserRole }> = [
  { label: '老年用户端', value: 'elder' },
  { label: '子女 / 守护人端', value: 'guardian' },
]

const form = reactive<LoginForm>({
  account: 'elder_demo',
  password: '111',
  role: 'elder',
})

async function submitLogin() {
  const success = await store.login(form)
  if (!success) {
    return
  }

  navigateToRoleHome(form.role, true)
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: calc(48rpx + var(--ss-safe-top)) 28rpx 48rpx;
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.orb {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(12rpx);
  opacity: 0.8;
}

.orb--left {
  top: 36rpx;
  left: -84rpx;
  width: 240rpx;
  height: 240rpx;
  background: radial-gradient(circle, rgba(23, 104, 229, 0.12), rgba(23, 104, 229, 0));
}

.orb--right {
  top: 180rpx;
  right: -78rpx;
  width: 220rpx;
  height: 220rpx;
  background: radial-gradient(circle, rgba(183, 121, 31, 0.08), rgba(183, 121, 31, 0));
}

.hero {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 12rpx 6rpx 0;
}

.eyebrow {
  font-size: var(--ss-font-size-caption);
  letter-spacing: 5rpx;
  color: var(--ss-color-primary);
  font-weight: var(--ss-font-weight-semibold);
}

.title {
  max-width: 11em;
  font-size: var(--ss-font-size-hero);
  font-weight: var(--ss-font-weight-bold);
  line-height: 1.2;
  letter-spacing: var(--ss-letter-spacing-tight);
  color: var(--ss-color-text-strong);
}

.subtitle {
  max-width: 20em;
  font-size: var(--ss-font-size-body);
  line-height: 1.75;
  color: var(--ss-color-subtext);
}

.login-card {
  position: relative;
  z-index: 1;
}

.login-card__head {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-bottom: 28rpx;
}

.login-card__title {
  font-size: var(--ss-font-size-title);
  font-weight: var(--ss-font-weight-bold);
  letter-spacing: var(--ss-letter-spacing-tight);
  color: var(--ss-color-text-strong);
}

.login-card__desc {
  font-size: var(--ss-font-size-body-sm);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}

.role-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-top: 20rpx;
}

.role-chip {
  min-height: 144rpx;
  padding: 22rpx;
  border-radius: 24rpx;
  background: rgba(245, 247, 250, 0.96);
  border: var(--ss-hairline);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 8rpx;
  color: var(--ss-color-text);
  box-shadow: none;
}

.role-chip__label {
  font-size: var(--ss-font-size-body);
  font-weight: var(--ss-font-weight-semibold);
}

.role-chip__meta {
  font-size: var(--ss-font-size-body-sm);
  line-height: 1.5;
  color: var(--ss-color-subtext);
}

.role-chip.active {
  background: rgba(236, 242, 250, 0.98);
  border-color: rgba(23, 104, 229, 0.18);
  color: var(--ss-color-primary-strong);
  box-shadow: var(--ss-shadow-soft);
}

.role-chip.active .role-chip__meta {
  color: var(--ss-color-primary);
}

.form-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-top: 28rpx;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.label {
  font-size: var(--ss-font-size-body-sm);
  font-weight: var(--ss-font-weight-semibold);
  color: var(--ss-color-text-strong);
}

.input {
  height: var(--ss-input-height);
  border-radius: 22rpx;
  background: var(--ss-color-surface-muted);
  border: var(--ss-hairline);
  padding: 0 24rpx;
  font-size: var(--ss-font-size-body);
  color: var(--ss-color-text);
}

.error-text {
  display: block;
  margin-top: 18rpx;
  color: var(--ss-color-danger);
  font-size: var(--ss-font-size-body-sm);
  font-weight: var(--ss-font-weight-medium);
}

.submit-button {
  margin-top: 24rpx;
  width: 100%;
}

.hint-text {
  display: block;
  margin-top: 18rpx;
  font-size: var(--ss-font-size-body-sm);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
</style>
