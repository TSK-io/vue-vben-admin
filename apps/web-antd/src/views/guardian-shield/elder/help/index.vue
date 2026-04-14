<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { Button, Card, Col, List, Modal, Row, Space, Tag, message } from 'ant-design-vue';

import { createHelpRequestApi, getBindingListApi } from '#/api';

defineOptions({ name: 'ElderHelp' });

const bindings = ref<any[]>([]);
const actionVisible = ref(false);
const selectedAction = ref('');
const submitting = ref(false);

const familyContacts = computed(() => bindings.value);

async function loadBindings() {
  bindings.value = await getBindingListApi();
}

async function openAction(title: string) {
  selectedAction.value = title;
  actionVisible.value = true;
}

async function submitAction() {
  submitting.value = true;
  try {
    await createHelpRequestApi({
      actionType: selectedAction.value,
      note: `老人发起求助：${selectedAction.value}`,
      notifyCommunity: true,
      notifyFamily: true,
    });
    message.success('求助已发送，家属和社区会收到通知');
    actionVisible.value = false;
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  void loadBindings();
});
</script>

<template>
  <div class="elder-help-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">老年端 / 快速求助</p>
        <h1>一键求助</h1>
        <p class="description">现在已接入真实求助联动。点击按钮后会向家属和社区同步通知，并保留求助记录。</p>
      </div>
      <div class="hero-note">
        <strong>先做这 3 件事</strong>
        <span>先挂电话，不转账，不说验证码。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="action-row">
      <Col :lg="8" :span="24"><Card class="action-card"><Button block size="large" type="primary" @click="openAction('联系家人')">联系家人</Button></Card></Col>
      <Col :lg="8" :span="24"><Card class="action-card"><Button block size="large" type="primary" @click="openAction('同步社区')">同步社区</Button></Card></Col>
      <Col :lg="8" :span="24"><Card class="action-card"><Button block size="large" type="primary" @click="openAction('记录求助')">记录求助</Button></Card></Col>
    </Row>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="15" :span="24">
        <Card class="list-card" :bordered="false" title="家人联系人">
          <List :data-source="familyContacts">
            <template #renderItem="{ item }">
              <List.Item class="contact-item">
                <div class="contact-main">
                  <div>
                    <div class="contact-head">
                      <h3>{{ item.familyName }}</h3>
                      <Tag color="gold">{{ item.relationshipType }}</Tag>
                      <Tag v-if="item.isEmergencyContact" color="blue">紧急联系人</Tag>
                    </div>
                    <p class="contact-note">最近授权：{{ item.authorizedAt }}</p>
                  </div>
                  <Button type="primary" @click="openAction(`联系${item.familyName}`)">联系</Button>
                </div>
              </List.Item>
            </template>
          </List>
        </Card>
      </Col>
      <Col :lg="9" :span="24">
        <Card class="tips-card" :bordered="false" title="当前联动说明">
          <Space direction="vertical">
            <span>会通知已绑定家属联系人</span>
            <span>会同步社区值班人员</span>
            <span>会保留本次求助记录时间</span>
          </Space>
        </Card>
      </Col>
    </Row>

    <Modal v-model:open="actionVisible" title="确认发起求助" ok-text="立即发送" cancel-text="关闭" :confirm-loading="submitting" @ok="submitAction">
      <p>将执行：{{ selectedAction }}</p>
      <p>系统会同时通知家属和社区，便于快速回电或回访。</p>
    </Modal>
  </div>
</template>

<style scoped>
.elder-help-page { min-height: 100%; padding: 24px; background: linear-gradient(180deg, #fff9f5 0%, #fff2ea 100%); }
.hero-panel,.action-card,.list-card,.tips-card { border: 1px solid rgba(249,115,22,.14); border-radius: 24px; background: rgba(255,255,255,.96); box-shadow: 0 16px 36px rgba(124,45,18,.08); }
.hero-panel { display: flex; justify-content: space-between; gap: 20px; padding: 28px 30px; }
.eyebrow { margin: 0 0 12px; color: #ea580c; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
h1 { margin: 0; color: #7c2d12; font-size: 34px; }
.description,.hero-note,.contact-note { color: #7c4a2d; line-height: 1.8; }
.hero-note { max-width: 280px; padding: 18px; border-radius: 20px; background: #fff7ed; }
.action-row,.content-row { margin-top: 18px; }
.contact-main,.contact-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; width: 100%; }
@media (max-width: 768px) { .elder-help-page { padding: 16px; } .hero-panel,.contact-main,.contact-head { flex-direction: column; align-items: flex-start; } h1 { font-size: 28px; } }
</style>
