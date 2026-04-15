<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Drawer,
  Row,
  Space,
  Table,
  Tag,
} from 'ant-design-vue';

import {
  getAdminRiskAlertDetailApi,
  getAdminRiskAlertListApi,
} from '#/api';

defineOptions({ name: 'AdminAlerts' });

const loading = ref(false);
const detailVisible = ref(false);
const rows = ref<any[]>([]);
const currentDetail = ref<any>(null);

const summaryCards = computed(() => [
  { title: '告警总数', value: `${rows.value.length}` },
  { title: '高风险', value: `${rows.value.filter((item) => item.riskLevel === 'high').length}` },
  { title: '联动通知', value: `${rows.value.reduce((sum, item) => sum + item.relatedNotifications, 0)}` },
  { title: '关联工单', value: `${rows.value.reduce((sum, item) => sum + item.relatedWorkorders, 0)}` },
]);

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await getAdminRiskAlertListApi();
  } finally {
    loading.value = false;
  }
}

async function openDetail(alertId: string) {
  currentDetail.value = await getAdminRiskAlertDetailApi(alertId);
  detailVisible.value = true;
}

function exportCsv() {
  const header = ['告警ID', '老人', '标题', '风险等级', '来源', '状态', '发生时间'];
  const lines = rows.value.map((item) =>
    [
      item.id,
      item.elderName,
      item.title,
      item.riskLevel,
      item.sourceType,
      item.status,
      item.occurredAt,
    ].join(','),
  );
  const blob = new Blob([[header.join(','), ...lines].join('\n')], {
    type: 'text/csv;charset=utf-8',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'risk-alerts.csv';
  link.click();
  URL.revokeObjectURL(url);
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="admin-alerts-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 告警中心</p>
        <h1>告警记录</h1>
        <p class="description">支持独立检索、详情追踪和 CSV 导出，便于统一查看处置闭环。</p>
      </div>
      <Button type="primary" @click="exportCsv">导出 CSV</Button>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="6" :span="24">
        <Card class="summary-card" :bordered="false">
          <p>{{ item.title }}</p>
          <strong>{{ item.value }}</strong>
        </Card>
      </Col>
    </Row>

    <Card class="table-card" :bordered="false">
      <Table :data-source="rows" :loading="loading" row-key="id" :pagination="{ pageSize: 8 }">
        <Table.Column title="标题" data-index="title" key="title" />
        <Table.Column title="老人" data-index="elderName" key="elderName" />
        <Table.Column title="风险" key="riskLevel">
          <template #default="{ record }">
            <Tag :color="record.riskLevel === 'high' ? 'red' : record.riskLevel === 'medium' ? 'orange' : 'green'">
              {{ record.riskLevel }}
            </Tag>
          </template>
        </Table.Column>
        <Table.Column title="联动" key="linked">
          <template #default="{ record }">
            {{ record.relatedNotifications }} 通知 / {{ record.relatedWorkorders }} 工单
          </template>
        </Table.Column>
        <Table.Column title="发生时间" data-index="occurredAt" key="occurredAt" />
        <Table.Column title="操作" key="actions">
          <template #default="{ record }">
            <Button type="link" size="small" @click="openDetail(record.id)">查看详情</Button>
          </template>
        </Table.Column>
      </Table>
    </Card>

    <Drawer v-model:open="detailVisible" width="520" title="告警详情">
      <Space v-if="currentDetail" direction="vertical" style="width: 100%">
        <Card size="small">
          <p><strong>{{ currentDetail.title }}</strong></p>
          <p>{{ currentDetail.elderName }} · {{ currentDetail.occurredAt }}</p>
          <Tag color="red">{{ currentDetail.riskLevel }}</Tag>
        </Card>
        <Card size="small" title="命中原因">{{ currentDetail.reasonDetail }}</Card>
        <Card size="small" title="建议动作">{{ currentDetail.suggestionAction }}</Card>
        <Card size="small" title="关联记录">
          <p>通知：{{ currentDetail.relatedNotificationIds.join('、') || '无' }}</p>
          <p>工单：{{ currentDetail.relatedWorkorderIds.join('、') || '无' }}</p>
        </Card>
      </Space>
    </Drawer>
  </div>
</template>

<style scoped>
.admin-alerts-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #fff8f8 0%, #fff1f2 100%);
}
.hero-panel,
.summary-card,
.table-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(244 63 94 / 12%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(159 18 57 / 8%);
}
.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 28px 30px;
}
.summary-row,
.table-card {
  margin-top: 18px;
}
</style>
