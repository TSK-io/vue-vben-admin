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
  createAdminRuleApi,
  getAdminRuleListApi,
  updateAdminRuleApi,
} from '#/api';

defineOptions({ name: 'AdminRules' });

const rows = ref<any[]>([]);
const visible = ref(false);
const editingId = ref<string>();
const formState = reactive({
  code: '',
  name: '',
  scene: 'sms',
  riskLevel: 'high',
  priority: 100,
  status: 'enabled',
  triggerExpression: '',
  reasonTemplate: '',
  suggestionTemplate: '',
});

async function loadRows() {
  rows.value = await getAdminRuleListApi();
}

function openCreate() {
  editingId.value = undefined;
  Object.assign(formState, {
    code: '',
    name: '',
    scene: 'sms',
    riskLevel: 'high',
    priority: 100,
    status: 'enabled',
    triggerExpression: '',
    reasonTemplate: '',
    suggestionTemplate: '',
  });
  visible.value = true;
}

function openEdit(item: any) {
  editingId.value = item.id;
  Object.assign(formState, item);
  visible.value = true;
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
  await loadRows();
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="admin-rules-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 规则管理</p>
        <h1>风险规则</h1>
        <p class="description">规则管理已切到真实后端，支持新增和编辑规则。</p>
      </div>
      <Button type="primary" @click="openCreate">新增规则</Button>
    </section>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="8" :span="24">
        <Card class="rule-card" :bordered="false">
          <div class="card-head">
            <div>
              <h3>{{ item.name }}</h3>
              <p>{{ item.code }} · {{ item.scene }}</p>
            </div>
            <Button size="small" @click="openEdit(item)">编辑</Button>
          </div>
          <Space wrap>
            <Tag color="red">{{ item.riskLevel }}</Tag>
            <Tag color="blue">{{ item.scene }}</Tag>
            <Tag :color="item.status === 'enabled' ? 'success' : 'default'">{{
              item.status
            }}</Tag>
          </Space>
          <div class="block">
            <p class="label">触发表达式</p>
            <p class="value">{{ item.triggerExpression }}</p>
          </div>
        </Card>
      </Col>
    </Row>

    <Modal
      v-model:open="visible"
      title="规则配置"
      ok-text="保存"
      cancel-text="关闭"
      @ok="submitRule"
    >
      <Form layout="vertical">
        <Form.Item label="规则编码"
          ><Input v-model:value="formState.code"
        /></Form.Item>
        <Form.Item label="规则名称"
          ><Input v-model:value="formState.name"
        /></Form.Item>
        <Form.Item label="场景"
          ><Select
            v-model:value="formState.scene"
            :options="[
              { label: '短信', value: 'sms' },
              { label: '通话', value: 'call' },
            ]"
        /></Form.Item>
        <Form.Item label="风险等级"
          ><Select
            v-model:value="formState.riskLevel"
            :options="[
              { label: '高', value: 'high' },
              { label: '中', value: 'medium' },
              { label: '低', value: 'low' },
            ]"
        /></Form.Item>
        <Form.Item label="触发表达式"
          ><Input.TextArea
            v-model:value="formState.triggerExpression"
            :rows="3"
        /></Form.Item>
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
.rule-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(245 158 11 / 16%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(146 64 14 / 8%);
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
  color: #d97706;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #92400e;
}

.description,
.value,
.card-head p {
  line-height: 1.8;
  color: #78350f;
}

.list-row {
  margin-top: 18px;
}

.card-head {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.label {
  margin: 0;
  font-weight: 700;
  color: #b45309;
}

@media (max-width: 768px) {
  .admin-rules-page {
    padding: 16px;
  }

  .hero-panel,
  .card-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
