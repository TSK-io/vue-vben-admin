<template>
  <view class="ss-page contacts-page">
    <ss-topbar title="联系人" subtitle="更像 iOS 通讯录，先看最常联系的人。" show-back />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="这里可以语音读出联系人姓名和关系，方便慢慢看。" />

    <ss-feedback-state
      v-if="!contacts.length"
      empty
      empty-title="联系人列表暂时为空"
      empty-description="稍后添加家人联系人后，就能从这里直接联系。"
    />

    <view v-else class="contact-section">
      <text class="section-label">优先联系</text>
      <view class="ss-list-group">
        <view v-for="contact in priorityContacts" :key="contact.id" class="ss-list-cell contact-cell" @click="chatWith(contact.id)">
          <view class="avatar">{{ contact.avatarText }}</view>
          <view class="contact-main">
            <view class="contact-top">
              <text class="name">{{ contact.name }}</text>
              <text v-if="contact.isBlacklisted" class="ss-chip ss-chip-danger">谨慎联系</text>
              <text v-else-if="contact.suspiciousLevel && contact.suspiciousLevel !== 'none'" class="ss-chip ss-chip-warn">先确认</text>
            </view>
            <text class="relation">{{ contact.relation }}</text>
            <text class="note">{{ contact.note }}</text>
          </view>
          <view class="contact-actions">
            <button class="action-chip" @click.stop="chatWith(contact.id)">消息</button>
            <button class="action-chip ghost" @click.stop="startCall(contact.id)">电话</button>
          </view>
        </view>
      </view>

      <text class="section-label secondary">其他联系人</text>
      <view class="ss-list-group">
        <view v-for="contact in otherContacts" :key="contact.id" class="ss-list-cell contact-cell compact" @click="chatWith(contact.id)">
          <view class="avatar">{{ contact.avatarText }}</view>
          <view class="contact-main">
            <text class="name">{{ contact.name }}</text>
            <text class="relation">{{ contact.relation }}</text>
          </view>
        </view>
      </view>
    </view>

    <button class="ss-secondary-button bottom-button" @click="openPage('/pages/elder/call-records')">最近通话</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const contacts = computed(() => store.contacts)
const priorityContacts = computed(() => contacts.value.filter((item) => item.isPriority))
const otherContacts = computed(() => contacts.value.filter((item) => !item.isPriority))

function chatWith(contactId: string) {
  store.selectContact(contactId)
  openPage('/pages/elder/chat')
}

function startCall(contactId: string) {
  store.selectContact(contactId)
  store.startCall(contactId, 'elder', 'outgoing')
  openPage('/pages/elder/call')
}
</script>

<style scoped lang="scss">
.contact-section {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.section-label {
  padding: 8rpx 8rpx 0;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
  color: var(--ss-color-primary);
}

.section-label.secondary {
  margin-top: 8rpx;
  color: var(--ss-color-subtext);
}

.contact-cell {
  align-items: flex-start;
}

.contact-cell.compact {
  align-items: center;
}

.avatar {
  width: 84rpx;
  height: 84rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
  color: var(--ss-color-primary);
  font-size: 30rpx;
  font-weight: 700;
}

.contact-main {
  flex: 1;
  min-width: 0;
}

.contact-top {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}

.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}

.relation,
.note {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.55;
  color: var(--ss-color-subtext);
}

.contact-actions {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.action-chip {
  min-width: 116rpx;
  min-height: 60rpx;
  padding: 0 16rpx;
  border: none;
  border-radius: var(--ss-pill-radius);
  background: linear-gradient(180deg, #3b82f6 0%, var(--ss-color-primary) 100%);
  color: #fff;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.action-chip.ghost {
  background: rgba(255, 255, 255, 0.9);
  color: var(--ss-color-text);
}

.bottom-button {
  margin-top: auto;
}
</style>
