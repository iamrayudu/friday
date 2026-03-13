"""
Friday Memory Store
--------------------
Single interface for writing to and reading from ChromaDB.
All other parts of the app go through here.

CHANGELOG:
- 2026-03-11 | created: add, update, delete, search, get_all, count, list_collections
- 2026-03-11 | added upsert() — adds if doc_id is new, updates if it already exists.
               populate.py and all ingest scripts should use upsert(), not add(),
               so re-running a script safely updates metadata without duplicating chunks.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import datetime
import uuid

# --- Init ---
DB_PATH = Path(__file__).parent / "db" / "chroma"
DB_PATH.mkdir(parents=True, exist_ok=True)

_client = None
_embedder = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(DB_PATH))
    return _client

def get_embedder():
    global _embedder
    if _embedder is None:
        print("Loading embedding model (first time only)...")
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def get_collection(name: str):
    return get_client().get_or_create_collection(name)


# --- WRITE ---

def add(collection_name: str, text: str, metadata: dict, doc_id: str = None):
    """Add a single chunk to a collection."""
    collection = get_collection(collection_name)
    embedding = get_embedder().encode(text).tolist()
    doc_id = doc_id or str(uuid.uuid4())

    # Always stamp when it was added
    metadata["added_on"] = str(datetime.date.today())

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    print(f"✓ Stored in [{collection_name}] | id: {doc_id}")
    return doc_id


def upsert(collection_name: str, text: str, metadata: dict, doc_id: str = None):
    """Add if new, update if exists. Always use this in ingest/populate scripts."""
    collection = get_collection(collection_name)
    embedding = get_embedder().encode(text).tolist()
    doc_id = doc_id or str(uuid.uuid4())
    metadata["added_on"] = str(datetime.date.today())

    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    print(f"✓ Upserted in [{collection_name}] | id: {doc_id}")
    return doc_id


def update(collection_name: str, doc_id: str, text: str, metadata: dict):
    """Update an existing chunk (delete + re-add)."""
    collection = get_collection(collection_name)
    collection.delete(ids=[doc_id])
    add(collection_name, text, metadata, doc_id)


def delete(collection_name: str, doc_id: str):
    """Remove a chunk by ID."""
    get_collection(collection_name).delete(ids=[doc_id])
    print(f"✓ Deleted [{doc_id}] from [{collection_name}]")


# --- READ ---

def search(collection_name: str, query: str, n: int = 4, filters: dict = None) -> list[dict]:
    """
    Semantic search. Returns list of {text, metadata, id, score} dicts.
    filters: ChromaDB where clause e.g. {"type": "framework"}
    """
    collection = get_collection(collection_name)
    embedding = get_embedder().encode(query).tolist()

    kwargs = {
        "query_embeddings": [embedding],
        "n_results": min(n, collection.count() or 1),
        "include": ["documents", "metadatas", "distances"]
    }
    if filters:
        kwargs["where"] = filters

    results = collection.query(**kwargs)

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        output.append({
            "text": doc,
            "metadata": meta,
            "score": round(1 - dist, 3)  # convert distance to similarity
        })
    return output


def get_all(collection_name: str) -> list[dict]:
    """Fetch everything in a collection (for inspection/debug)."""
    collection = get_collection(collection_name)
    results = collection.get(include=["documents", "metadatas"])
    output = []
    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        output.append({"id": doc_id, "text": doc, "metadata": meta})
    return output


def count(collection_name: str) -> int:
    return get_collection(collection_name).count()


def list_collections() -> list[str]:
    return [c.name for c in get_client().list_collections()]
