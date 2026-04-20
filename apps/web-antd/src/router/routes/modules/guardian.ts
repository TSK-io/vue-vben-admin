import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:shield-check',
      title: '后台管理',
      authority: ['admin', 'ops', 'reviewer', 'support'],
    },
    name: 'AdminPortal',
    path: '/admin',
    redirect: '/admin/users',
    children: [
      {
        name: 'AdminUsers',
        path: '/admin/users',
        component: () =>
          import('#/views/guardian-shield/admin/users/index.vue'),
        meta: {
          affixTab: true,
          authority: ['admin', 'ops'],
          icon: 'lucide:users',
          title: '用户管理',
        },
      },
      {
        name: 'AdminRoles',
        path: '/admin/roles',
        component: () =>
          import('#/views/guardian-shield/admin/roles/index.vue'),
        meta: {
          authority: ['admin'],
          icon: 'lucide:key-round',
          title: '角色权限',
        },
      },
      {
        name: 'AdminRules',
        path: '/admin/rules',
        component: () =>
          import('#/views/guardian-shield/admin/rules/index.vue'),
        meta: {
          authority: ['admin', 'reviewer'],
          icon: 'lucide:scan-search',
          title: '风险规则',
        },
      },
      {
        name: 'AdminContents',
        path: '/admin/contents',
        component: () =>
          import('#/views/guardian-shield/admin/contents/index.vue'),
        meta: {
          authority: ['admin', 'ops'],
          icon: 'lucide:book-copy',
          title: '内容管理',
        },
      },
      {
        name: 'AdminSystemSettings',
        path: '/admin/system-settings',
        component: () =>
          import('#/views/guardian-shield/admin/system-settings/index.vue'),
        meta: {
          authority: ['admin'],
          icon: 'lucide:settings-2',
          title: '系统配置',
        },
      },
    ],
  },
];

export default routes;
