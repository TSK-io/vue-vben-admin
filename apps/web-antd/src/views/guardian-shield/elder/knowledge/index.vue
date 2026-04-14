<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { Card, Empty, List, Select, Space, Tag } from 'ant-design-vue';

import { getElderKnowledgeListApi } from '#/api';

defineOptions({ name: 'ElderKnowledge' });

const loading = ref(false);
const category = ref<string>();
const rows = ref<any[]>([]);

const categories = computed(() =>
  Array.from(new Set(rows.value.map((item) => item.category))).map((item) => ({
    label: item,
    value: item,
  })),
);

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await getElderKnowledgeListApi(category.value);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="elder-knowledge-page">
    <Card class="page-card" :bordered="false">
      <p class="eyebrow">老年端 / 防骗知识</p>
      <h1>防骗知识</h1>
      <p class="description">
        知识库已接后台内容，可按分类查看图文案例和提示内容。
      </p>
      <Space style="margin-bottom: 16px">
        <Select
          v-model:value="category"
          allow-clear
          placeholder="选择分类"
          :options="categories"
          style="width: 180px"
          @change="loadRows"
        />
      </Space>
      <List v-if="rows.length" :data-source="rows" :loading="loading">
        <template #renderItem="{ item }">
          <List.Item class="knowledge-item">
            <div>
              <Space wrap>
                <Tag color="blue">{{ item.category }}</Tag>
                <Tag>{{ item.publishStatus }}</Tag>
              </Space>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary || item.contentBody }}</p>
            </div>
          </List.Item>
        </template>
      </List>
      <Empty v-else description="暂无知识内容" />
    </Card>
  </div>
</template>

<style scoped>
.elder-knowledge-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #f7fff8 0%, #eefcf2 100%);
}

.page-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(101 163 13 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(77 124 15 / 8%);
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #65a30d;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #3f6212;
}

.description,
.knowledge-item p {
  line-height: 1.8;
  color: #4d7c0f;
}

.knowledge-item h3 {
  margin: 10px 0 0;
  color: #365314;
}

@media (max-width: 768px) {
  .elder-knowledge-page {
    padding: 16px;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
