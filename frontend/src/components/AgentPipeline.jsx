import { AGENT_PIPELINE } from '../constants/dashboard'
import { Check } from 'lucide-react'

/**
 * The signature visual of the dashboard: a vertical command-center style
 * status chain mirroring the actual LangGraph execution order. Not
 * decorative — it reflects the real agent that's currently reasoning.
 */
export default function AgentPipeline({ activeStep, isSending }) {
  const activeIndex = AGENT_PIPELINE.findIndex((step) => step.key === activeStep)

  return (
    <div className="flex flex-col gap-0">
      {AGENT_PIPELINE.map((step, index) => {
        const isComplete = isSending && activeIndex > index
        const isActive = isSending && activeIndex === index
        const isPending = !isSending || activeIndex < index

        return (
          <div key={step.key} className="flex items-start gap-3">
            <div className="flex flex-col items-center">
              <div
                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border font-mono text-[10px] ${
                  isComplete
                    ? 'border-status-safe bg-status-safe/20 text-status-safe'
                    : isActive
                      ? 'border-accent bg-accent/20 text-accent animate-pulse-ring'
                      : 'border-border bg-surface text-text-secondary'
                }`}
              >
                {isComplete ? <Check size={12} /> : index + 1}
              </div>
              {index < AGENT_PIPELINE.length - 1 && (
                <div
                  className={`h-6 w-px ${isComplete ? 'bg-status-safe' : 'bg-border'}`}
                  aria-hidden="true"
                />
              )}
            </div>
            <div className={`pb-6 pt-0.5 text-sm ${isPending ? 'text-text-secondary' : 'text-text-primary'}`}>
              {step.label}
              {isActive && (
                <span className="ml-2 font-mono text-[10px] uppercase tracking-wide text-accent">
                  running
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
