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
  getCommunitySeniorListApi,
  updateCommunitySeniorFollowupApi,
} from '#/api';

defineOptions({ name: 'CommunitySeniors' });

const filters = reactive({
  keyword: '',
  riskLevel: undefined as string | undefined,
});
const rows = ref<any[]>([]);
const visible = ref(false);
const currentId = ref<string>();
const followupForm = reactive({
  followUpStatus: 'phone_following',
  manualRiskTag: 'high',
  note: '',
  recordType: 'phone_visit',
});

async function loadRows() {
  const result = await getCommunitySeniorListApi({
    keyword: filters.keyword || undefined,
    page: 1,
    pageSize: 20,
    riskLevel: filters.riskLevel,
  });
  rows.value = result.items;
}

function openFollowup(item: any) {
  currentId.value = item.id;
  Object.assign(followupForm, {
    followUpStatus: item.followUpStatus,
    manualRiskTag: item.manualRiskTag || item.riskLevel,
    note: '',
    recordType: 'phone_visit',
  });
  visible.value = true;
}

async function submitFollowup() {
  if (!currentId.value) return;
  await updateCommunitySeniorFollowupApi(currentId.value, { ...followupForm });
  visible.value = false;
  message.success('跟进记录已保存');
  await loadRows();
}

function getRiskMeta(level: 'high' | 'low' | 'medium') {
  if (level === 'high') return { color: 'red', text: '高风险' };
  if (level === 'medium') return { color: 'orange', text: '中风险' };
  return { color: 'green', text: '低风险' };
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="community-seniors-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 重点对象</p>
        <h1>重点老人</h1>
        <p class="description">已支持高风险标记、电话回访、走访记录和宣教录入。</p>
      </div>
    </section>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Input v-model:value="filters.keyword" allow-clear placeholder="搜索老人、标签或回访状态" style="width: 260px" />
        <Select
          v-model:value="filters.riskLevel"
          allow-clear
          placeholder="风险等级"
          style="width: 160px"
          :options="[
            { label: '高风险', value: 'high' },
            { label: '中风险', value: 'medium' },
            { label: '低风险', value: 'low' },
          ]"
        />
        <Button type="primary" @click="loadRows">查询</Button>
      </Space>
    </Card>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="12" :span="24">
        <Card class="senior-card" :bordered="false">
          <div class="card-head">
            <div>
              <h3>{{ item.elderName }}</h3>
              <p>{{ item.id }} · {{ item.followUpStatus }}</p>
            </div>
            <Space>
              <Tag v-if="item.manualRiskTag" color="magenta">人工标记 {{ item.manualRiskTag }}</Tag>
              <Tag :color="getRiskMeta(item.riskLevel).color">{{ getRiskMeta(item.riskLevel).text }}</Tag>
            </Space>
          </div>
          <div class="tag-row">
            <Tag v-for="tag in item.labels" :key="tag" color="blue">{{ tag }}</Tag>
          </div>
          <div class="info-block">
            <p class="label">协同信息</p>
            <p class="value">{{ item.collaboration }}</p>
            <p class="label" style="margin-top: 12px">最近跟进</p>
            <p class="value">
              {{ item.visitRecords[0]?.record_type || '暂无' }} ·
              {{ item.visitRecords[0]?.note || '尚未录入跟进记录' }}
            </p>
          </div>
          <Button style="margin-top: 16px" @click="openFollowup(item)">补录回访/宣教</Button>
        </Card>
      </Col>
    </Row>

    <Modal v-model:open="visible" title="补录跟进" @ok="submitFollowup">
      <Form layout="vertical">
        <Form.Item label="跟进状态">
          <Select
            v-model:value="followupForm.followUpStatus"
            :options="[
              { label: '电话回访中', value: 'phone_following' },
              { label: '待上门', value: 'pending_visit' },
              { label: '宣教完成', value: 'education_done' },
            ]"
          />
        </Form.Item>
        <Form.Item label="人工风险标记">
          <Select
            v-model:value="followupForm.manualRiskTag"
            :options="[
              { label: '高风险', value: 'high' },
              { label: '中风险', value: 'medium' },
              { label: '低风险', value: 'low' },
            ]"
          />
        </Form.Item>
        <Form.Item label="记录类型">
          <Select
            v-model:value="followupForm.recordType"
            :options="[
              { label: '电话回访', value: 'phone_visit' },
              { label: '上门走访', value: 'onsite_visit' },
              { label: '现场宣教', value: 'onsite_education' },
            ]"
          />
        </Form.Item>
        <Form.Item label="备注">
          <Input.TextArea v-model:value="followupForm.note" :rows="3" />
        </Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.community-seniors-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #f6fffb 0%, #edfff7 100%);
}
.hero-panel,
.filter-card,
.senior-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(16 185 129 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(6 95 70 / 8%);
}
.hero-panel {
  padding: 28px 30px;
}
.filter-card,
.list-row {
  margin-top: 18px;
}
.card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}
.info-block {
  padding: 18px;
  margin-top: 16px;
  background: #f0fdf4;
  border-radius: 18px;
}
</style>
