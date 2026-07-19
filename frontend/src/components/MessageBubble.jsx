import { AlertTriangle, ShieldCheck, ShieldAlert } from 'lucide-react'

function TypingDots() {
  return (
    <span className="inline-flex gap-1 py-1">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-text-secondary animate-typing-dot"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </span>
  )
}

function ValidationBadge({ result }) {
  if (!result?.requires_emergency_workflow) return null

  const passed = result.validation_passed
  return (
    <div
      className={`mt-2 flex items-center gap-1.5 text-[10px] uppercase tracking-wide ${
        passed ? 'text-status-safe' : 'text-status-warning'
      }`}
    >
      {passed ? <ShieldCheck size={12} /> : <ShieldAlert size={12} />}
      <span>
        {passed
          ? 'Grounded in knowledge base'
          : `${result.unsupported_claims?.length || 0} unverified recommendation(s)`}
      </span>
    </div>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const emergencyType = message.result?.emergency_type

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-accent text-white rounded-br-sm'
            : 'bg-surface-elevated text-text-primary rounded-bl-sm border border-border'
        }`}
      >
        {!isUser && emergencyType && (
          <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wide text-accent-soft">
            <AlertTriangle size={11} />
            {emergencyType}
            {typeof message.result.classification_confidence === 'number' && (
              <span className="text-text-secondary">
                {Math.round(message.result.classification_confidence * 100)}% confidence
              </span>
            )}
          </div>
        )}

        {message.isTyping && message.content === '' ? (
          <TypingDots />
        ) : (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}

        {!message.isTyping && !isUser && <ValidationBadge result={message.result} />}
      </div>
    </div>
  )
}
