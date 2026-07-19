"""
LangGraph orchestration for Guardian Council AI.

Wires every agent built in Phase 3 (+ the Report Generator and Simple
Response agents added in Phase 4) into a single StateGraph:

    START
      -> coordinator
           -> [not an emergency] -> simple_response -> memory -> END
           -> [is an emergency]  -> classification -> rag_retrieval -> tool_agent
                                     -> planning -> validation
                                          -> [failed, retries left] -> planning (loop)
                                          -> [passed or out of retries] -> report
                                     -> memory -> END

The compiled graph is checkpointed by thread_id (app.memory.conversation_memory),
so calling `invoke_workflow(query, thread_id)` repeatedly with the same
thread_id continues the same conversation.
"""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.classification_agent import run_classification_agent
from app.agents.coordinator_agent import run_coordinator_agent
from app.agents.memory_agent import run_memory_agent
from app.agents.planning_agent import run_planning_agent
from app.agents.rag_retrieval_agent import run_rag_retrieval_agent
from app.agents.report_generator_agent import run_report_generator_agent
from app.agents.simple_response_agent import run_simple_response_agent
from app.agents.tool_agent import run_tool_agent
from app.agents.validation_agent import run_validation_agent
from app.memory.conversation_memory import build_thread_config, get_checkpointer
from app.models.state import GuardianState
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_PLANNING_RETRIES = 1


def _route_after_coordinator(state: GuardianState) -> Literal["classification", "simple_response"]:
    """Branch into the full emergency pipeline or a direct reply."""
    if state.get("requires_emergency_workflow", False):
        return "classification"
    return "simple_response"


def _route_after_validation(state: GuardianState) -> Literal["planning", "report"]:
    """Retry planning once if validation failed, otherwise proceed to the report."""
    if state.get("validation_passed", False):
        return "report"

    retry_count = state.get("planning_retry_count", 0)
    if retry_count < MAX_PLANNING_RETRIES:
        logger.warning("Validation failed — retrying planning (attempt %d)", retry_count + 1)
        return "planning"

    logger.warning("Validation failed after max retries — proceeding to report with caveats.")
    return "report"


def _increment_retry_count(state: GuardianState) -> GuardianState:
    """Bump the retry counter before looping back into planning."""
    return {**state, "planning_retry_count": state.get("planning_retry_count", 0) + 1}


def build_workflow():
    """Construct and compile the Guardian Council AI LangGraph StateGraph."""
    graph = StateGraph(GuardianState)

    graph.add_node("coordinator", run_coordinator_agent)
    graph.add_node("simple_response", run_simple_response_agent)
    graph.add_node("classification", run_classification_agent)
    graph.add_node("rag_retrieval", run_rag_retrieval_agent)
    graph.add_node("tool_agent", run_tool_agent)
    graph.add_node("planning", run_planning_agent)
    graph.add_node("retry_counter", _increment_retry_count)
    graph.add_node("validation", run_validation_agent)
    graph.add_node("report", run_report_generator_agent)
    graph.add_node("memory", run_memory_agent)

    graph.add_edge(START, "coordinator")
    graph.add_conditional_edges(
        "coordinator",
        _route_after_coordinator,
        {"classification": "classification", "simple_response": "simple_response"},
    )
    graph.add_edge("simple_response", "memory")

    graph.add_edge("classification", "rag_retrieval")
    graph.add_edge("rag_retrieval", "tool_agent")
    graph.add_edge("tool_agent", "planning")
    graph.add_edge("planning", "validation")
    graph.add_conditional_edges(
        "validation",
        _route_after_validation,
        {"planning": "retry_counter", "report": "report"},
    )
    graph.add_edge("retry_counter", "planning")
    graph.add_edge("report", "memory")

    graph.add_edge("memory", END)

    return graph.compile(checkpointer=get_checkpointer())


# Compiled once per process; reused across requests.
_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
        logger.info("Guardian Council AI LangGraph workflow compiled.")
    return _workflow


def invoke_workflow(user_query: str, thread_id: str, location: str = "", country: str = "") -> GuardianState:
    """
    Run one full conversation turn through the workflow.

    The checkpointer automatically restores prior state (including
    chat_history) for the given thread_id, so multi-turn conversations
    work without the caller managing history manually.
    """
    workflow = get_workflow()
    config = build_thread_config(thread_id)

    initial_state: GuardianState = {"user_query": user_query, "thread_id": thread_id}
    if location:
        initial_state["location"] = location
    if country:
        initial_state["country"] = country

    result = workflow.invoke(initial_state, config=config)

    logger.info("Workflow completed for thread_id='%s'", thread_id)
    return result
