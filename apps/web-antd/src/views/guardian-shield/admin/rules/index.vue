<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Form,
  Input,
  Modal,
  Select,
  Table,
  Tabs,
  Tag,
  message,
} from 'ant-design-vue';

import {
  createAdminLexiconApi,
  createAdminRuleApi,
  getAdminLexiconListApi,
  getAdminRuleListApi,
  updateAdminLexiconApi,
  updateAdminRuleApi,
} from '#/api';

defineOptions({ name: 'AdminRules' });

const activeKey = ref('rules');
const rows = ref<any[]>([]);
const lexiconRows = ref<any[]>([]);
const visible = ref(false);
const lexiconVisible = ref(false);
const editingId = ref<string>();
const editingLexiconId = ref<string>();

const formState = reactive({
  code: '',
  name: '',
  priority: 100,
  reasonTemplate: '',
  riskLevel: 'high',
  scene: 'sms',
  status: 'enabled',
  suggestionTemplate: '',
  triggerExpression: '',
});

const lexiconState = reactive({
  category: 'sms_keyword',
  notes: '',
  riskLevel: 'high',
  scene: 'sms',
  source: 'manual',
  status: 'enabled',
  term: '',
});

async function loadData() {
  rows.value = await getAdminRuleListApi();
  lexiconRows.value = await getAdminLexiconListApi();
}

function openCreate() {
  editingId.value = undefined;
  Object.assign(formState, {
    code: '',
    name: '',
    priority: 100,
    reasonTemplate: '',
    riskLevel: 'high',
    scene: 'sms',
    status: 'enabled',
    suggestionTemplate: '',
    triggerExpression: '',
  });
  visible.value = true;
}

function openEdit(item: any) {
  editingId.value = item.id;
  Object.assign(formState, item);
  visible.value = true;
}

function openLexiconCreate() {
  editingLexiconId.value = undefined;
  Object.assign(lexiconState, {
    category: 'sms_keyword',
    notes: '',
    riskLevel: 'high',
    scene: 'sms',
    source: 'manual',
    status: 'enabled',
    term: '',
  });
  lexiconVisible.value = true;
}

function openLexiconEdit(item: any) {
  editingLexiconId.value = item.id;
  Object.assign(lexiconState, item);
  lexiconVisible.value = true;
}

async function submitRule() {
  if (editingId.value) {
    await updateAdminRuleApi(editingId.value, { ...formState });
    message.success('规则已更新');
  } else {
    await createAdminRuleApi({ ...formState });
    message.success('规则已新增');
  }
  visible.value = false;
  await loadData();
}

async function submitLexicon() {
  if (editingLexiconId.value) {
    await updateAdminLexiconApi(editingLexiconId.value, { ...lexiconState });
    message.success('风险词已更新');
  } else {
    await createAdminLexiconApi({ ...lexiconState });
    message.success('风险词已新增');
  }
  lexiconVisible.value = false;
  await loadData();
}

onMounted(() => {
  void loadData();
});
</script>

<template>
  <div class="admin-rules-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 风险策略</p>
        <h1>风险规则与词库</h1>
        <p class="description">规则、风险词库和诈骗案例分类已统一收口到真实后端管理。</p>
      </div>
    </section>

    <Card class="list-card" :bordered="false">
      <Tabs v-model:activeKey="activeKey">
        <Tabs.TabPane key="rules" tab="规则管理">
          <Button type="primary" @click="openCreate">新增规则</Button>
          <Table :data-source="rows" row-key="id" style="margin-top: 16px">
            <Table.Column title="编码" data-index="code" key="code" />
            <Table.Column title="名称" data-index="name" key="name" />
            <Table.Column title="场景" data-index="scene" key="scene" />
            <Table.Column title="风险等级" key="riskLevel">
              <template #default="{ record }"><Tag color="red">{{ record.riskLevel }}</Tag></template>
            </Table.Column>
            <Table.Column title="状态" data-index="status" key="status" />
            <Table.Column title="操作" key="actions">
              <template #default="{ record }">
                <Button type="link" size="small" @click="openEdit(record)">编辑</Button>
              </template>
            </Table.Column>
          </Table>
        </Tabs.TabPane>
        <Tabs.TabPane key="lexicon" tab="风险词库">
          <Button type="primary" @click="openLexiconCreate">新增风险词</Button>
          <Table :data-source="lexiconRows" row-key="id" style="margin-top: 16px">
            <Table.Column title="词条" data-index="term" key="term" />
            <Table.Column title="分类" data-index="category" key="category" />
            <Table.Column title="场景" data-index="scene" key="scene" />
            <Table.Column title="风险等级" data-index="riskLevel" key="riskLevel" />
            <Table.Column title="操作" key="actions">
              <template #default="{ record }">
                <Button type="link" size="small" @click="openLexiconEdit(record)">编辑</Button>
              </template>
            </Table.Column>
          </Table>
        </Tabs.TabPane>
        <Tabs.TabPane key="cases" tab="案例库说明">
          <Card size="small">
            诈骗案例库已归入“内容管理”，通过将内容分类设置为 `fraud_case` 进行真实数据维护。
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>

    <Modal v-model:open="visible" title="规则配置" @ok="submitRule">
      <Form layout="vertical">
        <Form.Item label="规则编码"><Input v-model:value="formState.code" /></Form.Item>
        <Form.Item label="规则名称"><Input v-model:value="formState.name" /></Form.Item>
        <Form.Item label="场景">
          <Select v-model:value="formState.scene" :options="[{ label: '短信', value: 'sms' }, { label: '通话', value: 'call' }]" />
        </Form.Item>
        <Form.Item label="风险等级">
          <Select v-model:value="formState.riskLevel" :options="[{ label: '高', value: 'high' }, { label: '中', value: 'medium' }, { label: '低', value: 'low' }]" />
        </Form.Item>
        <Form.Item label="状态">
          <Select v-model:value="formState.status" :options="[{ label: '启用', value: 'enabled' }, { label: '停用', value: 'disabled' }]" />
        </Form.Item>
        <Form.Item label="触发表达式"><Input.TextArea v-model:value="formState.triggerExpression" :rows="3" /></Form.Item>
      </Form>
    </Modal>

    <Modal v-model:open="lexiconVisible" title="风险词配置" @ok="submitLexicon">
      <Form layout="vertical">
        <Form.Item label="词条"><Input v-model:value="lexiconState.term" /></Form.Item>
        <Form.Item label="分类"><Input v-model:value="lexiconState.category" /></Form.Item>
        <Form.Item label="场景">
          <Select v-model:value="lexiconState.scene" :options="[{ label: '短信', value: 'sms' }, { label: '通话', value: 'call' }]" />
        </Form.Item>
        <Form.Item label="风险等级">
          <Select v-model:value="lexiconState.riskLevel" :options="[{ label: '高', value: 'high' }, { label: '中', value: 'medium' }, { label: '低', value: 'low' }]" />
        </Form.Item>
        <Form.Item label="备注"><Input.TextArea v-model:value="lexiconState.notes" :rows="2" /></Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.admin-rules-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #fffdf7 0%, #fff7e8 100%);
}
.hero-panel,
.list-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(245 158 11 / 16%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(146 64 14 / 8%);
}
.hero-panel {
  padding: 28px 30px;
}
.list-card {
  margin-top: 18px;
}
</style>
