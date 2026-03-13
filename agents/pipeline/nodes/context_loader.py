"""
Context Loader Node
===================
POSITION: Agent 2 of 12

RECEIVES FROM STATE:
  primary_topic (str)       — from Classifier: e.g. "SaaS unit economics"
  domains       (List[str]) — from Classifier: e.g. ["finance", "strategy"]

ADDS TO STATE:
  context_chunks (List[ContextChunk]) — top existing chunks from ChromaDB related to the topic.
    Each has: id, name, collection, content (truncated to 400 chars), score

PASSES TO: Chunker (Agent 3), then flows to all subsequent agents
  context_chunks stay in state for the entire pipeline.
  Key consumers:
    Chunker      — avoids re-chunking concepts already in the database
    Enricher     — produces non-redundant implications
    Critic       — adds comparative dimension ("how does this differ from what you already know?")
    Enricher Refiner — distinguishes what's genuinely new from what's already captured

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT (from state, after Classifier):
    primary_topic = "SaaS unit economics"
    domains       = ["finance", "strategy"]

  SEARCH QUERY: "SaaS unit economics finance strategy"

  CONTEXT CHUNKS LOADED (what Friday already knows):
    [
      { id: "km_pmf_growth_metrics_001",
        name: "PMF Growth Metrics",
        collection: "knowledge",
        content: "Product-market fit can be measured through NPS...",
        score: 0.81 },
      { id: "km_jtbd_retention_levers_001",
        name: "JTBD and Retention",
        collection: "knowledge",
        content: "Jobs-to-be-done theory suggests retention follows...",
        score: 0.72 },
      ...
    ]

  HOW DOWNSTREAM AGENTS USE THIS:
    Chunker prompt: "These concepts already exist in Friday's DB: [list].
      Do not re-chunk what's already there. Only create chunks for genuinely new concepts."
    Enricher prompt: "Given Friday already knows: [context]. Your implications should
      build on this rather than restate it."
    Critic prompt: "Given existing knowledge [context], compare: does this new content
      agree with, extend, or challenge what Friday already knows?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NO LLM CALL — pure vector search, same as Connector.
On first run (empty database): returns empty list. All agents handle this gracefully.
"""

from typing import List, Dict, Any

from agents.pipeline.state import IngestionState, ContextChunk, PipelineLogEntry
from memory.store import search, list_collections


CONTEXT_K = 4          # Top-K results per collection
CONTEXT_MIN_SCORE = 0.5  # Lower threshold than Connector — we want broad awareness, not just tight matches
CONTEXT_MAX_CHARS = 400  # Truncate long chunks for context (we need the gist, not full text)
CONTEXT_COLLECTIONS = ["knowledge", "frameworks", "personal"]


def run_context_loader(state: IngestionState) -> Dict[str, Any]:
    """
    Loads existing related knowledge before the pipeline processes new content.
    Gives all downstream agents awareness of what Friday already knows.

    READS FROM STATE:  primary_topic, domains
    WRITES TO STATE:   context_chunks, pipeline_log
    """
    existing_collections = list_collections()
    searchable = [c for c in CONTEXT_COLLECTIONS if c in existing_collections]

    context_chunks: List[ContextChunk] = []
    seen_ids: set = set()

    # Build query from topic + domains — broad enough to surface related knowledge
    query = f"{state['primary_topic']} {' '.join(state['domains'])}"

    for collection in searchable:
        try:
            results = search(collection, query, n=CONTEXT_K)
            for r in results:
                chunk_id = r["metadata"].get("id", "")
                if not chunk_id:
                    continue
                if chunk_id in seen_ids or r["score"] < CONTEXT_MIN_SCORE:
                    continue
                seen_ids.add(chunk_id)

                # Truncate long content to keep context concise
                content = r["text"]
                if len(content) > CONTEXT_MAX_CHARS:
                    content = content[:CONTEXT_MAX_CHARS] + "..."

                context_chunks.append({
                    "id":         chunk_id,
                    "name":       r["metadata"].get("name", "Unknown"),
                    "collection": collection,
                    "content":    content,
                    "score":      r["score"],
                })
        except Exception:
            # Collection empty or search fails — graceful skip
            pass

    # Sort by relevance descending so agents see the most related chunks first
    context_chunks.sort(key=lambda x: x["score"], reverse=True)

    summary = f"Loaded {len(context_chunks)} existing related chunks as context"
    if not context_chunks:
        summary = "No existing related chunks found (first run or unrelated topic)"

    log_entry: PipelineLogEntry = {
        "stage":   "context_loader",
        "status":  "done",
        "summary": summary,
        "detail":  [
            {"id": c["id"], "name": c["name"], "score": c["score"]}
            for c in context_chunks
        ],
    }

    return {
        "context_chunks": context_chunks,
        "pipeline_log":   state["pipeline_log"] + [log_entry],
    }
