<template>
  <view class="page-shell">
    <view class="chat-header">
      <button class="back-button" @click="goBack">返回</button>
      <view class="header-main">
        <text class="header-name">{{ selectedContact?.name || '聊天' }}</text>
        <text class="header-meta">{{ selectedContact?.relation || '和熟悉的人慢慢聊' }}</text>
      </view>
      <button v-if="showBroadcast" class="voice-button" @click="announceChat">朗读</button>
    </view>

    <view v-if="topHint" class="chat-tip">
      <text class="chat-tip-text">{{ topHint }}</text>
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

    <view class="message-list">
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
          <view class="bubble">
            <template v-if="message.type === 'image'">
              <view class="media-card">
                <text class="media-tag">图片</text>
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
        </template>
      </view>
    </view>

    <view class="composer">
      <button class="tool-button" @click="sendImageSample">+</button>
      <input v-model="draft" class="composer-input" placeholder="发消息" />
      <button class="send-button" :class="{ disabled: !draft.trim() }" @click="submitMessage">发送</button>
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
const topHint = computed(() => {
  const latestSystem = [...messages.value].reverse().find((item) => item.sender === 'system')
  return latestSystem ? systemHint(latestSystem) : '遇到转账、验证码、陌生链接，先问家人。'
})

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
.page-shell {
  min-height: 100vh;
  width: 100%;
  max-width: 760px;
  margin: 0 auto;
  padding: 18rpx 18rpx 148rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  background: linear-gradient(180deg, #efece4 0%, #e8eee9 100%);
}
.chat-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 8rpx 4rpx 4rpx;
}
.back-button,
.voice-button {
  min-height: 72rpx;
  padding: 0 20rpx;
  border: none;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.7);
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-caption);
}
.header-main {
  flex: 1;
  min-width: 0;
  text-align: center;
}
.header-name {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: var(--ss-color-text);
}
.header-meta {
  display: block;
  margin-top: 4rpx;
  font-size: 22rpx;
  color: var(--ss-color-subtext);
}
.chat-tip {
  align-self: center;
  max-width: 92%;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 243, 205, 0.92);
}
.chat-tip-text {
  font-size: 22rpx;
  line-height: 1.5;
  color: #8a5a00;
}
.time-divider {
  display: flex;
  justify-content: center;
  margin: 8rpx 0 4rpx;
}
.time-divider-text {
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(112, 130, 124, 0.12);
  font-size: 22rpx;
  color: var(--ss-color-subtext);
}
.message-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.message-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}
.message-item.sender-self {
  align-items: flex-end;
}
.message-item.sender-other {
  align-items: flex-start;
}
.message-item.sender-system {
  align-items: center;
  margin: 6rpx 0;
}
.bubble {
  max-width: 76%;
  padding: 18rpx 20rpx;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 20rpx rgba(22, 48, 43, 0.05);
}
.sender-self .bubble {
  border-bottom-right-radius: 10rpx;
  background: #95ec69;
  box-shadow: none;
}
.sender-other .bubble {
  border-bottom-left-radius: 10rpx;
  background: rgba(255, 255, 255, 0.98);
}
.type-link .bubble {
  background: #ffffff;
}
.system-note {
  max-width: 88%;
  padding: 12rpx 18rpx;
  border-radius: 18rpx;
  background: rgba(255, 243, 221, 0.96);
  border: 1px solid rgba(255, 196, 93, 0.45);
}
.system-note-text {
  font-size: 24rpx;
  line-height: 1.5;
  color: #8a5a00;
  text-align: center;
}
.message-content,
.link-title,
.link-url {
  font-size: var(--ss-font-size-body);
  line-height: 1.55;
  color: #111827;
}
.link-title {
  font-weight: 700;
}
.link-url,
.message-meta,
.media-tag {
  font-size: 22rpx;
  color: var(--ss-color-subtext);
}
.media-card,
.link-card {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}
.message-meta {
  padding: 0 10rpx;
}
.composer {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 16rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  width: calc(100% - 32rpx);
  max-width: 728px;
  padding: 12rpx;
  border-radius: 24rpx;
  background: rgba(247, 247, 247, 0.98);
  box-shadow: 0 10rpx 24rpx rgba(22, 48, 43, 0.08);
}
.tool-button {
  width: 76rpx;
  min-width: 76rpx;
  min-height: 76rpx;
  border: none;
  border-radius: 50%;
  background: #ffffff;
  color: #6b7280;
  font-size: 40rpx;
  line-height: 1;
}
.composer-input {
  flex: 1;
  height: 76rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #ffffff;
  font-size: var(--ss-font-size-body);
}
.send-button {
  width: 128rpx;
  min-height: 76rpx;
  border: none;
  border-radius: 999rpx;
  background: #07c160;
  color: #fff;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}
.send-button.disabled {
  background: #9fd9b5;
}

@media (min-width: 768px) {
  .page-shell {
    min-height: 100vh;
    border-left: 1px solid rgba(22, 48, 43, 0.08);
    border-right: 1px solid rgba(22, 48, 43, 0.08);
    background: linear-gradient(180deg, #efece4 0%, #e7ede8 100%);
  }
}
</style>
