import { useEffect, useRef, useState } from 'react'
import { Send, ShieldHalf, AlertCircle } from 'lucide-react'
import MessageBubble from './MessageBubble'
import QuickPrompts from './QuickPrompts'

export default function ChatWindow({ messages, isSending, error, onSend }) {
  const [input, setInput] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isSending) return
    onSend(input)
    setInput('')
  }

  return (
    <div className="flex h-full flex-1 flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-5 text-center">
            <ShieldHalf className="text-accent" size={40} />
            <div>
              <h2 className="font-display text-lg font-semibold text-text-primary">
                Guardian Council AI
              </h2>
              <p className="mt-1 max-w-sm text-sm text-text-secondary">
                Describe an emergency, or start with one of these common scenarios.
              </p>
            </div>
            <QuickPrompts onSelect={onSend} disabled={isSending} />
          </div>
        ) : (
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={scrollRef} />
          </div>
        )}
      </div>

      {error && (
        <div className="mx-6 mb-2 flex items-center gap-2 rounded-lg border border-status-critical/40 bg-status-critical/10 px-3 py-2 text-xs text-status-critical">
          <AlertCircle size={14} />
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-t border-border p-4">
        <div className="mx-auto flex max-w-3xl items-center gap-2 rounded-xl border border-border bg-surface px-3 py-2 focus-within:border-accent">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isSending}
            placeholder="Describe the emergency situation…"
            className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-secondary focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent text-white transition-opacity disabled:opacity-40"
            aria-label="Send message"
          >
            <Send size={15} />
          </button>
        </div>
      </form>
    </div>
  )
}
