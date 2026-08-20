import { api } from '@services/api-client'
import type { AgentChatRequest, AgentChatResponse } from '../types'

export async function sendChatMessage(body: AgentChatRequest): Promise<AgentChatResponse> {
  const { data } = await api.post<AgentChatResponse>('/agent/chat', body)
  return data
}
