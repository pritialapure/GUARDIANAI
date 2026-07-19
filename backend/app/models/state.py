"""
Shared conversation/workflow state passed between agent nodes.

Defined now (Phase 3) so every agent can be built and unit-tested against
a single contract. Phase 4 wires this exact TypedDict into the LangGraph
StateGraph — no changes needed here when that happens.
"""

from typing import Any, List, Optional, TypedDict


class SourceReference(TypedDict):
    source_file: str
    page: Any


class GuardianState(TypedDict, total=False):
    """The full state object threaded through the LangGraph workflow."""

    # --- Input ---
    thread_id: str
    user_query: str
    chat_history: List[dict]
    location: str
    country: str

    # --- Coordinator Agent output ---
    requires_emergency_workflow: bool
    coordinator_reasoning: str

    # --- Classification Agent output ---
    emergency_type: str
    classification_confidence: float
    classification_reasoning: str

    # --- RAG Retrieval Agent output ---
    retrieved_context: str
    source_references: List[SourceReference]
    retrieval_had_results: bool

    # --- Tool Agent output ---
    mcp_tool_results: List[dict]

    # --- Planning Agent output ---
    action_plan: dict

    # --- Validation Agent output ---
    validation_passed: bool
    validation_notes: List[str]
    unsupported_claims: List[str]
    planning_retry_count: int

    # --- Report Generator Agent output (Phase 4) ---
    final_report: dict

    # --- Final response returned to the user ---
    final_response: str
    error: Optional[str]
