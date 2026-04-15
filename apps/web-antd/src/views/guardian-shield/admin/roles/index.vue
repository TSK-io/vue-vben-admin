<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

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
  createAdminRoleApi,
  getRolePermissionOverviewApi,
  updateAdminRoleApi,
} from '#/api';
import type { RolePermissionOverviewItem } from '#/api';

defineOptions({ name: 'AdminRoles' });

const loading = ref(false);
const visible = ref(false);
const editingCode = ref<string>();
const rows = ref<RolePermissionOverviewItem[]>([]);

const menuOptions = [
  '用户管理',
  '角色权限',
  '风险规则',
  '内容管理',
  '系统配置',
  '告警记录',
  '辖区总览',
  '重点老人',
  '风险工单',
  '宣教管理',
  '统计报表',
  '首页',
  '风险提醒',
  '一键求助',
  '亲属绑定',
  '防骗知识',
  '适老设置',
  '监护总览',
  '老人列表',
  '风险详情',
  '通知记录',
  '监护设置',
].map((item) => ({ label: item, value: item }));

const permissionOptions = [
  'alerts:read',
  'alerts:export',
  'bindings:read',
  'binding:manage',
  'community:read',
  'content:review',
  'content:write',
  'elder:read',
  'elder-focus:read',
  'family:read',
  'notifications:read',
  'notifications:update',
  'risk:lexicon:write',
  'risk:rule:write',
  'sos:create',
  'users:write',
  'workorder:read',
  'workorder:update',
].map((item) => ({ label: item, value: item }));

const dataScopeOptions = [
  { label: '仅本人', value: 'self' },
  { label: '所属对象', value: 'assigned' },
  { label: '全社区', value: 'community' },
  { label: '全量', value: 'all' },
];

const formState = reactive({
  apiPermissions: [] as string[],
  buttonPermissions: [] as string[],
  code: 'admin' as RolePermissionOverviewItem['role'],
  dataScope: 'all',
  description: '',
  menus: [] as string[],
  name: '',
  permissions: [] as string[],
});

const summaryCards = computed(() => [
  {
    title: '角色数量',
    value: `${rows.value.length}`,
  },
  {
    title: '按钮权限',
    value: `${rows.value.reduce((sum, item) => sum + item.buttonPermissions.length, 0)}`,
  },
  {
    title: '接口权限',
    value: `${rows.value.reduce((sum, item) => sum + item.apiPermissions.length, 0)}`,
  },
  {
    title: '菜单总数',
    value: `${rows.value.reduce((sum, item) => sum + item.menuCount, 0)}`,
  },
]);

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await getRolePermissionOverviewApi();
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingCode.value = undefined;
  Object.assign(formState, {
    apiPermissions: [],
    buttonPermissions: [],
    code: 'admin',
    dataScope: 'all',
    description: '',
    menus: [],
    name: '',
    permissions: [],
  });
  visible.value = true;
}

function openEdit(item: RolePermissionOverviewItem) {
  editingCode.value = item.role;
  Object.assign(formState, {
    apiPermissions: [...item.apiPermissions],
    buttonPermissions: [...item.buttonPermissions],
    code: item.role,
    dataScope: item.dataScope,
    description: item.description,
    menus: [...item.menus],
    name: item.name,
    permissions: [...item.resources],
  });
  visible.value = true;
}

async function submitRole() {
  const payload = { ...formState };
  if (editingCode.value) {
    await updateAdminRoleApi(editingCode.value, payload);
    message.success('角色权限已更新');
  } else {
    await createAdminRoleApi(payload);
    message.success('角色权限已创建');
  }
  visible.value = false;
  await loadRows();
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="admin-roles-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 权限总览</p>
        <h1>角色权限</h1>
        <p class="description">
          已补齐角色菜单、按钮权限、接口权限和数据范围配置，可直接维护精细化权限。
        </p>
      </div>
      <Button type="primary" @click="openCreate">新增角色配置</Button>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="6" :span="24">
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.role" :lg="12" :span="24">
        <Card class="role-card" :bordered="false" :loading="loading">
          <div class="role-head">
            <div>
              <h3>{{ item.name }}</h3>
              <p>{{ item.description }}</p>
            </div>
            <Space>
              <Tag color="blue">{{ item.menuCount }} 个菜单</Tag>
              <Tag color="gold">{{ item.codeCount }} 个资源</Tag>
              <Tag color="green">{{ item.dataScope }}</Tag>
              <Button size="small" @click="openEdit(item)">编辑</Button>
            </Space>
          </div>
          <div class="block">
            <p class="label">菜单</p>
            <Space wrap>
              <Tag v-for="menu in item.menus" :key="menu">{{ menu }}</Tag>
            </Space>
          </div>
          <div class="block">
            <p class="label">按钮权限</p>
            <Space wrap>
              <Tag
                v-for="button in item.buttonPermissions"
                :key="button"
                color="processing"
              >
                {{ button }}
              </Tag>
            </Space>
          </div>
          <div class="block">
            <p class="label">接口权限</p>
            <Space wrap>
              <Tag
                v-for="resource in item.apiPermissions"
                :key="resource"
                color="purple"
              >
                {{ resource }}
              </Tag>
            </Space>
          </div>
        </Card>
      </Col>
    </Row>

    <Modal
      v-model:open="visible"
      title="角色权限配置"
      ok-text="保存"
      cancel-text="关闭"
      @ok="submitRole"
    >
      <Form layout="vertical">
        <Form.Item label="角色编码">
          <Select
            v-model:value="formState.code"
            :disabled="!!editingCode"
            :options="[
              { label: '管理员', value: 'admin' },
              { label: '社区', value: 'community' },
              { label: '老年端', value: 'elder' },
              { label: '子女端', value: 'family' },
            ]"
          />
        </Form.Item>
        <Form.Item label="角色名称">
          <Input v-model:value="formState.name" />
        </Form.Item>
        <Form.Item label="角色说明">
          <Input.TextArea v-model:value="formState.description" :rows="2" />
        </Form.Item>
        <Form.Item label="可见菜单">
          <Select v-model:value="formState.menus" mode="multiple" :options="menuOptions" />
        </Form.Item>
        <Form.Item label="资源权限">
          <Select
            v-model:value="formState.permissions"
            mode="multiple"
            :options="permissionOptions"
          />
        </Form.Item>
        <Form.Item label="按钮权限">
          <Select
            v-model:value="formState.buttonPermissions"
            mode="tags"
            :options="permissionOptions"
          />
        </Form.Item>
        <Form.Item label="接口权限">
          <Select
            v-model:value="formState.apiPermissions"
            mode="tags"
            :options="permissionOptions"
          />
        </Form.Item>
        <Form.Item label="数据范围">
          <Select v-model:value="formState.dataScope" :options="dataScopeOptions" />
        </Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.admin-roles-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(59 130 246 / 12%), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.hero-panel,
.summary-card,
.role-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(59 130 246 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(30 64 175 / 8%);
}

.hero-panel {
  display: flex;
  gap: 16px;
  justify-content: space-between;
  padding: 28px 30px;
}

.summary-row,
.list-row {
  margin-top: 18px;
}

.eyebrow,
.label {
  margin: 0 0 10px;
  font-weight: 700;
  color: #2563eb;
}

.description,
.role-head p {
  color: #475569;
  line-height: 1.8;
}

.summary-value {
  font-size: 30px;
  color: #172554;
}

.role-head {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.block {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .admin-roles-page {
    padding: 16px;
  }

  .hero-panel,
  .role-head {
    flex-direction: column;
  }
}
</style>
