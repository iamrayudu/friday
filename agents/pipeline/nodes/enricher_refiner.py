"""
Enricher Refiner Node
=====================
POSITION: Agent 6 of 12

RECEIVES FROM STATE:
  raw_chunks      (List[RawChunk])   — from Chunker: the original concept units
  enrichments     (List[Enrichment]) — from Enricher: first-pass enrichments
  critiques       (List[Critique])   — from Critic: limitations/biases/stress_tests
  context_chunks  (List[ContextChunk]) — from Context Loader: what Friday already knows
  primary_topic   (str)              — from Classifier
  domains         (List[str])        — from Classifier

ADDS TO STATE:
  enrichments (List[Enrichment]) — REPLACES the original enrichments with refined versions
    The Enricher Refiner's output overwrites state["enrichments"].
    This means the Assembler (Agent 10) always gets the best enrichments.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE AGENT DIALOGUE — HOW THIS NODE FITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  TURN 1 — Enricher (Agent 4):
    Reads raw chunks + existing context.
    Produces: first-pass enrichments (implications, use_cases, follow_up_questions).
    These are good but may be generic, may overlap with existing knowledge,
    or may miss the angles revealed by the Critic's analysis.

  TURN 2 — Critic (Agent 5):
    Reads raw chunks + first-pass enrichments.
    Produces: limitations, biases, stress tests that challenge each chunk.
    Exposes: where the chunk's idea breaks down, what assumptions it makes.

  TURN 3 — Enricher Refiner (THIS NODE):
    Reads: original enrichments + critiques + existing context.
    Produces: REFINED enrichments that:
      - Are sharper and more non-obvious than first pass
      - Follow-up questions that probe the Critic's identified limitations
      - Use cases that account for when the idea doesn't apply
      - Implications that distinguish what's new vs. what Friday already knows

  This 3-turn loop is what makes the enrichments substantially better than a
  single-pass system. The dialogue between Enricher and Critic produces depth
  that neither could achieve alone.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CHUNK: "km_saas_cac_payback_001" — CAC Payback Period Mechanics

  INITIAL ENRICHMENT (from Enricher Turn 1):
    implications: ["Short payback = reinvest revenue faster", ...]
    use_cases:    ["Evaluate SaaS fundraise readiness", ...]

  CRITIC'S ANALYSIS (Turn 2):
    limitations:  ["Calibrated for VC-funded SaaS — bootstrap businesses tolerate longer payback"]
    stress_tests: ["What if payback is 8 months but NRR is 70%? Payback alone doesn't signal health."]

  REFINED ENRICHMENT (from THIS NODE, Turn 3):
    implications: [
      "Short payback enables compounding growth WITHOUT external capital — a moat for bootstrapped SaaS.",
      "The 12-month benchmark assumes VC-funded growth; product-led growth companies with near-zero CAC make this metric misleading."
    ]
    follow_up_questions: [
      "How does payback change when channel mix shifts from paid (high CAC) to product-led (low CAC)?",
      "At what NRR threshold does a long payback period become acceptable? (payback + churn interaction)"
    ]
    use_cases: [
      "When diligencing a SaaS acquisition, pair payback with NRR: payback < 12 months AND NRR > 110% = exceptional efficiency.",
      "When advising a bootstrapped SaaS: don't apply the 12-month VC benchmark — focus on payback relative to your runway."
    ]

  The second-pass enrichments are demonstrably better: they're more specific,
  they account for the limitations raised by the Critic, and they surface the
  non-obvious angle (bootstrap vs. VC context matters for this metric).

ONE LLM CALL for all chunks — efficient, lets the Refiner see patterns across chunks.
"""

import json
from typing import List, Dict, Any

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from agents.pipeline.state import IngestionState, Enrichment, PipelineLogEntry
from agents.pipeline.utils import get_llm


# ── Structured output schema ──────────────────────────────────────────────────

class RefinedChunkEnrichment(BaseModel):
    chunk_id: str = Field(description="Must exactly match one of the input chunk IDs")
    implications: List[str] = Field(
        description="2-3 sharper, more non-obvious second-order consequences. "
                    "Must account for the limitations identified by the Critic. "
                    "Must not repeat what already exists in Friday's knowledge base."
    )
    follow_up_questions: List[str] = Field(
        description="2-3 specific research questions that probe the limitations and biases "
                    "identified by the Critic. Should push into the uncomfortable edges."
    )
    use_cases: List[str] = Field(
        description="2-3 concrete application scenarios. Should specify WHEN to use vs. "
                    "WHEN NOT to use (accounting for limitations). Be scenario-specific."
    )


class EnricherRefinerOutput(BaseModel):
    enrichments: List[RefinedChunkEnrichment] = Field(
        description="One refined enrichment per input chunk. Must cover every chunk_id."
    )


