"""
Report Generator Agent.

Final agent node before the graph ends. Combines classification, the
action plan, and the validation outcome into a single structured
IncidentReport, including a plain-language `responder_message` that
becomes the assistant's final reply to the user.
"""

import json

from app.agents.llm_client import get_chat_model, invoke_structured
from app.models.state import GuardianState
from app.prompts.agent_prompts import REPORT_SYSTEM_PROMPT
from app.schemas.agent_schemas import IncidentReport
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "report_generator_agent"


def run_report_generator_agent(state: GuardianState) -> GuardianState:
    """
    Generate the final incident report and responder-facing message.

    Reads: state["emergency_type"], state["classification_confidence"],
           state["action_plan"], state["validation_passed"],
           state["unsupported_claims"], state["validation_notes"],
           state["source_references"]
    Writes: state["final_report"], state["final_response"]
    """
    logger.info("Generating final incident report")

    try:
        model = get_chat_model(temperature=0.2)
        system_prompt = REPORT_SYSTEM_PROMPT.format(
            classification=json.dumps(
                {
                    "emergency_type": state.get("emergency_type", "Other"),
                    "confidence": state.get("classification_confidence", 0.0),
                }
            ),
            plan=json.dumps(state.get("action_plan", {}), indent=2),
            validation=json.dumps(
                {
                    "passed": state.get("validation_passed", False),
                    "unsupported_claims": state.get("unsupported_claims", []),
                    "notes": state.get("validation_notes", []),
                }
            ),
            sources=json.dumps(state.get("source_references", [])),
            tool_results=json.dumps(state.get("mcp_tool_results", [])),
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the final incident report now."},
        ]
        report: IncidentReport = invoke_structured(model, IncidentReport, messages)
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name=AGENT_NAME) from exc

    logger.info(
        "Report generated: severity=%s grounding_status=%s",
        report.severity,
        report.grounding_status,
    )

    return {
        **state,
        "final_report": report.model_dump(),
        "final_response": report.responder_message,
    }
