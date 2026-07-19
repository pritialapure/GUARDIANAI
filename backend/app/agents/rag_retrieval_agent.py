"""
RAG Retrieval Agent.

Thin agent-layer wrapper around `app.rag.retriever`. Combines the user's
original query with the classified emergency type to bias retrieval
toward the most relevant reference material before handing off to the
Planning Agent.
"""

from app.models.state import GuardianState
from app.rag.retriever import retrieve_context
from app.utils.exceptions import AgentExecutionError, RetrievalError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "rag_retrieval_agent"


def run_rag_retrieval_agent(state: GuardianState) -> GuardianState:
    """
    Retrieve trusted context relevant to the classified emergency.

    Reads: state["user_query"], state["emergency_type"]
    Writes: state["retrieved_context"], state["source_references"],
            state["retrieval_had_results"]
    """
    query = state.get("user_query", "").strip()
    emergency_type = state.get("emergency_type", "")

    # Bias the retrieval query with the emergency category for sharper recall.
    search_query = f"{emergency_type} emergency: {query}" if emergency_type else query

    logger.info("Retrieving context for: '%s'", search_query)

    try:
        result = retrieve_context(search_query)
    except RetrievalError as exc:
        raise AgentExecutionError(exc.message, agent_name=AGENT_NAME) from exc

    if result.is_empty:
        logger.warning("No knowledge base results found for '%s'", search_query)

    return {
        **state,
        "retrieved_context": result.formatted_context,
        "source_references": result.source_references,
        "retrieval_had_results": not result.is_empty,
    }
