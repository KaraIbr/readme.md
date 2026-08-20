import axios from 'axios'

export function createAxiosInstance(baseURL: string) {
  const instance = axios.create({
    baseURL,
    timeout: 30_000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  return instance
}
