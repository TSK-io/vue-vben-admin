<script lang="ts" setup>
import type { TableColumnsType } from 'ant-design-vue';

import type { AdminUserListItem } from '#/api';

import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Descriptions,
  Drawer,
  Form,
  Input,
  Modal,
  Row,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'ant-design-vue';

import {
  createAdminUserApi,
  getAdminUserDetailApi,
  getAdminUserListApi,
  resetAdminUserPasswordApi,
  updateAdminUserApi,
  updateAdminUserPhoneApi,
} from '#/api';

defineOptions({ name: 'AdminUsers' });

const loading = ref(false);
const rows = ref<AdminUserListItem[]>([]);
const total = ref(0);
const drawerVisible = ref(false);
const editorVisible = ref(false);
const resetVisible = ref(false);
const currentUser = ref<AdminUserListItem | null>(null);
const editingId = ref<string>();

const filters = reactive({
  keyword: '',
  page: 1,
  pageSize: 5,
  role: undefined as string | undefined,
  status: undefined as string | undefined,
});

const formState = reactive({
  username: '',
  displayName: '',
  phone: '',
  roles: ['elder'] as string[],
  status: 'enabled',
  password: '',
  notesText: '',
});

const resetPassword = ref('');

const roleTextMap: Record<AdminUserListItem['role'], string> = {
  admin: '管理员',
  community: '社区工作人员',
  elder: '老年用户',
  family: '子女用户',
};

const riskColorMap: Record<AdminUserListItem['riskLevel'], string> = {
  high: 'red',
  low: 'green',
  medium: 'orange',
};

const statusColorMap: Record<AdminUserListItem['status'], string> = {
  disabled: 'default',
  enabled: 'success',
};

const summaryCards = computed(() => [
  { title: '当前列表人数', value: `${total.value}`, description: '结合筛选条件统计当前可见用户总数。' },
  { title: '老年用户', value: `${rows.value.filter((item) => item.role === 'elder').length}`, description: '用于跟进风险提醒与家属绑定。' },
  { title: '高风险对象', value: `${rows.value.filter((item) => item.riskLevel === 'high').length}`, description: '便于联动告警与工单。' },
  { title: '启用账号', value: `${rows.value.filter((item) => item.status === 'enabled').length}`, description: '支持继续停用、重置密码与换绑手机号。' },
]);

const columns: TableColumnsType<AdminUserListItem> = [
  { dataIndex: 'name', key: 'name', title: '用户信息' },
  { dataIndex: 'role', key: 'role', title: '角色' },
  { dataIndex: 'communityName', key: 'communityName', title: '所属社区' },
  { dataIndex: 'riskLevel', key: 'riskLevel', title: '风险状态' },
  { dataIndex: 'bindCount', key: 'bindCount', title: '绑定关系' },
  { dataIndex: 'lastAlertAt', key: 'lastAlertAt', title: '最近告警' },
  { dataIndex: 'status', key: 'status', title: '账号状态' },
  { key: 'actions', title: '操作' },
];

function parseNotes(text: string) {
  return Object.fromEntries(
    text
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [key, ...rest] = line.split('=');
        return [key.trim(), rest.join('=').trim()];
      }),
  );
}

