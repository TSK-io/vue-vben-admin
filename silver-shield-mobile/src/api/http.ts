import { appConfig } from '@/utils/config'

export interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: string | Record<string, any> | ArrayBuffer
  params?: Record<string, any>
  useAiBase?: boolean
  header?: Record<string, string>
}

interface ApiEnvelope<T> {
  data: T
  message?: string
  meta?: Record<string, any>
}

export function request<T>(options: RequestOptions): Promise<T> {
  const baseUrl = options.useAiBase ? appConfig.aiApiBaseUrl : appConfig.apiBaseUrl
  const token = uni.getStorageSync('silver-shield-mobile-auth-token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${baseUrl}${options.url}`,
      method: options.method || 'GET',
      data: options.params ?? options.data,
      timeout: appConfig.apiTimeout,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.header || {}),
      },
      success: (response) => {
        const payload = response.data as ApiEnvelope<T> | T

        if (response.statusCode >= 200 && response.statusCode < 300) {
          if (
            payload &&
            typeof payload === 'object' &&
            !Array.isArray(payload) &&
            'data' in payload
          ) {
            resolve((payload as ApiEnvelope<T>).data)
            return
          }

          resolve(payload as T)
          return
        }

        reject(payload)
      },
      fail: reject,
    })
  })
}
