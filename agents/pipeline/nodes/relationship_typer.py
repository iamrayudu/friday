"""
Relationship Typer Node
=======================
POSITION: Agent 9 of 12

RECEIVES FROM STATE:
  raw_chunks     (List[RawChunk])  — from Chunker: new chunks
  connection_map (List[Connection]) — from Connector: related_ids found by vector similarity

ADDS TO STATE:
  relationship_map (List[RelationshipEntry]) — for each (new chunk, related chunk) pair:
    chunk_id          (str) — new chunk ID
    related_id        (str) — existing chunk ID (found by Connector)
    relationship_type (str) — BUILDS_ON | EXTENDS | APPLIES | CONTRADICTS | PARALLELS | EXEMPLIFIES
    explanation       (str) — 1-2 sentences explaining why this relationship holds

PASSES TO: Assembler (Agent 10)
  Assembler reads relationship_map to enrich FinalChunk metadata with relationship types.
  Stored as: relationship_types = "BUILDS_ON:km_pmf_001,EXTENDS:km_jtbd_001"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONNECTOR vs RELATIONSHIP TYPER — DIVISION OF LABOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Connector (Agent 8) — WHO is related?
    Uses vector similarity (cosine distance) to find IDs of existing chunks
    that are semantically close to each new chunk.
    Fast, objective, mathematically grounded. No LLM needed.

  Relationship Typer (THIS NODE) — HOW are they related?
    Takes those related IDs, fetches the actual content of each related chunk,
    and asks an LLM: "Given chunk A and existing chunk B, what is their
    intellectual relationship?"
    Slow(er), but produces semantically rich relationship metadata.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RELATIONSHIP TYPES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  BUILDS_ON   — new chunk extends/deepens the existing; learning existing enriches the new
  EXTENDS     — new chunk adds a dimension/nuance not covered by existing
  APPLIES     — new chunk demonstrates how to use existing framework in a specific context
  CONTRADICTS — new chunk challenges or offers evidence against existing chunk's claim
  PARALLELS   — both address same question from different angles/traditions
  EXEMPLIFIES — new chunk is a concrete case/instance of existing general principle

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  NEW CHUNK:
    id:      "km_saas_cac_payback_001"
    content: "CAC payback period is the number of months of gross-margin revenue..."

  RELATED EXISTING CHUNKS (from Connector):
    "km_pmf_growth_metrics_001" (score 0.81)
    "km_jtbd_retention_levers_001" (score 0.68)

  RELATIONSHIP MAP OUTPUT:
    [
      { chunk_id:          "km_saas_cac_payback_001",
        related_id:        "km_pmf_growth_metrics_001",
        relationship_type: "BUILDS_ON",
        explanation:       "CAC payback assumes a working PMF (you have customers paying
                           you) — understanding PMF growth metrics provides the business
                           context in which payback analysis is meaningful." },
      { chunk_id:          "km_saas_cac_payback_001",
        related_id:        "km_jtbd_retention_levers_001",
        relationship_type: "PARALLELS",
        explanation:       "Both analyze how to keep customers, but from different angles:
                           JTBD focuses on why customers stay (job fulfillment), while CAC
                           payback focuses on the financial cost of acquiring them." }
    ]

  HOW THIS SHOWS UP IN CHROMADB (via Assembler + Writer):
    metadata["relationship_types"] = "BUILDS_ON:km_pmf_growth_metrics_001,PARALLELS:km_jtbd_retention_levers_001"

ONE LLM CALL covering all (new chunk, related chunk) pairs together.
Skipped gracefully if connection_map is empty (first run or no connections found).
"""

import json
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from agents.pipeline.state import IngestionState, RelationshipEntry, PipelineLogEntry
from agents.pipeline.utils import get_llm
from memory.store import get_collection, list_collections


# ── Helper to fetch related chunk content from ChromaDB ──────────────────────

def _fetch_chunk_text(chunk_id: str) -> Optional[str]:
    """
    Try to fetch an existing chunk's text from any collection by ID.
    Returns first 400 chars (enough context for relationship classification).
    Returns None if not found.
    """
    for col_name in ["knowledge", "frameworks", "personal"]:
        try:
            col = get_collection(col_name)
            result = col.get(ids=[chunk_id], include=["documents", "metadatas"])
            if result and result["ids"]:
                text = result["documents"][0]
                return text[:400] + "..." if len(text) > 400 else text
        except Exception:
            pass
    return None


# ── Structured output schema ──────────────────────────────────────────────────

class RelationshipClassification(BaseModel):
    chunk_id: str = Field(description="The new chunk's ID")
    related_id: str = Field(description="The existing related chunk's ID")
    relationship_type: str = Field(
        description="Exactly one of: BUILDS_ON | EXTENDS | APPLIES | CONTRADICTS | PARALLELS | EXEMPLIFIES"
    )
    explanation: str = Field(
        description="1-2 sentences explaining specifically why this relationship type applies. "
                    "Reference the content of both chunks in the explanation."
    )


class RelationshipTyperOutput(BaseModel):
    relationships: List[RelationshipClassification] = Field(
        description="One entry for each (new_chunk, related_chunk) pair."
    )


