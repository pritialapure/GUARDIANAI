const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    let message = `Request to ${path} failed with status ${response.status}`
    try {
      const body = await response.json()
      message = body.message || message
    } catch {
      // response wasn't JSON — keep the default message
    }
    throw new Error(message)
  }

  return response.json()
}

export function sendChatMessage({ message, threadId, location, country }) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, thread_id: threadId, location, country }),
  })
}

export function fetchHealth() {
  return request('/health')
}

export function fetchAgentsStatus() {
  return request('/agents')
}

export function fetchDocumentsStatus() {
  return request('/documents')
}

export function triggerIngest(force = false) {
  return request('/ingest', {
    method: 'POST',
    body: JSON.stringify({ force }),
  })
}

export function fetchReport(threadId) {
  return request('/report', {
    method: 'POST',
    body: JSON.stringify({ thread_id: threadId }),
  })
}
