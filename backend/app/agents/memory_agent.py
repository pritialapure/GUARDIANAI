"""
Memory Agent.

While `app.memory.conversation_memory` provides the LangGraph checkpointer
that persists full graph state across turns, the Memory Agent is the node
responsible for maintaining the lightweight `chat_history` list inside
state — the rolling window of prior turns other agents (Planning,
Coordinator) read for conversational context.
"""

from typing import List

from app.models.state import GuardianState
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "memory_agent"

# Cap how many prior turns are kept in-state to bound prompt size.
MAX_HISTORY_TURNS = 10


def run_memory_agent(state: GuardianState) -> GuardianState:
    """
    Append the current turn to chat_history and trim to the most recent turns.

    Reads: state["user_query"], state["final_response"], state["chat_history"]
    Writes: state["chat_history"]

    Called twice per conversation turn in the graph: once (implicitly, via
    the checkpointer) before the workflow starts to load prior history, and
    once at the end to record the completed turn.
    """
    history: List[dict] = list(state.get("chat_history", []))
    query = state.get("user_query", "")
    response = state.get("final_response", "")

    if query and response:
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})

    if len(history) > MAX_HISTORY_TURNS * 2:
        history = history[-MAX_HISTORY_TURNS * 2 :]

    logger.debug("Memory agent: chat_history now has %d messages", len(history))

    return {**state, "chat_history": history}


def format_history_for_prompt(chat_history: List[dict]) -> str:
    """Render chat_history into a plain-text block for inclusion in agent prompts."""
    if not chat_history:
        return "No prior conversation."

    lines = [f"{turn['role'].capitalize()}: {turn['content']}" for turn in chat_history]
    return "\n".join(lines)
