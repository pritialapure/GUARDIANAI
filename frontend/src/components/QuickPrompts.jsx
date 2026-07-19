import { EMERGENCY_QUICK_PROMPTS } from '../constants/dashboard'

export default function QuickPrompts({ onSelect, disabled }) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {EMERGENCY_QUICK_PROMPTS.map((prompt) => (
        <button
          key={prompt.label}
          disabled={disabled}
          onClick={() => onSelect(prompt.text)}
          className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs text-text-secondary transition-colors hover:border-accent hover:text-accent disabled:opacity-50"
        >
          {prompt.label}
        </button>
      ))}
    </div>
  )
}
