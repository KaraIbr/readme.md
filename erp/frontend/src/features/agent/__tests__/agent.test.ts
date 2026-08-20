import { describe, it, expect } from 'vitest'
import { api } from '../../../test/mocks/api-client'
import { sendChatMessage } from '../services/agent.service'

describe('agent api service', () => {
  it('sends a chat message', async () => {
    const body = {
      message: 'How many leads did I close?',
      history: [{ role: 'user' as const, content: 'Hi' }],
    }
    const response = {
      answer: 'You closed 2 leads.',
      selected_skills: [],
      tool_calls: [],
      evidence: [],
      needs_confirmation: false,
    }
    api.post.mockResolvedValue({ data: response })

    const result = await sendChatMessage(body)

    expect(api.post).toHaveBeenCalledWith('/agent/chat', body)
    expect(result).toEqual(response)
  })
})
