import { useState, useRef, useEffect, useCallback } from 'react'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { sendChatMessage } from '../services/agent.service'
import type { ChatMessage, AgentEvidence } from '../types'

function EvidencePill({ evidence }: { evidence: AgentEvidence }) {
  return (
    <a
      href={evidence.source}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs hover:bg-primary/20 transition-colors"
    >
      <svg className="size-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
      </svg>
      {evidence.display_name ?? evidence.source}
    </a>
  )
}

function AssistantMessage({ message }: { message: ChatMessage }) {
  return (
    <div className="flex gap-3">
      <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
        <svg className="size-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
        </svg>
      </div>
      <div className="flex-1 min-w-0 space-y-2">
        <div className="bg-neutral-50 rounded-2xl rounded-tl-none px-4 py-3 text-sm text-text leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
        {message.selected_skills && message.selected_skills.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {message.selected_skills.map((skill) => (
              <span key={skill} className="px-1.5 py-0.5 rounded text-[11px] font-medium bg-neutral-100 text-text-tertiary">
                {skill}
              </span>
            ))}
          </div>
        )}
        {message.evidence && message.evidence.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.evidence.map((ev, i) => (
              <EvidencePill key={i} evidence={ev} />
            ))}
          </div>
        )}
        {message.isError && (
          <p className="text-xs text-danger">Failed to get response. Try again.</p>
        )}
      </div>
    </div>
  )
}

function UserMessage({ message }: { message: ChatMessage }) {
  return (
    <div className="flex justify-end">
      <div className="bg-primary text-white rounded-2xl rounded-tr-none px-4 py-3 text-sm leading-relaxed max-w-[75%] whitespace-pre-wrap">
        {message.content}
      </div>
    </div>
  )
}

function generateId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function AgentChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || isLoading) return

    setInput('')
    const userMessage: ChatMessage = { id: generateId(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const history = messages
        .filter((m) => !m.isError)
        .slice(-20)
        .map((m) => ({ role: m.role, content: m.content }))

      const response = await sendChatMessage({ message: text, history })
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.answer,
        evidence: response.evidence,
        tool_calls: response.tool_calls,
        selected_skills: response.selected_skills,
        needs_confirmation: response.needs_confirmation,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch {
      const errorMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        isError: true,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }, [input, isLoading, messages])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleReset = () => {
    setMessages([])
    setInput('')
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="size-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                <svg className="size-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-text mb-1">CRM Assistant</h3>
              <p className="text-sm text-text-tertiary leading-relaxed">
                Ask me about your contacts, leads, proposals, or pipeline. I can help you find information, track progress, and manage your sales workflow.
              </p>
            </div>
          </div>
        )}
        {messages.map((msg) =>
          msg.role === 'user' ? (
            <UserMessage key={msg.id} message={msg} />
          ) : (
            <AssistantMessage key={msg.id} message={msg} />
          ),
        )}
        {isLoading && (
          <div className="flex gap-3">
            <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Spinner size="sm" />
            </div>
            <div className="bg-neutral-50 rounded-2xl rounded-tl-none px-4 py-3">
              <div className="flex gap-1">
                <span className="size-1.5 rounded-full bg-text-tertiary animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="size-1.5 rounded-full bg-text-tertiary animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="size-1.5 rounded-full bg-text-tertiary animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border bg-white px-6 py-4">
        <div className="flex items-end gap-3 max-w-4xl mx-auto">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your CRM data..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-border px-4 py-3 text-sm text-text placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary/30 min-h-[44px] max-h-32"
          />
          <Button onClick={handleSend} disabled={!input.trim() || isLoading} icon={
            <svg className="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          }>
            Send
          </Button>
        </div>
        {messages.length > 0 && (
          <div className="flex justify-center mt-3">
            <button
              onClick={handleReset}
              className="text-xs text-text-tertiary hover:text-text-secondary transition-colors"
            >
              Clear conversation
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
