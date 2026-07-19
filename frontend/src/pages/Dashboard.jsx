import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import AgentStatusPanel from '../components/AgentStatusPanel'
import KnowledgeBaseStatus from '../components/KnowledgeBaseStatus'
import { useChat } from '../hooks/useChat'

export default function Dashboard() {
  const { threadId, messages, isSending, activePipelineStep, lastResult, error, sendMessage } = useChat()

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-text-primary">
      <Sidebar threadId={threadId} />

      <main className="flex flex-1 overflow-hidden">
        <ChatWindow messages={messages} isSending={isSending} error={error} onSend={sendMessage} />

        <aside className="hidden w-72 shrink-0 overflow-y-auto border-l border-border bg-surface lg:block">
          <AgentStatusPanel
            activeStep={activePipelineStep}
            isSending={isSending}
            lastResult={lastResult}
          />
          <KnowledgeBaseStatus />
        </aside>
      </main>
    </div>
  )
}
