"""
Emergency Classification Agent.

Classifies the user's described situation into one of the fixed emergency
categories (Fire, Flood, Earthquake, Medical, Chemical Leak, Electrical,
Explosion, Road Accident, Violence, Other), with a confidence score used
downstream by the Coordinator's decision node and the Report Generator.
"""

from app.agents.llm_client import get_chat_model, invoke_structured
from app.models.state import GuardianState
from app.prompts.agent_prompts import CLASSIFICATION_SYSTEM_PROMPT
from app.schemas.agent_schemas import ClassificationResult
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "classification_agent"


def run_classification_agent(state: GuardianState) -> GuardianState:
    """
    Classify the emergency type described in the user's query.

    Reads: state["user_query"]
    Writes: state["emergency_type"], state["classification_confidence"],
            state["classification_reasoning"]
    """
    query = state.get("user_query", "").strip()
    if not query:
        raise AgentExecutionError("Received an empty user query.", agent_name=AGENT_NAME)

    logger.info("Classifying emergency for query: '%s'", query)

    try:
        model = get_chat_model(temperature=0.0)
        messages = [
            {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        result: ClassificationResult = invoke_structured(model, ClassificationResult, messages)
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name=AGENT_NAME) from exc

    logger.info(
        "Classified as '%s' (confidence=%.2f)",
        result.emergency_type.value,
        result.confidence,
    )

    return {
        **state,
        "emergency_type": result.emergency_type.value,
        "classification_confidence": result.confidence,
        "classification_reasoning": result.reasoning,
    }
