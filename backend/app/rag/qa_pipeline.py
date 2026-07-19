"""
Grounded question-answering pipeline for the knowledge base.

This is the RAG-only building block (retrieve -> prompt -> generate ->
cite sources). The Planning and Validation agents in Phase 3 call into
`app.rag.retriever` directly for finer-grained control; this module
exists for simple, direct "ask the knowledge base" use cases and for
the /chat route's RAG step in the LangGraph workflow.
"""

from dataclasses import dataclass
from typing import List

from langchain.chat_models import init_chat_model

from app.config.settings import settings
from app.prompts.rag_prompt import build_rag_system_prompt
from app.rag.retriever import RetrievalResult, retrieve_context
from app.utils.exceptions import ConfigurationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GroundedAnswer:
    """A grounded, cited answer produced from the knowledge base."""

    answer: str
    source_references: List[dict]
    context_used: str
    has_sufficient_context: bool


def _get_chat_model():
    if not settings.GOOGLE_API_KEY:
        raise ConfigurationError("GOOGLE_API_KEY is not set. Required to query Gemini.")
    return init_chat_model(
        f"google_genai:{settings.GEMINI_CHAT_MODEL}",
        api_key=settings.GOOGLE_API_KEY,
    )


def ask_knowledge_base(query: str, k: int | None = None) -> GroundedAnswer:
    """
    Answer a query using only retrieved knowledge-base context.

    Returns a GroundedAnswer with the generated text, deduplicated source
    references (file + page), and a flag indicating whether retrieval
    found any relevant context at all.
    """
    retrieval: RetrievalResult = retrieve_context(query, k=k)

    if retrieval.is_empty:
        logger.warning("No context retrieved for query '%s' — returning fallback answer.", query)
        return GroundedAnswer(
            answer=(
                "I could not find relevant information in the knowledge base to answer "
                "this confidently. Please consult a qualified emergency responder or add "
                "relevant reference documents to the knowledge base."
            ),
            source_references=[],
            context_used="",
            has_sufficient_context=False,
        )

    model = _get_chat_model()
    system_message = build_rag_system_prompt(retrieval.formatted_context)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query},
    ]

    response = model.invoke(messages)
    answer_text = response.content if isinstance(response.content, str) else str(response.content)

    return GroundedAnswer(
        answer=answer_text,
        source_references=retrieval.source_references,
        context_used=retrieval.formatted_context,
        has_sufficient_context=True,
    )
