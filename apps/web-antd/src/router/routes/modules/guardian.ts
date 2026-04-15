import type { RouteRecordRaw } from 'vue-router';

import adminRoutes from './guardian/admin';
import communityRoutes from './guardian/community';
import elderRoutes from './guardian/elder';
import familyRoutes from './guardian/family';

const routes: RouteRecordRaw[] = [
  elderRoutes,
  familyRoutes,
  communityRoutes,
  adminRoutes,
];

export default routes;
