import { request } from '@/api/http'
import { backendModules } from '@/api/modules'
import { appConfig } from '@/utils/config'

interface CreateSosPayload {
  elderId: string
  elderName: string
  summary: string
  detail: string
}

interface CreateSosResponse {
  action_type: string
  created_at: string
  help_id: string
  notification_ids: string[]
  summary: string
}

async function requestWithFallback<T>(
  run: () => Promise<T>,
  fallback: () => T,
): Promise<T> {
  try {
    if (appConfig.appEnv === 'demo') {
      return fallback()
    }

    return await run()
  } catch {
    return fallback()
  }
}

export function createSosAlert(payload: CreateSosPayload): Promise<CreateSosResponse> {
  return requestWithFallback(
    () =>
      request<CreateSosResponse>({
        url: backendModules.main.sos,
        method: 'POST',
        data: {
          action_type: '一键求助',
          note: payload.detail,
          notify_community: true,
          notify_family: true,
        },
      }),
    () => ({
      action_type: '一键求助',
      created_at: new Date().toISOString(),
      help_id: `sos-${Date.now()}`,
      notification_ids: [],
      summary: payload.summary,
    }),
  )
}
