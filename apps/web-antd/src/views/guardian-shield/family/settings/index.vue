<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { Button, Card, Col, Input, Row, Select, Space, message } from 'ant-design-vue';

import { getBindingListApi, sendFamilyReminderApi } from '#/api';

defineOptions({ name: 'FamilySettings' });

const templates = ref([
  '先别转账，我马上给你回电话。',
  '验证码不要告诉别人，等我核实后再处理。',
  '先挂电话，确认是官方号码再联系。',
]);
const selectedElderId = ref<string>();
const reminderText = ref('');
const sendChannel = ref<'app' | 'sms' | 'voice'>('app');
const sending = ref(false);
const bindings = ref<any[]>([]);

const elderOptions = computed(() =>
  bindings.value.map((item) => ({
    label: item.elderName,
    value: item.elderUserId,
  })),
);

async function loadBindings() {
  bindings.value = await getBindingListApi();
  selectedElderId.value = bindings.value[0]?.elderUserId;
}

function useTemplate(value: string) {
  reminderText.value = value;
}

async function submitReminder() {
  if (!selectedElderId.value || !reminderText.value.trim()) {
    message.warning('请选择老人并填写提醒内容');
    return;
  }
  const targetBinding = bindings.value.find((item) => item.elderUserId === selectedElderId.value);
  if (!targetBinding) return;
  sending.value = true;
  try {
    await sendFamilyReminderApi({
      channel: sendChannel.value,
      content: reminderText.value.trim(),
      elderUserId: targetBinding.elderUserId,
    });
    message.success('远程提醒已发送');
    reminderText.value = '';
  } finally {
    sending.value = false;
  }
}

onMounted(() => {
  void loadBindings();
});
</script>

<template>
  <div class="family-settings-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 监护设置</p>
        <h1>监护设置</h1>
        <p class="description">当前已接入真实提醒发送能力，可选老人、渠道和提醒文案后直接下发。</p>
      </div>
      <div class="hero-note">
        <strong>建议</strong>
        <span>看到高风险事件时，优先使用简短明确的提醒文案。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="10" :span="24">
        <Card class="setting-card" :bordered="false" title="发送远程提醒">
          <Space direction="vertical" style="width: 100%">
            <Select v-model:value="selectedElderId" :options="elderOptions" placeholder="选择老人" />
            <Select
              v-model:value="sendChannel"
              :options="[
                { label: '站内提醒', value: 'app' },
                { label: '短信提醒', value: 'sms' },
                { label: '语音提醒', value: 'voice' },
              ]"
            />
            <Input.TextArea v-model:value="reminderText" :rows="5" placeholder="请输入提醒内容" />
            <Button type="primary" :loading="sending" @click="submitReminder">发送提醒</Button>
          </Space>
        </Card>
      </Col>
      <Col :lg="14" :span="24">
        <Card class="template-card" :bordered="false" title="常用提醒文案">
          <Space direction="vertical" style="width: 100%">
            <div v-for="(item, index) in templates" :key="item" class="template-item">
              <div class="template-head">
                <span>模板 {{ index + 1 }}</span>
                <Button size="small" @click="useTemplate(item)">使用</Button>
              </div>
              <p>{{ item }}</p>
            </div>
          </Space>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.family-settings-page { min-height: 100%; padding: 24px; background: linear-gradient(180deg, #fff8fa 0%, #fff1f5 100%); }
.hero-panel,.setting-card,.template-card { border: 1px solid rgba(244,63,94,.14); border-radius: 24px; background: rgba(255,255,255,.96); box-shadow: 0 16px 36px rgba(136,19,55,.08); }
.hero-panel { display: flex; justify-content: space-between; gap: 20px; padding: 28px 30px; }
.eyebrow { margin: 0 0 12px; color: #e11d48; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
h1 { margin: 0; color: #881337; font-size: 34px; }
.description,.hero-note,.template-item p { color: #9f1239; line-height: 1.8; }
.hero-note { max-width: 280px; padding: 18px; border-radius: 20px; background: #fff1f2; }
.content-row { margin-top: 18px; }
.template-item { padding: 16px; border-radius: 18px; background: #fff7f9; }
.template-head { display: flex; justify-content: space-between; margin-bottom: 12px; color: #881337; }
@media (max-width: 768px) { .family-settings-page { padding: 16px; } .hero-panel,.template-head { flex-direction: column; } h1 { font-size: 28px; } }
</style>
