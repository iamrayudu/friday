"""
Enricher Node
=============
POSITION: Agent 4 of 12

RECEIVES FROM STATE:
  raw_chunks     (List[RawChunk])     — from Chunker: each chunk is one standalone concept
  primary_topic  (str)                — from Classifier: e.g. "SaaS unit economics"
  domains        (List[str])          — from Classifier: e.g. ["finance", "strategy"]
  context_chunks (List[ContextChunk]) — from Context Loader: what Friday already knows

ADDS TO STATE:
  enrichments (List[Enrichment]) — one per raw_chunk, matched by chunk_id, each containing:
    chunk_id            (str)       — matches the raw_chunk id exactly
    implications        (List[str]) — 2-3 second-order consequences of this idea
    follow_up_questions (List[str]) — 2-3 specific questions this chunk raises
    use_cases           (List[str]) — 2-3 concrete scenarios where this knowledge applies

PASSES TO: Critic (Agent 5)
  The Critic reads raw_chunks + enrichments from state.
  Enrichments are also consumed by the Enricher Refiner (Agent 6) which refines them
  in light of the Critic's analysis, and finally by the Assembler (Agent 10) which
  appends the refined enrichments to the core chunk content under markdown headers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT CHUNK (one of potentially several):
    {
      "id":         "km_saas_cac_payback_001",
      "name":       "CAC Payback Period Mechanics",
      "domain":     "finance",
      "chunk_type": "principle",
      "content":    "CAC payback period is the number of months of gross-margin
                     revenue needed to recoup the customer acquisition cost.
                     Payback < 12 months = healthy. Payback > 18 months = high
                     capital risk at scale."
    }

  OUTPUT ENRICHMENT (added to state):
    {
      "chunk_id": "km_saas_cac_payback_001",
      "implications": [
        "Short payback means you can reinvest revenue into growth quickly,
         enabling compounding without needing continuous external capital.",
        "High payback periods mean early-stage SaaS companies must raise
         more frequently — making them vulnerable to funding market conditions."
      ],
      "follow_up_questions": [
        "How does blended CAC (all channels combined) vs. paid-only CAC change
         the payback calculation, and which should you optimize for?",
        "At what payback threshold does a SaaS business become self-funding
         without needing venture capital?"
      ],
      "use_cases": [
        "Evaluating a SaaS startup's fundraise readiness: if payback > 18 months,
         they will likely need to raise before becoming profitable.",
        "Consulting diligence on a SaaS acquisition: payback period signals
         how efficiently the business converts marketing spend into margin."
      ]
    }

  HOW THIS BECOMES VISIBLE IN CHROMADB:
    The Assembler appends this enrichment to the core chunk's content as:
      "...original chunk text...

       **Implications**
       - Short payback means you can reinvest...
       - High payback periods mean early-stage...

       **Use Cases**
       - Evaluating a SaaS startup's fundraise readiness...
       - Consulting diligence on a SaaS acquisition...

       **Follow-up Questions**
       - How does blended CAC vs. paid-only CAC change..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS NODE EXISTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  The Enricher turns "knowing a fact" into "understanding what the fact means."

  Without enrichment, a chunk about CAC payback contains only the definition
  and benchmarks. When Friday retrieves it to answer a question, the LLM has
  to infer implications on the fly — sometimes well, sometimes not.

  With enrichment, the chunk already contains:
    - Where this idea leads (implications)
    - What it connects to that's not yet in the database (follow-up questions)
    - How to actually use it in practice (use cases)

  This is what makes Friday feel like a thinking partner rather than a search
  engine: the knowledge base contains not just facts, but the second-order
  thinking about those facts.

ONE LLM CALL for all chunks (not N calls) — efficient and gives the LLM
context about all chunks so it can avoid redundant implications across them.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
import json

from agents.pipeline.state import IngestionState, Enrichment, PipelineLogEntry
from agents.pipeline.utils import get_llm


# ── Structured output schema ──────────────────────────────────────────────────

class ChunkEnrichment(BaseModel):
    chunk_id: str = Field(description="Must exactly match one of the input chunk IDs")
    implications: List[str] = Field(
        description="2-3 second-order consequences. What follows from this idea? What does it change?"
    )
    follow_up_questions: List[str] = Field(
        description="2-3 specific questions this chunk raises. What should be researched next?"
    )
    use_cases: List[str] = Field(
        description="2-3 concrete situations where this knowledge would be directly applied"
    )


class EnricherOutput(BaseModel):
    enrichments: List[ChunkEnrichment] = Field(
        description="One enrichment per input chunk. Must cover every chunk_id provided."
    )


SYSTEM_PROMPT = """You are the Enricher in Friday's multi-agent knowledge ingestion pipeline.

