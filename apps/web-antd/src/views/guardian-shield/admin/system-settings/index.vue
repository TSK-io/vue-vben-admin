<script lang="ts" setup>
import { onMounted, ref } from 'vue';

import { Button, Card, Col, Input, Row, Space, Tag, message } from 'ant-design-vue';

import { getAdminSystemConfigListApi, updateAdminSystemConfigApi } from '#/api';

defineOptions({ name: 'AdminSystemSettings' });

const rows = ref<any[]>([]);
const savingKey = ref('');

async function loadRows() {
  rows.value = await getAdminSystemConfigListApi();
}

async function saveRow(item: any) {
  savingKey.value = item.key;
  try {
    await updateAdminSystemConfigApi(item.key, item.value);
    message.success('配置已保存');
  } finally {
    savingKey.value = '';
  }
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="admin-system-settings-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 参数管理</p>
        <h1>系统配置</h1>
        <p class="description">系统配置已切到真实后端，可直接修改参数值并保存。</p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.key" :lg="8" :span="24">
        <Card class="setting-card" :bordered="false">
          <Space wrap>
            <Tag color="blue">{{ item.group }}</Tag>
            <Tag color="success">可编辑</Tag>
          </Space>
          <h3>{{ item.name }}</h3>
          <p class="key">{{ item.key }}</p>
          <Input v-model:value="item.value" />
          <p class="desc">{{ item.description }}</p>
          <Button type="primary" size="small" :loading="savingKey === item.key" @click="saveRow(item)">保存</Button>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.admin-system-settings-page { min-height: 100%; padding: 24px; background: linear-gradient(180deg, #f8f9ff 0%, #eef0ff 100%); }
.hero-panel,.setting-card { border: 1px solid rgba(99,102,241,.14); border-radius: 24px; background: rgba(255,255,255,.96); box-shadow: 0 16px 36px rgba(67,56,202,.08); }
.hero-panel { padding: 28px 30px; }
.eyebrow { margin: 0 0 12px; color: #4f46e5; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
h1,.setting-card h3 { margin: 0; color: #312e81; }
h1 { font-size: 34px; }
.description,.key,.desc { margin: 16px 0 0; color: #475569; line-height: 1.8; }
.list-row { margin-top: 18px; }
@media (max-width: 768px) { .admin-system-settings-page { padding: 16px; } h1 { font-size: 28px; } }
</style>
