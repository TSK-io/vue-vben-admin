import type { RouteRecordRaw } from 'vue-router';

const familyRoutes: RouteRecordRaw = {
  meta: {
    icon: 'lucide:bell-ring',
    title: '子女端',
    authority: ['family'],
  },
  name: 'FamilyPortal',
  path: '/family',
  redirect: '/family/overview',
  children: [
    {
      name: 'FamilyOverview',
      path: '/family/overview',
      component: () =>
        import('#/views/guardian-shield/family/overview/index.vue'),
      meta: {
        affixTab: true,
        authority: ['family'],
        icon: 'lucide:layout-dashboard',
        title: '监护总览',
      },
    },
    {
      name: 'FamilySeniors',
      path: '/family/seniors',
      component: () => import('#/views/guardian-shield/family/seniors/index.vue'),
      meta: {
        authority: ['family'],
        icon: 'lucide:users-round',
        title: '老人列表',
      },
    },
    {
      name: 'FamilyAlerts',
      path: '/family/alerts',
      component: () => import('#/views/guardian-shield/family/alerts/index.vue'),
      meta: {
        authority: ['family'],
        icon: 'lucide:shield-alert',
        title: '风险详情',
      },
    },
    {
      name: 'FamilyNotifications',
      path: '/family/notifications',
      component: () =>
        import('#/views/guardian-shield/family/notifications/index.vue'),
      meta: {
        authority: ['family'],
        icon: 'lucide:mail-warning',
        title: '通知记录',
      },
    },
    {
      name: 'FamilySettings',
      path: '/family/settings',
      component: () =>
        import('#/views/guardian-shield/family/settings/index.vue'),
      meta: {
        authority: ['family'],
        icon: 'lucide:sliders-horizontal',
        title: '监护设置',
      },
    },
  ],
};

export default familyRoutes;
