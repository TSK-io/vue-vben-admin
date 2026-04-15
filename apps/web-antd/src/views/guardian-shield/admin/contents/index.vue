<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
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
  assetUrl: '',
  audience: 'elder',
  auditStatus: 'pending',
  category: 'fraud_case',
  channel: 'app',
  code: '',
  contentBody: '',
  contentType: 'education',
  status: 'draft',
  summary: '',
  title: '',
});

async function loadRows() {
  rows.value = await getAdminContentListApi();
}

function openCreate() {
  editingId.value = undefined;
  Object.assign(formState, {
    assetUrl: '',
    audience: 'elder',
    auditStatus: 'pending',
    category: 'fraud_case',
    channel: 'app',
    code: '',
    contentBody: '',
    contentType: 'education',
    status: 'draft',
    summary: '',
    title: '',
  });
  visible.value = true;
}

function openEdit(item: any) {
  editingId.value = item.id;
  Object.assign(formState, {
    assetUrl: item.assetUrl || '',
    audience: item.audience || 'elder',
    auditStatus: item.auditStatus || 'pending',
    category: item.category,
    channel: item.channel || 'app',
    code: item.code || '',
    contentBody: item.summary || '',
    contentType: item.contentType,
    status: item.status,
    summary: item.summary || '',
    title: item.title,
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
          已补齐诈骗案例库分类、审核状态和素材地址字段，可维护文章、模板与宣教素材。
        </p>
      </div>
      <Button type="primary" @click="openCreate">新增内容</Button>
    </section>

    <Card class="table-card" :bordered="false">
      <Table :data-source="rows" row-key="id">
        <Table.Column title="标题" data-index="title" key="title" />
        <Table.Column title="分类" data-index="category" key="category" />
        <Table.Column title="类型" data-index="contentType" key="contentType" />
        <Table.Column title="状态" key="status">
          <template #default="{ record }">
            <Space>
              <Tag>{{ record.status }}</Tag>
              <Tag color="blue">{{ record.auditStatus }}</Tag>
            </Space>
          </template>
        </Table.Column>
        <Table.Column title="素材" key="asset">
          <template #default="{ record }">
            {{ record.assetUrl ? '已配置' : '未配置' }}
          </template>
        </Table.Column>
        <Table.Column title="操作" key="actions">
          <template #default="{ record }">
            <Button type="link" size="small" @click="openEdit(record)">编辑</Button>
          </template>
        </Table.Column>
      </Table>
    </Card>

    <Modal v-model:open="visible" title="内容配置" width="720px" @ok="submitContent">
      <Form layout="vertical">
        <Form.Item label="内容类型">
          <Select
            v-model:value="formState.contentType"
            :options="[
              { label: '宣教/案例内容', value: 'education' },
              { label: '模板', value: 'template' },
            ]"
          />
        </Form.Item>
        <Form.Item label="标题"><Input v-model:value="formState.title" /></Form.Item>
        <Form.Item label="分类">
          <Select
            v-model:value="formState.category"
            :options="[
              { label: '诈骗案例库', value: 'fraud_case' },
              { label: '防骗文章', value: 'anti_fraud_article' },
              { label: '通知模板', value: 'notification_template' },
            ]"
          />
        </Form.Item>
        <Form.Item label="发布状态">
          <Select
            v-model:value="formState.status"
            :options="[
              { label: '草稿', value: 'draft' },
              { label: '已发布', value: 'published' },
              { label: '启用', value: 'enabled' },
            ]"
          />
        </Form.Item>
        <Form.Item label="审核状态">
          <Select
            v-model:value="formState.auditStatus"
            :options="[
              { label: '待审核', value: 'pending' },
              { label: '已通过', value: 'approved' },
              { label: '驳回', value: 'rejected' },
            ]"
          />
        </Form.Item>
        <Form.Item label="素材地址">
          <Input v-model:value="formState.assetUrl" placeholder="图片/音频文件地址" />
        </Form.Item>
        <Form.Item label="摘要">
          <Input.TextArea v-model:value="formState.summary" :rows="2" />
        </Form.Item>
        <Form.Item label="正文">
          <Input.TextArea v-model:value="formState.contentBody" :rows="5" />
        </Form.Item>
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
.table-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(14 165 233 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(14 116 144 / 8%);
}
.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 28px 30px;
}
.table-card {
  margin-top: 18px;
}
</style>
