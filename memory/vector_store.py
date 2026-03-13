"""
Friday Vector Store
====================
LangChain Chroma wrapper around the existing local ChromaDB.

WHY THIS FILE EXISTS:
  The original memory/store.py uses the raw chromadb client directly.
  LangChain's retrieval tools expect a LangChain-compatible vector store object,
  not a raw chromadb collection. This file bridges the two.

  Both files can coexist:
  - memory/store.py    → used by ingest scripts (populate.py, ingest_*.py)
  - memory/vector_store.py → used by LangChain agent tools (tools/retrieval.py)
  Both point to the same local database (memory/db/chroma/).
  No data duplication.

EMBEDDINGS — IMPORTANT:
  We use all-MiniLM-L6-v2 (same as store.py / ingest scripts).
  This matters: if you change the embedding model, ALL existing vectors become
  incompatible and you'd need to re-embed everything.
  Do NOT switch to Google's embedding API or any other model without re-ingesting.

LAZY LOADING:
  Both the embedding model and collection stores are loaded only when first accessed
  and then cached globally. This avoids reloading the 80MB model on every request.
  First request: slow (loads model + connects to ChromaDB).
  Subsequent requests: fast (uses cached objects).

COLLECTIONS AVAILABLE:
  "knowledge"        — 42 chunks: deep analytical knowledge (JTBD, PMF, Sensemaking)
  "frameworks"       — 15 chunks: standalone reusable tools and methodologies
  "personal_knowledge" — 5 chunks: Sudheer's background (currently has placeholders)
  "episodes"         — empty (Phase 4: check-ins and events)
  "insights"         — empty (Phase 4: derived behavioral patterns)
  "case_memory"      — empty (Phase 4: MBA case history)

ADDING NEW COLLECTIONS:
  Just call get_store("your_collection_name") — it creates it if it doesn't exist.
  No schema registration needed. ChromaDB handles it.

CHANGELOG:
- 2026-03-12 | created: LangChain Chroma wrapper replacing raw chromadb calls
"""

from pathlib import Path
from typing import Dict, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Points to the same local SQLite + vector index used by all ingest scripts
DB_PATH = str(Path(__file__).parent / "db" / "chroma")

# Module-level singletons — loaded once, reused across all requests
_embeddings: Optional[HuggingFaceEmbeddings] = None
_stores: Dict[str, Chroma] = {}


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns the embedding model, loading it on first call.
    all-MiniLM-L6-v2: 80MB local model, 384-dim vectors, fast inference.
    Must match the model used when data was originally ingested (store.py).
    """
    global _embeddings
    if _embeddings is None:
        print("Loading embedding model...")
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings


def get_store(collection_name: str) -> Chroma:
    """
    Returns a LangChain Chroma store for the given collection.
    Creates and caches it on first call, returns cached version after.

    The returned object supports:
      .similarity_search(query, k=n)               → [Document, ...]
      .similarity_search_with_score(query, k=n)    → [(Document, float), ...]
      .as_retriever(search_kwargs={"k": n})         → LangChain Retriever

    Used by: tools/retrieval.py (agent tools)
    """
    global _stores
    if collection_name not in _stores:
        _stores[collection_name] = Chroma(
            collection_name=collection_name,
            embedding_function=get_embeddings(),
            persist_directory=DB_PATH,  # connects to existing local database
        )
    return _stores[collection_name]
