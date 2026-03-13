"""
Writer Node
===========
POSITION: Agent 11 of 12

RECEIVES FROM STATE:
  final_chunks (List[FinalChunk]) — from Assembler: fully assembled chunks ready for storage
    Each FinalChunk has: id, name, collection, domain, chunk_type,
                         your_analysis, content (full enriched text), metadata (dict)

ADDS TO STATE:
  write_log (List[Dict]) — one entry per chunk attempted:
    id         (str) — the chunk ID written
    collection (str) — "knowledge" | "frameworks" | "personal"
    status     (str) — "ok" | "error: <message>"

PASSES TO: Synthesizer (Agent 12)
  Synthesizer reads write_log to count successes and errors for the summary.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT FinalChunk (one of potentially many):
    {
      "id":            "km_saas_cac_payback_001",
      "collection":    "knowledge",
      "content":       "CAC payback period is the number of months...\n\n**Implications**\n...",
      "metadata": {
        "name":          "CAC Payback Period Mechanics",
        "domain":        "finance",
        "chunk_type":    "principle",
        "your_analysis": False,         ← bool — must be sanitized before upsert()
        "source":        "ingestion_pipeline",
        "related_ids":   "km_pmf_growth_metrics_001"
      }
    }

  METADATA SANITIZATION:
    False           → "False"    (bool → str)
    True            → "True"     (bool → str)
    ["a","b"]       → "a,b"      (list → comma-joined str)
    None            → ""         (None → empty str)
    42              → "42"       (int → str for consistency)

  UPSERT CALL:
    store.upsert(
      collection_name = "knowledge",
      text            = chunk["content"],
      metadata        = { "name": "CAC Payback...", "your_analysis": "False", ... },
      doc_id          = "km_saas_cac_payback_001"
    )
    ChromaDB internally: embed text → store (content, metadata, vector) under this ID

  WRITE LOG OUTPUT (added to state):
    [
      { "id": "km_saas_cac_payback_001",           "collection": "knowledge", "status": "ok" },
      { "id": "km_saas_cac_payback_001_critique",   "collection": "knowledge", "status": "ok" },
      { "id": "km_saas_ltv_cac_ratio_001",          "collection": "knowledge", "status": "ok" },
      { "id": "km_saas_ltv_cac_ratio_001_critique", "collection": "knowledge", "status": "ok" },
      ...
    ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UPSERT vs ADD — WHY UPSERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ChromaDB's add() raises DuplicateIDError if the same ID is added twice.
  upsert() updates in place if the ID already exists.

  This means:
    - Running the pipeline twice on the same content → updates, not duplicates
    - The chunk ID is the deduplication key (set by Chunker, e.g. "km_saas_cac_payback_001")
    - Safe to re-process content after editing it — the old chunk is replaced
    - Safe to run pipeline tests repeatedly without polluting the database

CHROMADB METADATA CONSTRAINT:
  ChromaDB's Python client rejects metadata values that are:
    - bool (even though Python bool is a subclass of int, ChromaDB rejects it)
    - list or dict
    - None
  All values must be str, int, or float.
  _sanitize_metadata() handles this transformation before every upsert().

NO LLM CALL — pure I/O: sanitize metadata → call store.upsert() → log result.
"""

from typing import List, Dict, Any

from agents.pipeline.state import IngestionState, FinalChunk, PipelineLogEntry
from memory.store import upsert


def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, str]:
    """
    Ensure all metadata values are ChromaDB-safe (str/int/float).
    ChromaDB rejects booleans, lists, dicts, and None.
    """
    safe: Dict[str, str] = {}
    for key, value in metadata.items():
        if isinstance(value, bool):
            safe[key] = str(value)
        elif isinstance(value, (int, float)):
            safe[key] = str(value)   # normalize everything to str for consistency
        elif isinstance(value, list):
            safe[key] = ",".join(str(v) for v in value)
        elif value is None:
            safe[key] = ""
        else:
            safe[key] = str(value)
    return safe


def run_writer(state: IngestionState) -> Dict[str, Any]:
    """
    Upserts all final chunks into ChromaDB.
    Builds a write_log tracking each chunk's outcome.
    """
    final_chunks: List[FinalChunk] = state["final_chunks"]
    write_log: List[Dict[str, str]] = []
    counts: Dict[str, int] = {"knowledge": 0, "frameworks": 0, "personal": 0}

    for chunk in final_chunks:
        try:
            safe_metadata = _sanitize_metadata(chunk["metadata"])

            upsert(
                collection_name=chunk["collection"],
                text=chunk["content"],
                metadata=safe_metadata,
                doc_id=chunk["id"],
            )

            write_log.append({
                "id":         chunk["id"],
                "collection": chunk["collection"],
                "status":     "ok",
            })
            counts[chunk["collection"]] = counts.get(chunk["collection"], 0) + 1

        except Exception as e:
            write_log.append({
                "id":         chunk["id"],
                "collection": chunk["collection"],
                "status":     f"error: {str(e)}",
            })

    ok_count    = sum(1 for w in write_log if w["status"] == "ok")
    error_count = len(write_log) - ok_count
    counts_str  = ", ".join(f"{col}: {n}" for col, n in counts.items() if n > 0)

    summary = f"Wrote {ok_count}/{len(final_chunks)} chunks to ChromaDB ({counts_str})"
    if error_count:
        summary += f" — {error_count} errors"

    log_entry: PipelineLogEntry = {
        "stage":   "writer",
        "status":  "done" if error_count == 0 else "partial",
        "summary": summary,
        "detail":  write_log,
    }

    return {
        "write_log":    write_log,
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
