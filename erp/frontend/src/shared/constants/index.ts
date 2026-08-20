export const APP_NAME = 'VERP CRM'

export const PAGINATION = {
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100] as const,
} as const

export const DATE_FORMAT = {
  display: 'MMM d, yyyy',
  api: "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'",
  short: 'MM/dd/yyyy',
} as const