SYSTEM_PROMPT = """You are the Enricher Refiner — the third turn in a 3-turn agent dialogue.

The dialogue:
  Turn 1 (Enricher):         proposed initial enrichments for each knowledge chunk
  Turn 2 (Critic):           challenged each chunk with limitations, biases, stress tests
  Turn 3 (YOU, Refiner):     refine the enrichments in light of the critique

Friday is a personal second brain for Sudheer — an MBA student / tech professional.

YOUR JOB: Produce REFINED enrichments that are substantially better than Turn 1.

REFINEMENT PRINCIPLES:
  1. CRITIQUE-AWARE IMPLICATIONS
     Where the Critic found a limitation, your implications should acknowledge it.
     Not: "Short payback enables faster growth"
     But: "Short payback enables faster growth in VC-funded models — in bootstrapped businesses,
          payback is less binding because the constraint is operating cash flow, not raise timing."

  2. PROBE-THE-EDGES FOLLOW-UP QUESTIONS
     The Critic identified where the idea breaks down. Your follow-up questions should go there.
     Not: "How does CAC payback work in different industries?"
     But: "At what NRR does a high payback period become acceptable? What's the payback × NRR interaction?"

  3. CONDITIONAL USE CASES
     Use cases should specify WHEN to apply AND when NOT to apply the idea.
     Not: "Use this for fundraise diligence"
     But: "Use payback < 12 months as a fundraise signal for VC-backed SaaS;
          ignore it for bootstrapped businesses where the benchmark doesn't apply."

  4. NON-REDUNDANT WITH EXISTING KNOWLEDGE
     You're given what Friday already knows (context_chunks).
     Your implications must add something new, not restate existing chunks.

Keep each point to 1-3 sentences. Depth over breadth."""


def run_enricher_refiner(state: IngestionState) -> Dict[str, Any]:
    """
    Refines enrichments after seeing the Critic's analysis.
    Third turn in the Enricher → Critic → Enricher Refiner dialogue.
    OVERWRITES state["enrichments"] with the refined version.

    READS FROM STATE:  raw_chunks, enrichments, critiques, context_chunks, primary_topic, domains
    WRITES TO STATE:   enrichments (refined), pipeline_log
    """
    raw_chunks = state["raw_chunks"]

    if not raw_chunks:
        log_entry: PipelineLogEntry = {
            "stage":   "enricher_refiner",
            "status":  "done",
            "summary": "No chunks to refine",
            "detail":  [],
        }
        return {
            "enrichments":  [],
            "pipeline_log": state["pipeline_log"] + [log_entry],
        }

    llm = get_llm(temperature=0.4)  # slightly higher — refined thinking benefits from creativity
    structured_llm = llm.with_structured_output(EnricherRefinerOutput)

    # Build an enrichment lookup for easy access
    enrichment_lookup = {e["chunk_id"]: e for e in state["enrichments"]}
    critique_lookup = {c["chunk_id"]: c for c in state["critiques"]}

    # Combine everything for the LLM: original chunk + first-pass enrichment + critique
    chunks_with_dialogue = []
    for chunk in raw_chunks:
        e = enrichment_lookup.get(chunk["id"], {})
        c = critique_lookup.get(chunk["id"], {})
        chunks_with_dialogue.append({
            "chunk_id":    chunk["id"],
            "name":        chunk["name"],
            "domain":      chunk["domain"],
            "chunk_type":  chunk["chunk_type"],
            "content":     chunk["content"],
            "initial_enrichment": {
                "implications":        e.get("implications", []),
                "follow_up_questions": e.get("follow_up_questions", []),
                "use_cases":           e.get("use_cases", []),
            },
            "critics_analysis": {
                "limitations":   c.get("limitations", []),
                "biases":        c.get("biases", []),
                "stress_tests":  c.get("stress_tests", []),
            },
        })

    # Format existing context
    context_summary = ""
    if state["context_chunks"]:
        context_lines = [
            f"  - [{c['name']}] ({c['collection']}, score {c['score']}): {c['content'][:150]}..."
            for c in state["context_chunks"][:5]
        ]
        context_summary = "\n\nFriday already knows about this topic:\n" + "\n".join(context_lines)

    user_message = (
        f"Primary topic: {state['primary_topic']}\n"
        f"Domains: {', '.join(state['domains'])}"
        f"{context_summary}\n\n"
        f"Dialogue so far (initial enrichments + critic's analysis):\n"
        f"{json.dumps(chunks_with_dialogue, indent=2)}"
    )

    result: EnricherRefinerOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    # Check for missed chunks
    refined_ids = {e.chunk_id for e in result.enrichments}
    missing = [c["id"] for c in raw_chunks if c["id"] not in refined_ids]

    refined_enrichments: List[Enrichment] = [
        {
            "chunk_id":             e.chunk_id,
            "implications":         e.implications,
            "follow_up_questions":  e.follow_up_questions,
            "use_cases":            e.use_cases,
        }
        for e in result.enrichments
    ]

    summary = f"Refined enrichments for {len(refined_enrichments)}/{len(raw_chunks)} chunks after Critic dialogue"
    if missing:
        summary += f" (missed: {', '.join(missing)})"

    log_entry = {
        "stage":   "enricher_refiner",
        "status":  "done",
        "summary": summary,
        "detail":  [{"chunk_id": e["chunk_id"]} for e in refined_enrichments],
    }

    return {
        "enrichments":  refined_enrichments,  # OVERWRITES the initial enrichments
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
