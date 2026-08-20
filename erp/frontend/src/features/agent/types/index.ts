export interface AgentMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AgentChatRequest {
  message: string
  history: AgentMessage[]
}

export interface AgentEvidence {
  source: string
  record_type: string | null
  record_id: number | null
  display_name: string | null
}

export interface AgentChatResponse {
  answer: string
  selected_skills: string[]
  tool_calls: string[]
  evidence: AgentEvidence[]
  needs_confirmation: boolean
}

export interface ChatMessage extends AgentMessage {
  id: string
  evidence?: AgentEvidence[]
  tool_calls?: string[]
  selected_skills?: string[]
  needs_confirmation?: boolean
  isError?: boolean
}
