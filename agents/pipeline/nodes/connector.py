"""
Connector Node
==============
POSITION: Agent 8 of 12

RECEIVES FROM STATE:
  raw_chunks    (List[RawChunk]) — from Chunker: each chunk is one standalone concept
  primary_topic (str)            — from Classifier: e.g. "SaaS unit economics"
  domains       (List[str])      — from Classifier: e.g. ["finance", "strategy"]

ADDS TO STATE:
  connection_map (List[Connection]) — one per raw_chunk, matched by chunk_id, each containing:
    chunk_id           (str)       — matches the raw_chunk id exactly
    related_ids        (List[str]) — IDs of existing ChromaDB chunks with high similarity
    relationship_notes (str)       — human-readable string with score and collection info

PASSES TO: Relationship Typer (Agent 9)
  The Assembler reads connection_map to write related_ids as comma-separated
  string in the FinalChunk's metadata. This metadata is then stored in ChromaDB
  so Friday can surface related knowledge during retrieval.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT CHUNK (from state):
    {
      "id":      "km_saas_cac_payback_001",
      "name":    "CAC Payback Period Mechanics",
      "content": "CAC payback period is the number of months of gross-margin
                  revenue needed to recoup the customer acquisition cost. A
                  payback < 12 months means you can reinvest profits quickly."
    }

  SEARCH PROCESS:
    1. Embed chunk["content"] using all-MiniLM-L6-v2 (384-dim vector)
    2. Query "knowledge" collection: nearest neighbors in cosine space
    3. Query "frameworks" collection: nearest neighbors in cosine space
    4. Keep only results where score >= 0.65 (high confidence match)
    5. Skip self-matches (same chunk ID already in DB from a previous run)

  OUTPUT CONNECTION (added to state):
    {
      "chunk_id":   "km_saas_cac_payback_001",
      "related_ids": [
        "km_pmf_growth_metrics_001",
        "km_jtbd_retention_levers_001"
      ],
      "relationship_notes": "km_pmf_growth_metrics_001 (score: 0.81, collection: knowledge); km_jtbd_retention_levers_001 (score: 0.68, collection: knowledge)"
    }

  HOW THIS SHOWS UP IN CHROMADB (after Assembler + Writer):
    The core chunk "km_saas_cac_payback_001" stored in ChromaDB will have:
      metadata["related_ids"] = "km_pmf_growth_metrics_001,km_jtbd_retention_levers_001"
    This lets Friday's chat agent say: "This chunk also relates to PMF metrics
    and JTBD retention — do you want me to pull those in too?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW IT WORKS — NO LLM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Unlike every other agent in this pipeline, the Connector makes zero LLM calls.
  Connections are established by VECTOR SIMILARITY, not by reasoning:

    chunk.content → embedding model → 384-dim vector
        ↓
    ChromaDB cosine similarity search (TOP_K=3 per collection)
        ↓
    filter: score >= SIMILARITY_THRESHOLD (0.65)
        ↓
    related_ids = [ids of matching existing chunks]

  This is intentional:
    - Fast: embedding + ANN search is ~10ms vs ~2s for an LLM call
    - Objective: cosine similarity doesn't hallucinate relationships
    - Scales: works whether the DB has 10 chunks or 10,000 chunks
    - Same model at ingest and query time (all-MiniLM-L6-v2, 384-dim)
      ensures consistent vector space across all stored chunks

FIRST RUN (empty database):
  If the database has no existing chunks yet, all searches return empty.
  Every connection_map entry will have related_ids=[] and
  relationship_notes="no connections found". This is fine — the Assembler
  handles empty related_ids gracefully. Connections build up over time.

WHY THIS NODE EXISTS:
  Knowledge becomes more valuable when it's connected.
  Without the Connector, every chunk in ChromaDB is an isolated island.
  With the Connector, new knowledge gets anchored to what's already known.
  As Sudheer adds more content, the knowledge web grows denser —
  making Friday increasingly effective at surfacing relevant prior knowledge.
"""

from typing import List, Dict, Any

from agents.pipeline.state import IngestionState, Connection, PipelineLogEntry
from memory.store import search, list_collections

# Minimum similarity score to count as a meaningful connection
SIMILARITY_THRESHOLD = 0.65

# How many related chunks to look for per new chunk
TOP_K = 3

# Collections to search for connections (not personal — too noisy)
SEARCH_COLLECTIONS = ["knowledge", "frameworks"]


def run_connector(state: IngestionState) -> Dict[str, Any]:
    """
    Finds connections between new chunks and existing ChromaDB content.
    Pure vector similarity — no LLM call needed.
    """
    raw_chunks = state["raw_chunks"]

    if not raw_chunks:
        log_entry: PipelineLogEntry = {
            "stage":   "connector",
            "status":  "done",
            "summary": "No chunks to connect",
            "detail":  [],
        }
        return {
            "connection_map": [],
            "pipeline_log":   state["pipeline_log"] + [log_entry],
        }

    # Check which collections exist in the DB
    existing_collections = list_collections()
    searchable = [c for c in SEARCH_COLLECTIONS if c in existing_collections]

    connection_map: List[Connection] = []
    total_connections = 0

    for chunk in raw_chunks:
        related_ids: List[str] = []
        notes_parts: List[str] = []

        for collection in searchable:
            try:
                results = search(collection, chunk["content"], n=TOP_K)
                for r in results:
                    # Only keep high-confidence connections, skip self (same ID)
                    if r["score"] >= SIMILARITY_THRESHOLD and r["metadata"].get("id") != chunk["id"]:
                        # ChromaDB doesn't always store id in metadata — use the doc ID from get_all
                        # The search() function returns metadata dict; IDs come from the collection
                        # We use the "name" field as a proxy identifier when id isn't in metadata
                        related_name = r["metadata"].get("name", "unknown")
                        related_id   = r["metadata"].get("id", related_name)
                        if related_id not in related_ids:
                            related_ids.append(related_id)
                            notes_parts.append(
                                f"{related_id} (score: {r['score']}, collection: {collection})"
                            )
            except Exception:
                # If a collection is empty or search fails, skip it silently
                pass

        relationship_notes = "; ".join(notes_parts) if notes_parts else "no connections found"

        connection_map.append({
            "chunk_id":           chunk["id"],
            "related_ids":        related_ids,
            "relationship_notes": relationship_notes,
        })
        total_connections += len(related_ids)

    chunks_with_connections = sum(1 for c in connection_map if c["related_ids"])

    log_entry = {
        "stage":   "connector",
        "status":  "done",
        "summary": f"Found {total_connections} connections for {chunks_with_connections}/{len(raw_chunks)} chunks",
        "detail":  [
            {"chunk_id": c["chunk_id"], "connections": len(c["related_ids"])}
            for c in connection_map
        ],
    }

    return {
        "connection_map": connection_map,
        "pipeline_log":   state["pipeline_log"] + [log_entry],
    }
