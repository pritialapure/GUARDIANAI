"""
Validation Agent.

Guardrails the Planning Agent's output: checks every recommendation in
the generated action plan against the retrieved context and flags any
claim that isn't actually supported. This is what makes Guardian Council
AI "grounded" rather than just "RAG-flavored" — a plan can be rejected
downstream (Report Generator / API layer) if validation fails.
"""

import json

from app.agents.llm_client import get_chat_model, invoke_structured
from app.models.state import GuardianState
from app.prompts.agent_prompts import VALIDATION_SYSTEM_PROMPT
from app.schemas.agent_schemas import ValidationResult
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "validation_agent"


def run_validation_agent(state: GuardianState) -> GuardianState:
    """
    Validate the generated action plan against the retrieved context.

    Reads: state["retrieved_context"], state["action_plan"]
    Writes: state["validation_passed"], state["validation_notes"],
            state["unsupported_claims"]
    """
    context = state.get("retrieved_context", "")
    plan = state.get("action_plan", {})

    if not plan:
        raise AgentExecutionError("No action plan present to validate.", agent_name=AGENT_NAME)

    logger.info("Validating action plan against retrieved context")

    try:
        model = get_chat_model(temperature=0.0)
        system_prompt = VALIDATION_SYSTEM_PROMPT.format(
            context=context or "No context was retrieved.",
            plan=json.dumps(plan, indent=2),
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Validate this plan now."},
        ]
        result: ValidationResult = invoke_structured(model, ValidationResult, messages)
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name=AGENT_NAME) from exc

    if not result.passed:
        logger.warning(
            "Validation FAILED: %d unsupported claim(s): %s",
            len(result.unsupported_claims),
            result.unsupported_claims,
        )
    else:
        logger.info("Validation passed — all recommendations are grounded.")

    return {
        **state,
        "validation_passed": result.passed,
        "validation_notes": result.notes,
        "unsupported_claims": result.unsupported_claims,
    }
