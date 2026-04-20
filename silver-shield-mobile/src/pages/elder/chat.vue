<template>
  <view class="chat-page">
    <view class="chat-shell">
      <view class="chat-header ss-glass-card ss-fade-up">
        <button class="circle-button ss-pressable" @click="goBack">‹</button>
        <view class="header-main">
          <text class="header-name">{{ selectedContact?.name || '聊天' }}</text>
          <text class="header-meta">{{ selectedContact?.relation || '和熟悉的人慢慢聊' }}</text>
        </view>
        <button v-if="showBroadcast" class="circle-button small ss-pressable" @click="announceChat">读</button>
      </view>

      <view v-if="topHint" class="risk-banner ss-fade-in" :class="{ danger: topHintLevel === 'high' }">
        <text class="risk-banner-text">{{ topHint }}</text>
      </view>

      <ss-feedback-state
        v-if="!selectedContact"
        empty
        empty-title="当前还没有选择联系人"
        empty-description="请先从联系人列表或会话列表进入聊天页。"
      />
      <ss-feedback-state
        v-else-if="!messages.length"
        empty
        empty-title="当前会话还没有消息"
        empty-description="可以先发一句“我先问下家里人”，后续这里会展示消息和风险提示。"
      />

      <view v-else class="message-list">
        <view class="time-divider">
          <text class="time-divider-text">今天</text>
        </view>
        <view
          v-for="message in messages"
          :key="message.id"
          class="message-item"
          :class="[`sender-${message.sender}`, `type-${message.type}`]"
        >
          <template v-if="message.sender === 'system'">
            <view class="system-note">
              <text class="system-note-text">{{ systemHint(message) }}</text>
            </view>
          </template>
          <template v-else>
            <view class="bubble-wrap ss-fade-up">
              <view class="bubble">
                <template v-if="message.type === 'image'">
                  <view class="media-card">
                    <text class="media-tag">图片内容</text>
                    <text class="message-content">{{ cleanImageText(message.content) }}</text>
                  </view>
                </template>
                <template v-else-if="message.type === 'link'">
                  <view class="link-card">
                    <text class="link-title">{{ message.linkTitle || '收到一个链接' }}</text>
                    <text class="link-url">{{ message.linkUrl }}</text>
                    <text class="message-content">{{ message.content }}</text>
                  </view>
                </template>
                <template v-else>
                  <text class="message-content">{{ message.content }}</text>
                </template>
              </view>
              <text class="message-meta">{{ message.time }}</text>
            </view>
          </template>
        </view>
      </view>
    </view>

    <view class="composer ss-glass-card ss-pop-in">
      <button class="circle-button composer-tool ss-pressable" @click="sendImageSample">+</button>
      <input v-model="draft" class="composer-input" placeholder="发消息前，先想一想是不是熟悉的人" />
      <button class="send-button ss-pressable" :class="{ disabled: !draft.trim() }" @click="submitMessage">发送</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import { useAppStore } from '@/store/app'
import { backPage } from '@/utils/navigation'
import type { ChatMessage } from '@/types/app'

const store = useAppStore()
const draft = ref('')

const selectedContact = computed(() => store.selectedContact)
const messages = computed(() => store.selectedMessages)
const showBroadcast = computed(() => store.elderSettings.voiceBroadcastReserved)
const latestSystem = computed(() => [...messages.value].reverse().find((item) => item.sender === 'system'))
const topHint = computed(() => latestSystem.value ? systemHint(latestSystem.value) : '遇到转账、验证码、陌生链接，先问家人。')
const topHintLevel = computed(() => latestSystem.value?.riskLevel || 'medium')

function submitMessage() {
  if (!draft.value.trim()) {
    return
  }
  store.sendMessage(draft.value)
  draft.value = ''
}

function sendImageSample() {
  void store.sendImageMessage({
    title: '陌生短信截图',
    ocrText: '系统通知您补缴养老金，请点击链接并输入验证码。',
  })
}

function announceChat() {
  uni.showToast({
    title: '已开始朗读聊天',
    icon: 'none',
  })
}

function goBack() {
  backPage()
}

