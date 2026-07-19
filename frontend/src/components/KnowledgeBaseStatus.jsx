import { useCallback, useEffect, useState } from 'react'
import { FileText, RefreshCw, Database } from 'lucide-react'
import { fetchDocumentsStatus, triggerIngest } from '../services/api'

export default function KnowledgeBaseStatus() {
  const [status, setStatus] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isIngesting, setIsIngesting] = useState(false)
  const [loadError, setLoadError] = useState(false)

  const refresh = useCallback(() => {
    setIsLoading(true)
    setLoadError(false)
    fetchDocumentsStatus()
      .then(setStatus)
      .catch(() => setLoadError(true))
      .finally(() => setIsLoading(false))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const handleIngest = async () => {
    setIsIngesting(true)
    try {
      await triggerIngest(false)
      refresh()
    } catch {
      setLoadError(true)
    } finally {
      setIsIngesting(false)
    }
  }

  return (
    <div className="border-t border-border p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-text-primary">
          Knowledge Base
        </h2>
        <button
          onClick={handleIngest}
          disabled={isIngesting}
          className="flex items-center gap-1 rounded-md border border-border px-2 py-1 text-[10px] uppercase tracking-wide text-text-secondary transition-colors hover:border-accent hover:text-accent disabled:opacity-50"
        >
          <RefreshCw size={11} className={isIngesting ? 'animate-spin' : ''} />
          {isIngesting ? 'Ingesting' : 'Ingest'}
        </button>
      </div>

      {isLoading && <p className="text-xs text-text-secondary">Loading…</p>}
      {loadError && !isLoading && (
        <p className="text-xs text-text-secondary">Could not reach the backend.</p>
      )}

      {status && !isLoading && (
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <Database size={12} />
            <span>{status.total_chunks} indexed chunks</span>
          </div>

          <div>
            <p className="mb-1.5 text-[10px] uppercase tracking-wide text-text-secondary">
              Indexed ({status.indexed_files.length})
            </p>
            {status.indexed_files.length === 0 ? (
              <p className="text-xs text-text-secondary">No documents indexed yet.</p>
            ) : (
              <ul className="flex flex-col gap-1.5">
                {status.indexed_files.map((file) => (
                  <li key={file} className="flex items-center gap-2 text-xs text-text-primary">
                    <FileText size={12} className="shrink-0 text-status-safe" />
                    <span className="truncate">{file}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {status.pending_files.length > 0 && (
            <div>
              <p className="mb-1.5 text-[10px] uppercase tracking-wide text-text-secondary">
                Pending ingestion ({status.pending_files.length})
              </p>
              <ul className="flex flex-col gap-1.5">
                {status.pending_files.map((file) => (
                  <li key={file} className="flex items-center gap-2 text-xs text-status-warning">
                    <FileText size={12} className="shrink-0" />
                    <span className="truncate">{file}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
