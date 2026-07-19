"""
Planning Agent.

Generates a structured emergency response plan grounded strictly in the
context retrieved by the RAG Retrieval Agent. Output feeds directly into
the Validation Agent, which checks every recommendation against the same
context.
"""

from app.agents.llm_client import get_chat_model, invoke_structured
from app.models.state import GuardianState
from app.prompts.agent_prompts import PLANNING_SYSTEM_PROMPT
from app.schemas.agent_schemas import ActionPlan
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "planning_agent"


def run_planning_agent(state: GuardianState) -> GuardianState:
    """
    Generate a structured action plan for the classified emergency.

    Reads: state["user_query"], state["emergency_type"], state["retrieved_context"]
    Writes: state["action_plan"]
    """
    query = state.get("user_query", "").strip()
    emergency_type = state.get("emergency_type", "Other")
    context = state.get("retrieved_context", "")
    tool_results = state.get("mcp_tool_results", [])

    if not context:
        logger.warning("Planning agent running with no retrieved context — plan will be minimally grounded.")

    logger.info("Generating action plan for emergency_type='%s'", emergency_type)

    try:
        model = get_chat_model(temperature=0.3)
        system_prompt = PLANNING_SYSTEM_PROMPT.format(
            context=context or "No context was retrieved from the knowledge base."
        )
        user_content = f"Emergency type: {emergency_type}\nSituation described by user: {query}"
        if tool_results:
            user_content += f"\n\nLive resource lookups available (hospitals, stations, contacts, weather):\n{tool_results}"
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_content,
            },
        ]
        plan: ActionPlan = invoke_structured(model, ActionPlan, messages)
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name=AGENT_NAME) from exc

    logger.info(
        "Generated plan with %d immediate and %d follow-up actions",
        len(plan.immediate_actions),
        len(plan.follow_up_actions),
    )

    return {**state, "action_plan": plan.model_dump()}
