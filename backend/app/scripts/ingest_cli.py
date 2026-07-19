"""
CLI entrypoint for ingesting the knowledge base without starting the API.

Usage:
    cd backend
    python -m app.scripts.ingest_cli
    python -m app.scripts.ingest_cli --force
"""

import argparse

from app.rag.ingestion import ingest_knowledge_base
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs into the Guardian Council AI knowledge base.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest files even if already present in the vector store.",
    )
    args = parser.parse_args()

    summary = ingest_knowledge_base(force=args.force)

    print("\n=== Ingestion Summary ===")
    print(f"Newly ingested : {summary.newly_ingested_files}")
    print(f"Skipped        : {summary.skipped_already_indexed}")
    print(f"Failed         : {summary.failed_files}")
    print(f"Chunks added   : {summary.total_chunks_added}")


if __name__ == "__main__":
    main()
