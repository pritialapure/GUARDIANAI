import { useEffect, useState } from 'react'
import { ShieldHalf, Circle } from 'lucide-react'
import { fetchHealth } from '../services/api'

export default function Sidebar({ threadId }) {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    const check = () => fetchHealth().then(setHealth).catch(() => setHealth(null))
    check()
    const interval = setInterval(check, 15000)
    return () => clearInterval(interval)
  }, [])

  const isOnline = health?.status === 'ok'

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex items-center gap-2.5 border-b border-border px-5 py-5">
        <ShieldHalf className="text-accent" size={22} />
        <div>
          <h1 className="font-display text-sm font-semibold leading-tight text-text-primary">
            Guardian Council
          </h1>
          <p className="font-mono text-[10px] leading-tight text-text-secondary">EMERGENCY AI</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4">
        <p className="mb-2 text-[10px] uppercase tracking-wide text-text-secondary">Session</p>
        <p className="truncate font-mono text-xs text-text-primary">{threadId}</p>

        <p className="mb-2 mt-6 text-[10px] uppercase tracking-wide text-text-secondary">
          How this works
        </p>
        <p className="text-xs leading-relaxed text-text-secondary">
          Describe an emergency and Guardian Council AI classifies it, retrieves
          trusted guidance, drafts a grounded action plan, validates every
          recommendation, and returns a structured response.
        </p>
      </div>

      <div className="flex items-center gap-2 border-t border-border px-5 py-4">
        <Circle
          size={8}
          fill="currentColor"
          className={isOnline ? 'text-status-safe' : 'text-status-critical'}
        />
        <span className="text-xs text-text-secondary">
          {isOnline ? 'Backend online' : 'Backend unreachable'}
        </span>
      </div>
    </aside>
  )
}
