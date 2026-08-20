import type { AxiosInstance, AxiosResponse } from 'axios'
import { createAxiosInstance } from '@lib/axios'
import { env } from '@lib/env'

const api: AxiosInstance = initApi()
let pendingRefresh: Promise<void> | null = null

async function doRefresh(): Promise<void> {
  await createAxiosInstance(env.apiBaseUrl).post(
    '/identity/auth/refresh',
    {},
    { withCredentials: true },
  )
}

function initApi(): AxiosInstance {
  const instance = createAxiosInstance(env.apiBaseUrl)

  instance.interceptors.request.use((req) => {
    req.withCredentials = true
    return req
  })

  instance.interceptors.response.use(
    (res: AxiosResponse) => res,
    async (error) => {
      const originalRequest = error.config
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        try {
          pendingRefresh = pendingRefresh ?? doRefresh()
          await pendingRefresh
          pendingRefresh = null
          return instance(originalRequest)
        } catch {
          pendingRefresh = null
          window.location.href = '/login'
          return Promise.reject(error)
        }
      }
      return Promise.reject(error)
    },
  )

  return instance
}

export { api }