function systemHint(message: ChatMessage) {
  if (message.riskLevel === 'high') {
    return '这条内容像诈骗，先别转账，先联系家人。'
  }

  return message.content.replace(/^[^：:]*[：:]/, '').trim() || '这条内容需要先确认。'
}

function cleanImageText(content: string) {
  return content.replace('图片消息预留：', '')
}
</script>

<style scoped lang="scss">
.chat-page {
  min-height: 100vh;
  padding: 20rpx 20rpx 164rpx;
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.85), transparent 26%),
    linear-gradient(180deg, #ffffff 0%, #f7f8fb 18%, #f2f4f8 100%);
}

.chat-shell {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 18rpx 20rpx;
  border-radius: 30rpx;
}

.circle-button {
  width: 74rpx;
  min-width: 74rpx;
  min-height: 74rpx;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  color: var(--ss-color-primary);
  font-size: 40rpx;
  line-height: 1;
}

.circle-button.small {
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}

.header-main {
  flex: 1;
  min-width: 0;
  text-align: center;
}

.header-name {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  letter-spacing: var(--ss-letter-spacing-tight);
}

.header-meta {
  display: block;
  margin-top: 6rpx;
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-subtext);
}

.risk-banner {
  padding: 16rpx 20rpx;
  border-radius: 999rpx;
  background: rgba(255, 243, 205, 0.96);
  align-self: center;
}

.risk-banner.danger {
  background: rgba(254, 226, 226, 0.94);
}

.risk-banner-text {
  font-size: var(--ss-font-size-caption);
  line-height: 1.5;
  color: #9a6700;
}

.risk-banner.danger .risk-banner-text {
  color: #b91c1c;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding-bottom: 12rpx;
}

.time-divider {
  display: flex;
  justify-content: center;
  margin: 6rpx 0;
}

.time-divider-text {
  padding: 8rpx 18rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(148, 163, 184, 0.14);
  color: var(--ss-color-subtext);
  font-size: var(--ss-font-size-caption);
}

.message-item {
  display: flex;
}

.message-item.sender-self {
  justify-content: flex-end;
}

.message-item.sender-other {
  justify-content: flex-start;
}

.message-item.sender-system {
  justify-content: center;
}

.bubble-wrap {
  max-width: 78%;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.bubble {
  padding: 20rpx 22rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 14rpx 30rpx rgba(15, 23, 42, 0.08);
}

.sender-self .bubble {
  border-bottom-right-radius: 12rpx;
  background: linear-gradient(180deg, #3f9bff 0%, var(--ss-color-primary) 100%);
}

.sender-self .message-content,
.sender-self .link-title,
.sender-self .link-url {
  color: #fff;
}

.sender-other .bubble {
  border-bottom-left-radius: 12rpx;
}

.system-note {
  max-width: 88%;
  padding: 14rpx 18rpx;
  border-radius: 22rpx;
  background: rgba(255, 247, 224, 0.98);
}

.system-note-text {
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: #9a6700;
  text-align: center;
}

.message-content,
.link-title,
.link-url {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-text);
}

.link-title {
  font-weight: 700;
}

.link-url,
.media-tag,
.message-meta {
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-subtext);
}

.media-card,
.link-card {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.message-meta {
  padding: 0 12rpx;
}

.composer {
  position: fixed;
  left: 20rpx;
  right: 20rpx;
  bottom: 18rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 12rpx;
  border-radius: 30rpx;
}

.composer-tool {
  background: rgba(255, 255, 255, 0.94);
  color: var(--ss-color-subtext);
}

.composer-input {
  flex: 1;
  height: 76rpx;
  padding: 0 22rpx;
  border-radius: var(--ss-pill-radius);
  background: rgba(255, 255, 255, 0.96);
  font-size: var(--ss-font-size-body);
}

.send-button {
  min-width: 136rpx;
  min-height: 76rpx;
  border: none;
  border-radius: var(--ss-pill-radius);
  background: linear-gradient(180deg, #3b82f6 0%, var(--ss-color-primary) 100%);
  color: #fff;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}

.send-button.disabled {
  background: #bfdbfe;
}
</style>
