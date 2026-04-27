import type { GuardianRole, PhoneDirectoryUser } from '#/types/guardian-phone';

import { requestClient } from '#/api/request';

export async function lookupPhoneApi(phone: string, role?: GuardianRole) {
  const result = await requestClient.get<any>('/phone-directory/lookup', {
    params: { phone, role },
  });
  return {
    displayName: result.display_name,
    phone: result.phone,
    roles: result.roles,
    status: result.status,
    userId: result.user_id,
    username: result.username,
  } satisfies PhoneDirectoryUser;
}
