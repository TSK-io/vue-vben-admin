import type { RouteRecordRaw } from 'vue-router';

const communityRoutes: RouteRecordRaw = {
  meta: {
    icon: 'lucide:building-2',
    title: '社区端',
    authority: ['community'],
  },
  name: 'CommunityPortal',
  path: '/community',
  redirect: '/community/dashboard',
  children: [
    {
      name: 'CommunityDashboard',
      path: '/community/dashboard',
      component: () =>
        import('#/views/guardian-shield/community/dashboard/index.vue'),
      meta: {
        affixTab: true,
        authority: ['community'],
        icon: 'lucide:chart-column-big',
        title: '辖区总览',
      },
    },
    {
      name: 'CommunitySeniors',
      path: '/community/seniors',
      component: () =>
        import('#/views/guardian-shield/community/seniors/index.vue'),
      meta: {
        authority: ['community'],
        icon: 'lucide:user-round-search',
        title: '重点老人',
      },
    },
    {
      name: 'CommunityWorkorders',
      path: '/community/workorders',
      component: () =>
        import('#/views/guardian-shield/community/workorders/index.vue'),
      meta: {
        authority: ['community'],
        icon: 'lucide:files',
        title: '风险工单',
      },
    },
    {
      name: 'CommunityEducation',
      path: '/community/education',
      component: () =>
        import('#/views/guardian-shield/community/education/index.vue'),
      meta: {
        authority: ['community'],
        icon: 'lucide:megaphone',
        title: '宣教管理',
      },
    },
    {
      name: 'CommunityReports',
      path: '/community/reports',
      component: () =>
        import('#/views/guardian-shield/community/reports/index.vue'),
      meta: {
        authority: ['community'],
        icon: 'lucide:file-bar-chart',
        title: '统计报表',
      },
    },
  ],
};

export default communityRoutes;
