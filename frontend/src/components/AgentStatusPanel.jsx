import { useEffect, useState } from 'react'
import { Radio } from 'lucide-react'
import AgentPipeline from './AgentPipeline'
import { fetchAgentsStatus } from '../services/api'

export default function AgentStatusPanel({ activeStep, isSending, lastResult }) {
  const [mcpTools, setMcpTools] = useState([])
  const [loadError, setLoadError] = useState(false)

  useEffect(() => {
    fetchAgentsStatus()
      .then((data) => setMcpTools(data.mcp_tools || []))
      .catch(() => setLoadError(true))
  }, [])

  const usedToolNames = new Set((lastResult?.mcp_tool_results || []).map((r) => r.tool_name))

  return (
    <div className="flex flex-col gap-6 p-4">
      <div>
        <h2 className="mb-4 font-display text-sm font-semibold uppercase tracking-wide text-text-primary">
          Agent Pipeline
        </h2>
        <AgentPipeline activeStep={activeStep} isSending={isSending} />
      </div>

      <div className="border-t border-border pt-4">
        <h2 className="mb-3 font-display text-sm font-semibold uppercase tracking-wide text-text-primary">
          MCP Tools
        </h2>
        {loadError ? (
          <p className="text-xs text-text-secondary">Could not reach the backend.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {mcpTools.map((tool) => {
              const wasUsed = usedToolNames.has(tool.name)
              return (
                <li key={tool.name} className="flex items-center gap-2 text-xs">
                  <Radio
                    size={12}
                    className={wasUsed ? 'text-status-safe' : 'text-status-idle'}
                  />
                  <span className={wasUsed ? 'text-text-primary' : 'text-text-secondary'}>
                    {tool.name.replace(/_/g, ' ')}
                  </span>
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}
