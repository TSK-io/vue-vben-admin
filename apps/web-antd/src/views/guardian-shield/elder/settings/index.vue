<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';

import { Button, Card, Form, Select, Switch, message } from 'ant-design-vue';

import {
  getAccessibilitySettingsApi,
  updateAccessibilitySettingsApi,
} from '#/api';

defineOptions({ name: 'ElderSettings' });

const loading = ref(false);
const saving = ref(false);
const formState = reactive({
  fontScale: 'large',
  highContrast: false,
  voiceAssistant: false,
  voiceSpeed: 'normal',
});

async function loadSettings() {
  loading.value = true;
  try {
    Object.assign(formState, await getAccessibilitySettingsApi());
  } finally {
    loading.value = false;
  }
}

async function saveSettings() {
  saving.value = true;
  try {
    await updateAccessibilitySettingsApi({ ...formState });
    message.success('适老设置已保存');
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  void loadSettings();
});
</script>

<template>
  <div class="elder-settings-page">
    <Card class="settings-card" :bordered="false" :loading="loading">
      <p class="eyebrow">老年端 / 适老设置</p>
      <h1>适老设置</h1>
      <p class="description">
        当前已接真实配置接口，可保存大字号、高对比度和语音辅助偏好。
      </p>
      <Form layout="vertical">
        <Form.Item label="字号">
          <Select
            v-model:value="formState.fontScale"
            :options="[
              { label: '标准', value: 'normal' },
              { label: '大字号', value: 'large' },
              { label: '超大字号', value: 'x-large' },
            ]"
          />
        </Form.Item>
        <Form.Item label="高对比度">
          <Switch v-model:checked="formState.highContrast" />
        </Form.Item>
        <Form.Item label="语音辅助">
          <Switch v-model:checked="formState.voiceAssistant" />
        </Form.Item>
        <Form.Item label="语速">
          <Select
            v-model:value="formState.voiceSpeed"
            :options="[
              { label: '慢速', value: 'slow' },
              { label: '正常', value: 'normal' },
              { label: '快速', value: 'fast' },
            ]"
          />
        </Form.Item>
        <Button type="primary" :loading="saving" @click="saveSettings"
          >保存设置</Button
        >
      </Form>
    </Card>
  </div>
</template>

<style scoped>
.elder-settings-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #faf7ff 0%, #f3edff 100%);
}

.settings-card {
  max-width: 760px;
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(124 58 237 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(91 33 182 / 8%);
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #7c3aed;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #5b21b6;
}

.description {
  margin: 16px 0 24px;
  line-height: 1.8;
  color: #6b21a8;
}

@media (max-width: 768px) {
  .elder-settings-page {
    padding: 16px;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
