import { api } from '@services/api-client'

export async function downloadFile(url: string, filename: string): Promise<void> {
  const { data } = await api.get(url, { responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = blobUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(blobUrl)
}