async function loadUsers() {
  loading.value = true;
  try {
    const data = await getAdminUserListApi(filters);
    rows.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

async function openDetail(item: AdminUserListItem) {
  currentUser.value = await getAdminUserDetailApi(item.id);
  drawerVisible.value = true;
}

function openCreate() {
  editingId.value = undefined;
  Object.assign(formState, {
    username: '',
    displayName: '',
    phone: '',
    roles: ['elder'],
    status: 'enabled',
    password: '111',
    notesText: '',
  });
  editorVisible.value = true;
}

function openEdit(item: AdminUserListItem) {
  editingId.value = item.id;
  Object.assign(formState, {
    username: item.username,
    displayName: item.name,
    phone: item.phone,
    roles: item.roles || [item.role],
    status: item.status,
    password: '',
    notesText: Object.entries(item.notes || {})
      .map(([key, value]) => `${key}=${value}`)
      .join('\n'),
  });
  editorVisible.value = true;
}

function openReset(item: AdminUserListItem) {
  editingId.value = item.id;
  resetPassword.value = '111';
  resetVisible.value = true;
}

async function submitEditor() {
  const payload = {
    displayName: formState.displayName,
    notes: parseNotes(formState.notesText),
    password: formState.password || undefined,
    phone: formState.phone,
    roles: formState.roles,
    status: formState.status,
    username: formState.username,
  };
  if (editingId.value) {
    await updateAdminUserApi(editingId.value, payload);
    await updateAdminUserPhoneApi(editingId.value, formState.phone);
    message.success('用户已更新');
  } else {
    await createAdminUserApi(payload);
    message.success('用户已新增');
  }
  editorVisible.value = false;
  await loadUsers();
}

async function submitResetPassword() {
  if (!editingId.value) return;
  await resetAdminUserPasswordApi(editingId.value, resetPassword.value);
  resetVisible.value = false;
  message.success('密码已重置');
}

onMounted(() => {
  void loadUsers();
});
</script>

<template>
  <div class="admin-users-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 第一阶段</p>
        <h1>用户管理</h1>
        <p class="description">
          当前页已补齐新增、编辑、详情、重置密码和换绑手机号，账号运维链路可以直接联调。
        </p>
      </div>
      <Button type="primary" @click="openCreate">新增用户</Button>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="6" :md="12" :span="24">
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Card class="filter-card" :bordered="false">
      <Space :size="12" wrap>
        <Input v-model:value="filters.keyword" allow-clear placeholder="搜索姓名、手机号或账号" style="width: 260px" />
        <Select v-model:value="filters.role" allow-clear placeholder="角色" style="width: 180px" :options="[
          { label: '老年用户', value: 'elder' },
          { label: '子女用户', value: 'family' },
          { label: '社区工作人员', value: 'community' },
          { label: '管理员', value: 'admin' },
        ]" />
        <Select v-model:value="filters.status" allow-clear placeholder="状态" style="width: 140px" :options="[
          { label: '启用', value: 'enabled' },
          { label: '停用', value: 'disabled' },
        ]" />
        <Button type="primary" @click="loadUsers">查询</Button>
      </Space>
    </Card>

    <Card class="table-card" :bordered="false">
      <Table
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        :pagination="{ current: filters.page, pageSize: filters.pageSize, total }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <strong>{{ record.name }}</strong>
            <div>{{ record.username }} · {{ record.phone }}</div>
          </template>
          <template v-else-if="column.key === 'role'">
            {{ roleTextMap[record.role] }}
          </template>
          <template v-else-if="column.key === 'riskLevel'">
            <Tag :color="riskColorMap[record.riskLevel]">{{ record.riskLevel }}</Tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <Tag :color="statusColorMap[record.status]">{{ record.status }}</Tag>
          </template>
          <template v-else-if="column.key === 'actions'">
            <Space>
              <Button size="small" @click="openDetail(record)">详情</Button>
              <Button size="small" @click="openEdit(record)">编辑</Button>
              <Button size="small" @click="openReset(record)">重置密码</Button>
            </Space>
          </template>
        </template>
      </Table>
    </Card>

    <Drawer v-model:open="drawerVisible" title="用户详情" width="560">
      <Descriptions v-if="currentUser" bordered :column="1">
        <Descriptions.Item label="姓名">{{ currentUser.name }}</Descriptions.Item>
        <Descriptions.Item label="账号">{{ currentUser.username }}</Descriptions.Item>
        <Descriptions.Item label="手机号">{{ currentUser.phone }}</Descriptions.Item>
        <Descriptions.Item label="角色">{{ (currentUser.roles || []).join(', ') }}</Descriptions.Item>
        <Descriptions.Item label="最近告警">{{ currentUser.latestAlertTitle || '-' }}</Descriptions.Item>
        <Descriptions.Item label="绑定关系">{{ currentUser.bindingIds?.join(', ') || '-' }}</Descriptions.Item>
      </Descriptions>
    </Drawer>

    <Modal v-model:open="editorVisible" title="用户配置" ok-text="保存" cancel-text="关闭" @ok="submitEditor">
      <Form layout="vertical">
        <Form.Item label="账号"><Input v-model:value="formState.username" /></Form.Item>
        <Form.Item label="姓名"><Input v-model:value="formState.displayName" /></Form.Item>
        <Form.Item label="手机号"><Input v-model:value="formState.phone" /></Form.Item>
        <Form.Item label="角色">
          <Select
            v-model:value="formState.roles"
            mode="multiple"
            :options="[
              { label: '老年用户', value: 'elder' },
              { label: '子女用户', value: 'family' },
              { label: '社区工作人员', value: 'community' },
              { label: '管理员', value: 'admin' },
            ]"
          />
        </Form.Item>
        <Form.Item label="状态">
          <Select v-model:value="formState.status" :options="[
            { label: '启用', value: 'enabled' },
            { label: '停用', value: 'disabled' },
          ]" />
        </Form.Item>
        <Form.Item label="密码"><Input v-model:value="formState.password" /></Form.Item>
        <Form.Item label="画像备注">
          <Input.TextArea v-model:value="formState.notesText" :rows="4" placeholder="每行一个 key=value" />
        </Form.Item>
      </Form>
    </Modal>

    <Modal v-model:open="resetVisible" title="重置密码" ok-text="确认" cancel-text="关闭" @ok="submitResetPassword">
      <Input v-model:value="resetPassword" />
    </Modal>
  </div>
</template>

<style scoped>
.admin-users-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.hero-panel,
.summary-card,
.filter-card,
.table-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(59 130 246 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(30 64 175 / 8%);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  padding: 28px 30px;
}

.summary-row,
.filter-card,
.table-card {
  margin-top: 18px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #1d4ed8;
}

.description,
.summary-desc {
  line-height: 1.8;
  color: #475569;
}

.summary-title {
  color: #1d4ed8;
}

.summary-value {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  color: #172554;
}
</style>
