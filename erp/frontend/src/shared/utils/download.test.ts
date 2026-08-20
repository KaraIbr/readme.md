import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '../../test/mocks/api-client'
import { downloadFile } from './download'

describe('downloadFile', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.defineProperty(window.URL, 'createObjectURL', {
      configurable: true,
      writable: true,
      value: vi.fn(() => 'blob:test'),
    })
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      configurable: true,
      writable: true,
      value: vi.fn(),
    })
  })

  it('fetches the file as a blob and triggers a download', async () => {
    const blob = new Blob(['data'])
    api.get.mockResolvedValue({ data: blob })
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    const appendSpy = vi.spyOn(document.body, 'appendChild')
    const removeSpy = vi.spyOn(document.body, 'removeChild')

    await downloadFile('/files/report.pdf', 'report.pdf')

    expect(api.get).toHaveBeenCalledWith('/files/report.pdf', { responseType: 'blob' })
    expect(window.URL.createObjectURL).toHaveBeenCalledWith(blob)
    expect(appendSpy).toHaveBeenCalled()
    expect(clickSpy).toHaveBeenCalled()
    expect(removeSpy).toHaveBeenCalled()
    expect(window.URL.revokeObjectURL).toHaveBeenCalled()
  })
})
