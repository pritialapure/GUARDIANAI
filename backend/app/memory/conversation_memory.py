"""
Conversation memory backend.

Provides the LangGraph checkpointer (Phase 4 wires this into the
StateGraph's `.compile(checkpointer=...)` call) so multi-turn
conversations persist across agent invocations, keyed by thread_id.

Swappable via settings.MEMORY_BACKEND:
    - "in_memory": process-local, cleared on restart (good for a hackathon demo)
    - "sqlite": persisted to disk, survives restarts
"""

from functools import lru_cache
from typing import Any

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_checkpointer() -> Any:
    """Return the configured LangGraph checkpointer (cached, one instance per process)."""
    backend = settings.MEMORY_BACKEND.lower()

    if backend == "sqlite":
        import sqlite3

        from langgraph.checkpoint.sqlite import SqliteSaver

        logger.info("Using SQLite conversation memory at '%s'", settings.SQLITE_MEMORY_PATH)
        connection = sqlite3.connect(settings.SQLITE_MEMORY_PATH, check_same_thread=False)
        return SqliteSaver(connection)

    if backend == "in_memory":
        from langgraph.checkpoint.memory import InMemorySaver

        logger.info("Using in-memory conversation memory (cleared on restart)")
        return InMemorySaver()

    raise ValueError(f"Unknown MEMORY_BACKEND '{settings.MEMORY_BACKEND}'. Use 'in_memory' or 'sqlite'.")


def build_thread_config(thread_id: str) -> dict:
    """Build the LangGraph `config` dict expected by `.invoke(..., config=...)`."""
    return {"configurable": {"thread_id": thread_id}}