SYSTEM_PROMPT = """You are the Relationship Typer in Friday's knowledge pipeline.

Friday is a personal second brain for Sudheer — MBA student / tech professional.

YOUR JOB: For each pair of (new chunk, related existing chunk), classify their intellectual relationship.

RELATIONSHIP TYPES:
  BUILDS_ON   — The new chunk directly extends or deepens the existing; understanding the existing
                chunk first makes the new chunk clearer or more meaningful.
                E.g.: "CAC payback" BUILDS_ON "what is CAC"

  EXTENDS     — The new chunk adds a dimension, nuance, or application that the existing chunk
                doesn't cover. Both remain separately useful.
                E.g.: "Blended vs. paid-only CAC" EXTENDS "CAC payback mechanics"

  APPLIES     — The new chunk is a specific application of the existing chunk's framework
                or principle in a particular context.
                E.g.: "Applying Porter's Five Forces to Netflix" APPLIES "Porter's Five Forces framework"

  CONTRADICTS — The new chunk challenges, disputes, or offers counter-evidence to the existing
                chunk's central claim. Not just a different angle — a genuine tension.
                E.g.: "Product-led growth invalidates traditional CAC" CONTRADICTS "CAC payback mechanics"

  PARALLELS   — Both chunks address the same fundamental question but from different intellectual
                traditions, schools of thought, or analytical frameworks.
                E.g.: "Porter's Five Forces" PARALLELS "Blue Ocean Strategy"

  EXEMPLIFIES — The new chunk is a concrete case, example, or instance of the existing chunk's
                general principle or theory.
                E.g.: "How Slack's pricing evolved" EXEMPLIFIES "SaaS pricing theory"

IMPORTANT:
  - Use the EXACT chunk_id strings — do not modify them
  - Be specific in your explanation — name what the intellectual connection actually is
  - If two chunks are related but none of the types fit well, choose the closest one and
    explain why in the explanation field"""


def run_relationship_typer(state: IngestionState) -> Dict[str, Any]:
    """
    Classifies the type of relationship between new chunks and their related existing chunks.
    Uses the connection_map from Connector as input.

    READS FROM STATE:  raw_chunks, connection_map
    WRITES TO STATE:   relationship_map, pipeline_log
    """
    connection_map = state["connection_map"]

    # Check if there are any connections to classify
    pairs_to_classify = [
        (conn["chunk_id"], related_id)
        for conn in connection_map
        for related_id in conn["related_ids"]
    ]

    if not pairs_to_classify:
        log_entry: PipelineLogEntry = {
            "stage":   "relationship_typer",
            "status":  "done",
            "summary": "No connections to classify (empty DB or no related chunks found)",
            "detail":  [],
        }
        return {
            "relationship_map": [],
            "pipeline_log":     state["pipeline_log"] + [log_entry],
        }

    llm = get_llm(temperature=0.1)  # low temperature — classification should be precise
    structured_llm = llm.with_structured_output(RelationshipTyperOutput)

    # Build chunk content lookup for new chunks
    new_chunk_lookup = {c["id"]: c for c in state["raw_chunks"]}

    # Build the pairs list with actual content for the LLM
    pairs_for_llm = []
    for chunk_id, related_id in pairs_to_classify:
        new_chunk = new_chunk_lookup.get(chunk_id, {})
        existing_text = _fetch_chunk_text(related_id)

        if existing_text is None:
            # Can't fetch the related chunk — skip this pair
            continue

        pairs_for_llm.append({
            "new_chunk": {
                "id":      chunk_id,
                "name":    new_chunk.get("name", "Unknown"),
                "content": new_chunk.get("content", "")[:300],
            },
            "existing_chunk": {
                "id":      related_id,
                "content": existing_text,
            },
        })

    if not pairs_for_llm:
        log_entry = {
            "stage":   "relationship_typer",
            "status":  "done",
            "summary": "No pairs to classify (related chunks not found in DB)",
            "detail":  [],
        }
        return {
            "relationship_map": [],
            "pipeline_log":     state["pipeline_log"] + [log_entry],
        }

    user_message = (
        f"Classify the relationship for each of the following (new chunk, existing chunk) pairs:\n\n"
        f"{json.dumps(pairs_for_llm, indent=2)}"
    )

    result: RelationshipTyperOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    relationship_map: List[RelationshipEntry] = [
        {
            "chunk_id":          r.chunk_id,
            "related_id":        r.related_id,
            "relationship_type": r.relationship_type,
            "explanation":       r.explanation,
        }
        for r in result.relationships
    ]

    # Count relationship types for the log
    type_counts: Dict[str, int] = {}
    for r in relationship_map:
        type_counts[r["relationship_type"]] = type_counts.get(r["relationship_type"], 0) + 1
    types_str = ", ".join(f"{t}: {n}" for t, n in type_counts.items())

    log_entry = {
        "stage":   "relationship_typer",
        "status":  "done",
        "summary": f"Classified {len(relationship_map)} relationships ({types_str})",
        "detail":  [
            {
                "new_chunk":   r["chunk_id"],
                "related":     r["related_id"],
                "type":        r["relationship_type"],
                "explanation": r["explanation"],
            }
            for r in relationship_map
        ],
    }

    return {
        "relationship_map": relationship_map,
        "pipeline_log":     state["pipeline_log"] + [log_entry],
    }
