<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import { Button, Card, Col, Form, Input, List, Modal, Row, Select, Space, Tag, message } from 'ant-design-vue';

import { createBindingApi, deleteBindingApi, getBindingListApi, updateBindingApi } from '#/api';
import { useUserStore } from '@vben/stores';

defineOptions({ name: 'ElderFamilyBinding' });

const userStore = useUserStore();
const bindings = ref<any[]>([]);
const modalVisible = ref(false);
const editingId = ref<string>();
const formState = reactive({
  familyUserId: 'u-family-001',
  isEmergencyContact: false,
  relationshipType: 'daughter',
});

const availableSlots = computed(() => Math.max(0, 3 - bindings.value.length));

async function loadBindings() {
  bindings.value = await getBindingListApi();
}

function openCreate() {
  editingId.value = undefined;
  formState.familyUserId = 'u-family-001';
  formState.isEmergencyContact = false;
  formState.relationshipType = 'daughter';
  modalVisible.value = true;
}

function openEdit(item: any) {
  editingId.value = item.id;
  formState.familyUserId = item.familyUserId;
  formState.isEmergencyContact = item.isEmergencyContact;
  formState.relationshipType = item.relationshipType;
  modalVisible.value = true;
}

async function submitBinding() {
  if (editingId.value) {
    await updateBindingApi(editingId.value, {
      isEmergencyContact: formState.isEmergencyContact,
      relationshipType: formState.relationshipType,
      status: 'active',
    });
    message.success('绑定关系已更新');
  } else {
    await createBindingApi({
      elderUserId: userStore.userInfo?.userId || 'u-elder-001',
      familyUserId: formState.familyUserId,
      isEmergencyContact: formState.isEmergencyContact,
      relationshipType: formState.relationshipType,
    });
    message.success('绑定成功');
  }
  modalVisible.value = false;
  await loadBindings();
}

async function removeBinding(id: string) {
  await deleteBindingApi(id);
  message.success('已解绑');
  await loadBindings();
}
</script>

<template>
  <div class="elder-family-binding-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">老年端 / 亲属绑定</p>
        <h1>亲属绑定</h1>
        <p class="description">页面已接真实 `bindings` 接口，支持新增、修改和解绑，并保留紧急联系人标记。</p>
      </div>
      <div class="hero-note">
        <strong>当前状态</strong>
        <span>已绑定 {{ bindings.length }} 人，还可新增 {{ availableSlots }} 人。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="16" :span="24">
        <Card class="list-card" :bordered="false" title="已绑定亲属">
          <List :data-source="bindings">
            <template #renderItem="{ item }">
              <List.Item class="binding-item">
                <div class="binding-main">
                  <div>
                    <div class="binding-head">
                      <h3>{{ item.familyName }}</h3>
                      <Tag color="gold">{{ item.relationshipType }}</Tag>
                      <Tag v-if="item.isEmergencyContact" color="blue">默认联系人</Tag>
                      <Tag :color="item.status === 'active' ? 'success' : 'warning'">{{ item.status }}</Tag>
                    </div>
                    <p class="binding-time">最近授权：{{ item.authorizedAt }}</p>
                  </div>
                  <Space wrap>
                    <Button @click="openEdit(item)">修改</Button>
                    <Button danger @click="removeBinding(item.id)">解绑</Button>
                  </Space>
                </div>
              </List.Item>
            </template>
          </List>
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="flow-card" :bordered="false" title="绑定流程">
          <p>支持新增家属、更新关系和重新设为紧急联系人。</p>
          <Button block size="large" type="primary" :disabled="availableSlots <= 0" @click="openCreate">新增绑定</Button>
        </Card>
      </Col>
    </Row>

    <Modal v-model:open="modalVisible" title="绑定家属" ok-text="保存" cancel-text="关闭" @ok="submitBinding">
      <Form layout="vertical">
        <Form.Item label="家属账号">
          <Select
            v-model:value="formState.familyUserId"
            :options="[
              { label: '王女士', value: 'u-family-001' },
              { label: '李先生', value: 'u-family-002' },
            ]"
          />
        </Form.Item>
        <Form.Item label="关系">
          <Input v-model:value="formState.relationshipType" />
        </Form.Item>
        <Form.Item label="紧急联系人">
          <Select
            v-model:value="formState.isEmergencyContact"
            :options="[
              { label: '是', value: true },
              { label: '否', value: false },
            ]"
          />
        </Form.Item>
      </Form>
    </Modal>
  </div>
</template>

<style scoped>
.elder-family-binding-page { min-height: 100%; padding: 24px; background: linear-gradient(180deg, #f8fcff 0%, #eef7ff 100%); }
.hero-panel,.list-card,.flow-card { border: 1px solid rgba(14,165,233,.14); border-radius: 24px; background: rgba(255,255,255,.96); box-shadow: 0 16px 36px rgba(14,116,144,.08); }
.hero-panel { display: flex; justify-content: space-between; gap: 20px; padding: 28px 30px; }
.eyebrow { margin: 0 0 12px; color: #0284c7; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
h1 { margin: 0; color: #0f172a; font-size: 34px; }
.description,.hero-note,.binding-time { color: #334155; line-height: 1.8; }
.hero-note { max-width: 280px; padding: 18px; border-radius: 20px; background: #eff6ff; }
.content-row { margin-top: 18px; }
.binding-main,.binding-head { display: flex; justify-content: space-between; gap: 12px; width: 100%; align-items: center; }
@media (max-width: 768px) { .elder-family-binding-page { padding: 16px; } .hero-panel,.binding-main,.binding-head { flex-direction: column; align-items: flex-start; } h1 { font-size: 28px; } }
</style>
