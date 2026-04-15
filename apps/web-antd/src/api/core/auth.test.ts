import { beforeEach, describe, expect, it, vi } from 'vitest';

const { baseRequestClient, requestClient } = vi.hoisted(() => ({
  requestClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
  baseRequestClient: {
    post: vi.fn(),
  },
}));

vi.mock('#/api/request', () => ({
  baseRequestClient,
  requestClient,
}));

import {
  getAccessCodesApi,
  loginApi,
  logoutApi,
  refreshTokenApi,
  registerApi,
} from './auth';

describe('auth api', () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('maps snake_case login and refresh responses to camelCase', async () => {
    requestClient.post
      .mockResolvedValueOnce({ access_token: 'token-1' })
      .mockResolvedValueOnce({ access_token: 'token-2' });

    await expect(loginApi({ username: 'demo', password: '111' })).resolves.toEqual({
      accessToken: 'token-1',
    });
    await expect(refreshTokenApi()).resolves.toEqual({
      accessToken: 'token-2',
    });
  });

  it('serializes register payload fields for fastapi', async () => {
    requestClient.post.mockResolvedValueOnce({ success: true });

    await registerApi({
      username: 'elder_demo',
      password: '111',
      displayName: '李阿姨',
      phone: '13800001001',
      role: 'elder',
      inviteCode: 'ELDER-INVITE-001',
    });

    expect(requestClient.post).toHaveBeenCalledWith('/auth/register', {
      username: 'elder_demo',
      password: '111',
      display_name: '李阿姨',
      phone: '13800001001',
      role: 'elder',
      invite_code: 'ELDER-INVITE-001',
    });
  });

  it('reads permissions from profile and forwards logout', async () => {
    requestClient.get.mockResolvedValueOnce({
      permissions: ['alerts:read', 'notifications:read'],
    });
    baseRequestClient.post.mockResolvedValueOnce({ success: true });

    await expect(getAccessCodesApi()).resolves.toEqual([
      'alerts:read',
      'notifications:read',
    ]);
    await logoutApi();

    expect(baseRequestClient.post).toHaveBeenCalledWith('/auth/logout', {
      withCredentials: true,
    });
  });
});
