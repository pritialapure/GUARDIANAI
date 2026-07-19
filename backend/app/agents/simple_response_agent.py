"""
Simple Response Agent.

Used when the Coordinator Agent determines the user's message does not
describe an emergency. Skips classification/RAG/planning/validation
entirely and replies directly, keeping conversation history in mind.
"""

from app.agents.llm_client import get_chat_model
from app.agents.memory_agent import format_history_for_prompt
from app.models.state import GuardianState
from app.prompts.agent_prompts import SIMPLE_RESPONSE_SYSTEM_PROMPT
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "simple_response_agent"


def run_simple_response_agent(state: GuardianState) -> GuardianState:
    """
    Generate a direct conversational reply for non-emergency messages.

    Reads: state["user_query"], state["chat_history"]
    Writes: state["final_response"]
    """
    query = state.get("user_query", "")
    history = state.get("chat_history", [])

    logger.info("Generating simple response for non-emergency query")

    try:
        model = get_chat_model(temperature=0.5)
        system_prompt = SIMPLE_RESPONSE_SYSTEM_PROMPT.format(history=format_history_for_prompt(history))
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = model.invoke(messages)
        answer_text = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name=AGENT_NAME) from exc

    return {**state, "final_response": answer_text}
