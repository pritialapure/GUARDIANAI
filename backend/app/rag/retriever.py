"""
Retrieval for the Guardian Council AI knowledge base.

Given a user query, performs semantic search against ChromaDB and
returns both the raw source documents (for citation / validation)
and a formatted context block ready to drop into a prompt template.
"""

from dataclasses import dataclass, field
from typing import List

from langchain_core.documents import Document

from app.config.settings import settings
from app.rag.vector_store import get_vector_store
from app.utils.exceptions import RetrievalError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """Structured output of a retrieval call, ready for prompting and citation."""

    query: str
    documents: List[Document] = field(default_factory=list)
    formatted_context: str = ""

    @property
    def source_references(self) -> List[dict]:
        """Deduplicated list of {source_file, page} references for the frontend/report."""
        seen = set()
        references = []
        for doc in self.documents:
            source = doc.metadata.get("source_file", "unknown")
            page = doc.metadata.get("page", "unknown")
            key = (source, page)
            if key not in seen:
                seen.add(key)
                references.append({"source_file": source, "page": page})
        return references

    @property
    def is_empty(self) -> bool:
        return len(self.documents) == 0


def _format_context(documents: List[Document]) -> str:
    """Render retrieved chunks into a labeled context block for the LLM prompt."""
    blocks = []
    for doc in documents:
        source = doc.metadata.get("source_file", "unknown")
        page = doc.metadata.get("page", "unknown")
        blocks.append(f"[Source: {source}, page {page}]\n{doc.page_content}")
    return "\n\n".join(blocks)


def retrieve_context(query: str, k: int | None = None) -> RetrievalResult:
    """
    Run semantic search against the knowledge base for the given query.

    Args:
        query: The user's question or emergency description.
        k: Number of chunks to retrieve. Defaults to settings.RETRIEVAL_TOP_K.

    Raises:
        RetrievalError: if the underlying vector store search fails.
    """
    top_k = k or settings.RETRIEVAL_TOP_K
    store = get_vector_store()

    try:
        documents = store.similarity_search(query, k=top_k)
    except Exception as exc:  # noqa: BLE001
        raise RetrievalError(f"Similarity search failed for query '{query}': {exc}") from exc

    if not documents:
        logger.warning("No relevant chunks found for query: '%s'", query)

    return RetrievalResult(
        query=query,
        documents=documents,
        formatted_context=_format_context(documents),
    )


def retrieve_context_with_scores(query: str, k: int | None = None) -> List[tuple[Document, float]]:
    """Same as retrieve_context but returns (document, similarity_score) pairs.

    Useful for the Validation Agent, which needs a confidence signal to decide
    whether a retrieved chunk is strong enough to ground a recommendation.
    """
    top_k = k or settings.RETRIEVAL_TOP_K
    store = get_vector_store()

    try:
        return store.similarity_search_with_relevance_scores(query, k=top_k)
    except Exception as exc:  # noqa: BLE001
        raise RetrievalError(f"Scored similarity search failed for query '{query}': {exc}") from exc
