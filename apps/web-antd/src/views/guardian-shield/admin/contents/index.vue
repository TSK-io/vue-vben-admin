<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Modal,
  Row,
  Select,
  Space,
  Tag,
  message,
} from 'ant-design-vue';

import {
  createAdminContentApi,
  getAdminContentListApi,
  updateAdminContentApi,
} from '#/api';

defineOptions({ name: 'AdminContents' });

const rows = ref<any[]>([]);
const visible = ref(false);
const editingId = ref<string>();
const formState = reactive({
  contentType: 'template',
  code: '',
  title: '',
  category: '',
  audience: 'elder',
  channel: 'app',
  status: 'draft',
  summary: '',
  contentBody: '',
  auditStatus: 'approved',
  assetUrl: '',
});

async function loadRows() {
  rows.value = await getAdminContentListApi();
}

function openCreate() {
  editingId.value = undefined;
  Object.assign(formState, {
    contentType: 'template',
    code: '',
    title: '',
    category: '',
    audience: 'elder',
    channel: 'app',
    status: 'draft',
    summary: '',
    contentBody: '',
    auditStatus: 'approved',
    assetUrl: '',
  });
  visible.value = true;
}

function openEdit(item: any) {
  editingId.value = item.id;
  Object.assign(formState, {
    contentType: item.contentType,
    code: item.code || '',
    title: item.title,
    category: item.category,
    audience: item.audience || 'elder',
    channel: item.channel || 'app',
    status: item.status,
    summary: item.summary || '',
    contentBody: item.summary || item.title,
    auditStatus: item.auditStatus || 'approved',
    assetUrl: item.assetUrl || '',
  });
  visible.value = true;
}

async function submitContent() {
  if (editingId.value) {
    await updateAdminContentApi(editingId.value, { ...formState });
    message.success('内容已更新');
  } else {
    await createAdminContentApi({ ...formState });
    message.success('内容已新增');
  }
  visible.value = false;
  await loadRows();
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="admin-contents-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 内容资产</p>
        <h1>内容管理</h1>
        <p class="description">
          内容管理已接真实后端，支持模板与宣教内容的新增、编辑和发布状态维护。
        </p>
      </div>
      <Button type="primary" @click="openCreate">新增内容</Button>
    </section>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="8" :span="24">
        <Card class="content-card" :bordered="false">
          <Space wrap>
            <Tag color="blue">{{ item.contentType }}</Tag>
            <Tag>{{ item.channel || item.audience }}</Tag>
            <Tag
              :color="
                item.status === 'published' || item.status === 'enabled'
                  ? 'success'
                  : 'warning'
              "
              >{{ item.status }}</Tag
            >
          </Space>
          <h3>{{ item.title }}</h3>
          <p>{{ item.category }} · {{ item.updatedAt }}</p>
          <Button size="small" @click="openEdit(item)">编辑</Button>
        </Card>
      </Col>
    </Row>

    <Modal
      v-model:open="visible"
      title="内容配置"
      ok-text="保存"
      cancel-text="关闭"
      @ok="submitContent"
    >
      <Form layout="vertical">
        <Form.Item label="内容类型"
          ><Select
            v-model:value="formState.contentType"
            :options="[
              { label: '模板', value: 'template' },
              { label: '宣教内容', value: 'education' },
            ]"
        /></Form.Item>
        <Form.Item label="标题"
          ><Input v-model:value="formState.title"
        /></Form.Item>
        <Form.Item label="分类"
          ><Input v-model:value="formState.category"
        /></Form.Item>
        <Form.Item label="状态"
          ><Select
            v-model:value="formState.status"
            :options="[
              { label: '草稿', value: 'draft' },
              { label: '已发布', value: 'published' },
              { label: '启用', value: 'enabled' },
            ]"
        /></Form.Item>
        <Form.Item label="内容"
          ><Input.TextArea v-model:value="formState.contentBody" :rows="4"
        /></Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.admin-contents-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #f7fcff 0%, #eef8ff 100%);
}

.hero-panel,
.content-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(14 165 233 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(14 116 144 / 8%);
}

.hero-panel {
  display: flex;
  gap: 16px;
  justify-content: space-between;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #0284c7;
  letter-spacing: 0.08em;
}

h1,
.content-card h3 {
  margin: 0;
  color: #0c4a6e;
}

h1 {
  font-size: 34px;
}

.description,
.content-card p {
  margin: 16px 0 0;
  line-height: 1.8;
  color: #475569;
}

.list-row {
  margin-top: 18px;
}

@media (max-width: 768px) {
  .admin-contents-page {
    padding: 16px;
  }

  .hero-panel {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
