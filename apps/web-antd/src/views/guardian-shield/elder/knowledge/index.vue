<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Empty,
  Input,
  List,
  Modal,
  Select,
  Space,
  Tag,
} from 'ant-design-vue';

import {
  getAccessibilitySettingsApi,
  getElderKnowledgeDetailApi,
  getElderKnowledgeListApi,
} from '#/api';
import type { AccessibilitySettings, KnowledgeItem } from '#/api';

defineOptions({ name: 'ElderKnowledge' });

const loading = ref(false);
const detailVisible = ref(false);
const detailLoading = ref(false);
const category = ref<string>();
const keyword = ref('');
const rows = ref<KnowledgeItem[]>([]);
const currentItem = ref<KnowledgeItem>();
const accessibility = reactive<AccessibilitySettings>({
  fontScale: 'large',
  highContrast: false,
  voiceAssistant: false,
  voiceSpeed: 'normal',
});

const categories = computed(() =>
  Array.from(new Set(rows.value.map((item) => item.category))).map((item) => ({
    label: item,
    value: item,
  })),
);

const pageClassName = computed(() => [
  accessibility.highContrast ? 'is-contrast' : '',
  accessibility.fontScale === 'x-large' ? 'is-xl' : 'is-lg',
]);

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await getElderKnowledgeListApi({
      category: category.value,
      keyword: keyword.value.trim() || undefined,
    });
  } finally {
    loading.value = false;
  }
}

async function loadAccessibility() {
  Object.assign(accessibility, await getAccessibilitySettingsApi());
}

async function openDetail(item: KnowledgeItem) {
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    currentItem.value = await getElderKnowledgeDetailApi(item.id);
  } finally {
    detailLoading.value = false;
  }
}

function playContent() {
  if (!currentItem.value || typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return;
  }
  const utterance = new SpeechSynthesisUtterance(
    `${currentItem.value.title}。${currentItem.value.summary || ''}。${currentItem.value.contentBody}`,
  );
  utterance.rate =
    accessibility.voiceSpeed === 'slow'
      ? 0.8
      : accessibility.voiceSpeed === 'fast'
        ? 1.2
        : 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

onMounted(() => {
  void Promise.all([loadRows(), loadAccessibility()]);
});
</script>

<template>
  <div :class="['elder-knowledge-page', ...pageClassName]">
    <Card class="page-card" :bordered="false">
      <p class="eyebrow">老年端 / 防骗知识</p>
      <h1>防骗知识</h1>
      <p class="description">
        已支持分类筛选、关键词搜索、详情查看和语音播报，内容样式会跟随适老设置联动。
      </p>
      <Space wrap style="margin-bottom: 16px">
        <Input
          v-model:value="keyword"
          allow-clear
          placeholder="搜索骗局类型、关键词或建议动作"
          style="width: 240px"
          @press-enter="loadRows"
        />
        <Select
          v-model:value="category"
          allow-clear
          placeholder="选择分类"
          :options="categories"
          style="width: 180px"
          @change="loadRows"
        />
        <Button type="primary" @click="loadRows">查询</Button>
      </Space>
      <List v-if="rows.length" :data-source="rows" :loading="loading">
        <template #renderItem="{ item }">
          <List.Item class="knowledge-item">
            <div>
              <Space wrap>
                <Tag color="blue">{{ item.category }}</Tag>
                <Tag>{{ item.publishStatus }}</Tag>
                <Tag v-if="accessibility.voiceAssistant" color="green">可语音播报</Tag>
              </Space>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary || item.contentBody }}</p>
              <Button size="small" @click="openDetail(item)">查看详情</Button>
            </div>
          </List.Item>
        </template>
      </List>
      <Empty v-else description="暂无知识内容" />
    </Card>

    <Modal
      v-model:open="detailVisible"
      :footer="null"
      title="知识详情"
    >
      <Card :bordered="false" :loading="detailLoading">
        <template v-if="currentItem">
          <Space wrap>
            <Tag color="blue">{{ currentItem.category }}</Tag>
            <Tag>{{ currentItem.publishStatus }}</Tag>
          </Space>
          <h2>{{ currentItem.title }}</h2>
          <p class="detail-summary">{{ currentItem.summary }}</p>
          <p class="detail-body">{{ currentItem.contentBody }}</p>
          <Button v-if="accessibility.voiceAssistant" @click="playContent">
            播放语音
          </Button>
        </template>
      </Card>
    </Modal>
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

h1,
h2 {
  margin: 0;
  color: #3f6212;
}

h1 {
  font-size: 34px;
}

.description,
.knowledge-item p,
.detail-summary,
.detail-body {
  line-height: 1.8;
  color: #4d7c0f;
}

.knowledge-item h3 {
  margin: 10px 0 0;
  color: #365314;
}

.detail-summary {
  margin: 16px 0 10px;
  font-weight: 600;
}

.is-xl {
  font-size: 18px;
}

.is-contrast {
  filter: contrast(1.2);
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
