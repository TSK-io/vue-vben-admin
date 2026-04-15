import { describe, expect, it } from 'vitest';

import guardianRoutes from './guardian';

describe('guardian routes', () => {
  it('covers four role portals and key pages', () => {
    const portalNames = guardianRoutes.map((route) => route.name);
    expect(portalNames).toEqual([
      'ElderPortal',
      'FamilyPortal',
      'CommunityPortal',
      'AdminPortal',
    ]);

    const expectations = [
      ['ElderPortal', ['ElderHome', 'ElderAlerts', 'ElderHelp', 'ElderFamilyBinding', 'ElderKnowledge', 'ElderSettings']],
      ['FamilyPortal', ['FamilyOverview', 'FamilySeniors', 'FamilyAlerts', 'FamilyNotifications', 'FamilySettings']],
      ['CommunityPortal', ['CommunityDashboard', 'CommunitySeniors', 'CommunityWorkorders', 'CommunityEducation', 'CommunityReports']],
      ['AdminPortal', ['AdminUsers', 'AdminRoles', 'AdminRules', 'AdminContents', 'AdminSystemSettings']],
    ] as const;

    for (const [portalName, childNames] of expectations) {
      const portal = guardianRoutes.find((route) => route.name === portalName);
      expect(portal?.meta?.authority).toHaveLength(1);
      expect((portal?.children ?? []).map((child) => child.name)).toEqual(childNames);
    }
  });
});
