export const appConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  aiApiBaseUrl: import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:3001',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT || 10000),
}
