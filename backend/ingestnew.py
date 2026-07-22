from app.rag.ingestion import ingest_knowledge_base

summary = ingest_knowledge_base(force=True)

print(summary)