Friday is a personal second brain for Sudheer — an MBA student with a background in tech.

YOUR JOB: For each knowledge chunk provided, add three layers of depth:
  1. IMPLICATIONS — what does this idea lead to? What second-order effects matter?
     Example: if the chunk is about CAC payback period, implications include:
     "short payback = can reinvest faster", "payback > 18 months = high risk at scale"
  2. FOLLOW-UP QUESTIONS — what should be researched next based on this chunk?
     Be specific. "How does X apply to Y context?" not just "Tell me more."
  3. USE CASES — concrete real-world situations where this knowledge gets applied.
     Prefer scenarios relevant to MBA, tech startups, product management, or consulting.

IMPORTANT:
  - Return one ChunkEnrichment per chunk_id. Do not skip any.
  - Use the EXACT chunk_id strings provided — do not modify them.
  - Keep each implication/question/use_case to 1-2 sentences max.
  - Make implications non-obvious — skip anything the reader already knows from the chunk.
  - For personal chunks (your_analysis: true), implications should be more reflective.
  - If context_chunks are provided, your implications MUST distinguish what's new vs. what Friday already knows.
    Don't restate what's already in the DB — build on it."""


def run_enricher(state: IngestionState) -> Dict[str, Any]:
    """
    Enriches all raw chunks with implications, questions, and use cases.
    Single LLM call for all chunks together.

    READS FROM STATE:  raw_chunks, primary_topic, domains, context_chunks
    WRITES TO STATE:   enrichments, pipeline_log
    """
    raw_chunks = state["raw_chunks"]

    # Edge case: no chunks to enrich (e.g. chunker returned empty on very short content)
    if not raw_chunks:
        log_entry: PipelineLogEntry = {
            "stage":   "enricher",
            "status":  "done",
            "summary": "No chunks to enrich",
            "detail":  [],
        }
        return {
            "enrichments": [],
            "pipeline_log": state["pipeline_log"] + [log_entry],
        }

    llm = get_llm(temperature=0.3)  # slightly higher temperature — implications benefit from creativity
    structured_llm = llm.with_structured_output(EnricherOutput)

    # Serialize chunks as JSON for the LLM — gives full chunk context per chunk_id
    chunks_for_llm = [
        {
            "chunk_id":      c["id"],
            "name":          c["name"],
            "domain":        c["domain"],
            "chunk_type":    c["chunk_type"],
            "your_analysis": c["your_analysis"],
            "content":       c["content"],
        }
        for c in raw_chunks
    ]

    # Format existing context for the LLM
    context_section = ""
    if state.get("context_chunks"):
        context_lines = [
            f"  - [{c['name']}] ({c['collection']}): {c['content'][:150]}..."
            for c in state["context_chunks"][:4]
        ]
        context_section = "\nWhat Friday already knows about this topic:\n" + "\n".join(context_lines) + "\n"

    # Primary topic and domains give the LLM context about what Sudheer is learning —
    # this lets it tailor implications to the right intellectual neighborhood
    user_message = (
        f"Primary topic: {state['primary_topic']}\n"
        f"Domains: {', '.join(state['domains'])}\n"
        f"{context_section}\n"
        f"Chunks to enrich:\n{json.dumps(chunks_for_llm, indent=2)}"
    )

    result: EnricherOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    # Convert to TypedDicts + warn if any chunk was missed by the LLM
    enrichment_ids = {e.chunk_id for e in result.enrichments}
    missing = [c["id"] for c in raw_chunks if c["id"] not in enrichment_ids]

    enrichments: List[Enrichment] = [
        {
            "chunk_id":             e.chunk_id,
            "implications":         e.implications,
            "follow_up_questions":  e.follow_up_questions,
            "use_cases":            e.use_cases,
        }
        for e in result.enrichments
    ]

    summary = f"Enriched {len(enrichments)}/{len(raw_chunks)} chunks with implications, questions, use cases"
    if missing:
        summary += f" (missed: {', '.join(missing)})"

    log_entry = {
        "stage":   "enricher",
        "status":  "done",
        "summary": summary,
        "detail":  [{"chunk_id": e["chunk_id"], "implications_count": len(e["implications"])} for e in enrichments],
    }

    return {
        "enrichments":  enrichments,
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
