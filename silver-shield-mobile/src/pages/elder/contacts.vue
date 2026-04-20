<template>
  <view class="ss-page ss-page--with-nav ss-page--with-tabbar contacts-page">
    <app-nav-bar title="联系人" subtitle="优先联系人和其他联系人分开展示，更容易找。" />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="这里可以语音读出联系人姓名和关系，方便慢慢看。" />

    <ss-feedback-state
      v-if="!contacts.length"
      empty
      empty-title="联系人列表暂时为空"
      empty-description="稍后添加家人联系人后，就能从这里直接联系。"
    />

    <view v-else class="contact-section">
      <text class="section-label ss-page-caption">优先联系</text>
      <view class="ss-list-group ss-fade-up ss-stagger-1">
        <app-list-cell
          v-for="contact in priorityContacts"
          :key="contact.id"
          class="contact-cell"
          :title="contact.name"
          :description="contact.relation"
          :secondary="contact.note"
          :avatar-text="contact.avatarText"
          align="start"
          @click="chatWith(contact.id)"
        >
          <template #titleSuffix>
            <text v-if="contact.isBlacklisted" class="ss-chip ss-chip-danger">谨慎联系</text>
            <text v-else-if="contact.suspiciousLevel && contact.suspiciousLevel !== 'none'" class="ss-chip ss-chip-warn">先确认</text>
          </template>
          <template #trailing>
            <view class="contact-actions">
              <button class="action-chip ss-pressable" @click.stop="chatWith(contact.id)">消息</button>
              <button class="action-chip ghost ss-pressable" @click.stop="startCall(contact.id)">电话</button>
            </view>
          </template>
        </app-list-cell>
      </view>

      <text class="section-label secondary ss-page-caption">其他联系人</text>
      <view class="ss-list-group ss-fade-up ss-stagger-2">
        <app-list-cell
          v-for="contact in otherContacts"
          :key="contact.id"
          class="contact-cell compact"
          :title="contact.name"
          :description="contact.relation"
          :avatar-text="contact.avatarText"
          compact
          @click="chatWith(contact.id)"
        />
      </view>
    </view>

    <app-tab-bar role="elder" current="contacts" />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppListCell from '@/components/app/AppListCell.vue'
import AppNavBar from '@/components/app/AppNavBar.vue'
import AppTabBar from '@/components/app/AppTabBar.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
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
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}

.action-chip.ghost {
  background: var(--ss-color-surface-muted);
  color: var(--ss-color-text);
}

</style>
