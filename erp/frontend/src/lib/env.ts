export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  appName: import.meta.env.VITE_APP_NAME ?? 'VERP CRM',
  appVersion: import.meta.env.VITE_APP_VERSION ?? '0.5.0',
} as const
