export const EMERGENCY_QUICK_PROMPTS = [
  { label: 'Fire', text: 'There is a fire with heavy smoke and I need immediate guidance.' },
  { label: 'Flood', text: 'Flood water is rising quickly near my location. What should I do?' },
  { label: 'Medical', text: 'Someone near me is unresponsive and needs urgent medical help.' },
  { label: 'Earthquake', text: 'A strong earthquake just hit and the building is shaking.' },
  { label: 'Gas Leak', text: 'I smell gas leaking inside my home. What are the immediate steps?' },
  { label: 'Road Accident', text: 'There has been a serious road accident with injuries.' },
]

// Order mirrors the LangGraph workflow so the pipeline visual reflects real execution order.
export const AGENT_PIPELINE = [
  { key: 'coordinator', label: 'Coordinator' },
  { key: 'classification', label: 'Classification' },
  { key: 'rag_retrieval', label: 'RAG Retrieval' },
  { key: 'tool_agent', label: 'Tool Agent' },
  { key: 'planning', label: 'Planning' },
  { key: 'validation', label: 'Validation' },
  { key: 'report', label: 'Report' },
]
