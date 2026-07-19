"""
Document loading for the Guardian Council AI knowledge base.

Scans `settings.KNOWLEDGE_BASE_DIR` for PDF files and loads them with
PyPDFLoader. Kept isolated from splitting/embedding so new loader types
(e.g. .docx, .txt) can be added later without touching the rest of the
RAG pipeline.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.config.settings import settings
from app.utils.exceptions import DocumentIngestionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def list_knowledge_base_pdfs() -> List[Path]:
    """Return every .pdf file currently sitting in the knowledge base directory."""
    kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)
    kb_dir.mkdir(parents=True, exist_ok=True)
    return sorted(kb_dir.glob("*.pdf"))


def load_pdf(file_path: Path) -> List[Document]:
    """
    Load a single PDF into a list of LangChain Documents (one per page).

    Raises:
        DocumentIngestionError: if the file cannot be parsed.
    """
    if not file_path.exists():
        raise DocumentIngestionError(f"File not found: {file_path}")

    try:
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
    except Exception as exc:  # noqa: BLE001 - surfaced as a typed error
        raise DocumentIngestionError(f"Failed to load PDF '{file_path.name}': {exc}") from exc

    if not pages:
        raise DocumentIngestionError(f"PDF '{file_path.name}' contains no extractable text.")

    # Normalize metadata so downstream citation/report generation is consistent.
    for page in pages:
        page.metadata["source_file"] = file_path.name

    logger.info("Loaded '%s' (%d pages)", file_path.name, len(pages))
    return pages


def load_all_knowledge_base_pdfs() -> List[Document]:
    """Load every PDF currently in the knowledge base directory into Documents."""
    pdf_paths = list_knowledge_base_pdfs()
    if not pdf_paths:
        logger.warning("No PDFs found in knowledge base directory: %s", settings.KNOWLEDGE_BASE_DIR)
        return []

    all_documents: List[Document] = []
    for pdf_path in pdf_paths:
        try:
            all_documents.extend(load_pdf(pdf_path))
        except DocumentIngestionError as exc:
            # One bad PDF should not abort ingestion of the rest of the knowledge base.
            logger.error("Skipping '%s': %s", pdf_path.name, exc.message)

    return all_documents
