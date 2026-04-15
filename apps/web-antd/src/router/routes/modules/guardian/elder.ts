import type { RouteRecordRaw } from 'vue-router';

const elderRoutes: RouteRecordRaw = {
  meta: {
    icon: 'lucide:heart-handshake',
    title: '老年端',
    authority: ['elder'],
  },
  name: 'ElderPortal',
  path: '/elder',
  redirect: '/elder/home',
  children: [
    {
      name: 'ElderHome',
      path: '/elder/home',
      component: () => import('#/views/guardian-shield/elder/home/index.vue'),
      meta: {
        affixTab: true,
        authority: ['elder'],
        icon: 'lucide:house',
        title: '首页',
      },
    },
    {
      name: 'ElderAlerts',
      path: '/elder/alerts',
      component: () => import('#/views/guardian-shield/elder/alerts/index.vue'),
      meta: {
        authority: ['elder'],
        icon: 'lucide:shield-alert',
        title: '风险提醒',
      },
    },
    {
      name: 'ElderHelp',
      path: '/elder/help',
      component: () => import('#/views/guardian-shield/elder/help/index.vue'),
      meta: {
        authority: ['elder'],
        icon: 'lucide:siren',
        title: '一键求助',
      },
    },
    {
      name: 'ElderFamilyBinding',
      path: '/elder/family-binding',
      component: () =>
        import('#/views/guardian-shield/elder/family-binding/index.vue'),
      meta: {
        authority: ['elder'],
        icon: 'lucide:users',
        title: '亲属绑定',
      },
    },
    {
      name: 'ElderKnowledge',
      path: '/elder/knowledge',
      component: () =>
        import('#/views/guardian-shield/elder/knowledge/index.vue'),
      meta: {
        authority: ['elder'],
        icon: 'lucide:book-open',
        title: '防骗知识',
      },
    },
    {
      name: 'ElderSettings',
      path: '/elder/settings',
      component: () =>
        import('#/views/guardian-shield/elder/settings/index.vue'),
      meta: {
        authority: ['elder'],
        icon: 'lucide:settings',
        title: '适老设置',
      },
    },
  ],
};

export default elderRoutes;
