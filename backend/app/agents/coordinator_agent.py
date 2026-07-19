"""
Coordinator Agent.

First node in the LangGraph workflow. Decides whether the user's message
warrants the full multi-agent emergency pipeline (classification -> RAG ->
planning -> validation -> report) or is a greeting/off-topic message that
should get a short direct reply instead.
"""

from app.agents.llm_client import get_chat_model, invoke_structured
from app.models.state import GuardianState
from app.prompts.agent_prompts import COORDINATOR_SYSTEM_PROMPT
from app.schemas.agent_schemas import CoordinatorDecision
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "coordinator_agent"


def run_coordinator_agent(state: GuardianState) -> GuardianState:
    """
    Decide whether the emergency workflow should run.

    Reads: state["user_query"]
    Writes: state["requires_emergency_workflow"], state["coordinator_reasoning"]
    """
    query = state.get("user_query", "").strip()
    if not query:
        raise AgentExecutionError("Received an empty user query.", agent_name=AGENT_NAME)

    logger.info("Coordinator evaluating query: '%s'", query)

    try:
        model = get_chat_model(temperature=0.0)
        messages = [
            {"role": "system", "content": COORDINATOR_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        decision: CoordinatorDecision = invoke_structured(model, CoordinatorDecision, messages)
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name=AGENT_NAME) from exc

    logger.info(
        "Coordinator decision: requires_emergency_workflow=%s (%s)",
        decision.requires_emergency_workflow,
        decision.reasoning,
    )

    return {
        **state,
        "requires_emergency_workflow": decision.requires_emergency_workflow,
        "coordinator_reasoning": decision.reasoning,
    }
