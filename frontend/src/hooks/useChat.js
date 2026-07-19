import { useCallback, useRef, useState } from 'react'
import { sendChatMessage } from '../services/api'
import { AGENT_PIPELINE } from '../constants/dashboard'

function generateThreadId() {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function typewriterReveal(fullText, onUpdate, onDone) {
  const characters = Array.from(fullText)
  let index = 0
  const chunkSize = 3
  const intervalId = setInterval(() => {
    index += chunkSize
    onUpdate(characters.slice(0, index).join(''))
    if (index >= characters.length) {
      clearInterval(intervalId)
      onDone()
    }
  }, 12)
  return () => clearInterval(intervalId)
}

export function useChat() {
  const [threadId] = useState(generateThreadId)
  const [messages, setMessages] = useState([])
  const [isSending, setIsSending] = useState(false)
  const [activePipelineStep, setActivePipelineStep] = useState(null)
  const [lastResult, setLastResult] = useState(null)
  const [error, setError] = useState(null)
  const cleanupTypewriter = useRef(null)

  const sendMessage = useCallback(
    async (text, { location, country } = {}) => {
      const trimmed = text.trim()
      if (!trimmed || isSending) return

      setError(null)
      setMessages((prev) => [...prev, { role: 'user', content: trimmed, id: `u-${Date.now()}` }])
      setIsSending(true)

      // Animate the pipeline optimistically while we wait for the real response —
      // the backend responds with the final state, not incremental progress, so
      // this gives the responder immediate visual feedback that work is happening.
      let stepIndex = 0
      setActivePipelineStep(AGENT_PIPELINE[0].key)
      const pipelineInterval = setInterval(() => {
        stepIndex = Math.min(stepIndex + 1, AGENT_PIPELINE.length - 1)
        setActivePipelineStep(AGENT_PIPELINE[stepIndex].key)
      }, 550)

      try {
        const result = await sendChatMessage({ message: trimmed, threadId, location, country })
        clearInterval(pipelineInterval)
        setActivePipelineStep(result.requires_emergency_workflow ? 'report' : null)
        setLastResult(result)

        const assistantMessageId = `a-${Date.now()}`
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: '', id: assistantMessageId, isTyping: true, result },
        ])

        cleanupTypewriter.current = typewriterReveal(
          result.response || '',
          (partial) => {
            setMessages((prev) =>
              prev.map((m) => (m.id === assistantMessageId ? { ...m, content: partial } : m))
            )
          },
          () => {
            setMessages((prev) =>
              prev.map((m) => (m.id === assistantMessageId ? { ...m, isTyping: false } : m))
            )
            setIsSending(false)
          }
        )
      } catch (err) {
        clearInterval(pipelineInterval)
        setActivePipelineStep(null)
        setError(err.message || 'Something went wrong contacting Guardian Council AI.')
        setIsSending(false)
      }
    },
    [threadId, isSending]
  )

  return { threadId, messages, isSending, activePipelineStep, lastResult, error, sendMessage }
}
