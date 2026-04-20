export const backendModules = {
  main: {
    login: '/api/v1/auth/login',
    profile: '/api/v1/auth/me',
    binding: '/api/v1/bindings',
    alerts: '/api/v1/risk-alerts',
    alertDetail: '/api/v1/risk-alerts',
    elderSettings: '/api/v1/elder/accessibility-settings',
    elderKnowledge: '/api/v1/elder/knowledge',
    familyReminders: '/api/v1/family/reminders',
    notifications: '/api/v1/notifications',
    sos: '/api/v1/elder/help-requests'
  },
  ai: {
    messageDetect: '/api/fraud-detect',
    chatLogDetect: '/api/fraud-detect/chat-log',
    linkDetect: '/api/fraud-detect/link'
  }
}
