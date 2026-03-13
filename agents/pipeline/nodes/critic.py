"""
Critic Node
===========
POSITION: Agent 5 of 12

RECEIVES FROM STATE:
  raw_chunks     (List[RawChunk])     — from Chunker: each chunk is one standalone concept
  primary_topic  (str)                — from Classifier: e.g. "SaaS unit economics"
  content_type   (str)                — from Classifier: e.g. "article" | "framework_ref" | "personal_reflection"
  enrichments    (List[Enrichment])   — from Enricher: first-pass implications/questions/use_cases
  context_chunks (List[ContextChunk]) — from Context Loader: what Friday already knows

ADDS TO STATE:
  critiques (List[Critique]) — one per raw_chunk, matched by chunk_id, each containing:
    chunk_id     (str)       — matches the raw_chunk id exactly
    limitations  (List[str]) — 2-3 specific situations where this idea breaks down
    biases       (List[str]) — 2-3 biases embedded in the knowledge (source, selection, temporal, etc.)
    stress_tests (List[str]) — 2-3 edge cases or counterexamples that challenge the chunk's claim

PASSES TO: Enricher Refiner (Agent 6)
  The Enricher Refiner reads both enrichments and critiques from state to produce
  refined enrichments that address the limitations and biases identified here.
  Critiques are also consumed by the Assembler (Agent 10), which turns each critique
  into a standalone "_critique" companion FinalChunk stored in the same collection
  as its parent, with chunk_type="critique" and parent_id metadata.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT CHUNK:
    {
      "chunk_id":   "km_jtbd_core_principle_001",
      "name":       "Jobs-to-be-Done Core Principle",
      "domain":     "product",
      "chunk_type": "principle",
      "content":    "Customers don't buy products — they hire them to do a job.
                     A job is the progress a person is trying to make in a
                     particular circumstance. Understanding the job (not the
                     customer demographic) is the unit of analysis for innovation."
    }

  OUTPUT CRITIQUE (added to state):
    {
      "chunk_id": "km_jtbd_core_principle_001",
      "limitations": [
        "JTBD is most useful for innovation and positioning decisions but offers
         little guidance for execution, pricing, or operational problems where
         customer demographics and cohort behavior matter more.",
        "The framework assumes a relatively stable 'job' — it struggles with
         rapidly evolving use cases (e.g. early-stage consumer apps) where
         users don't yet know what job they want done.",
        "Defining the job at the right level of abstraction is notoriously
         difficult in practice; too broad ('make my life better') and it's
         useless, too narrow ('send a file quickly') and you miss adjacent opportunities."
      ],
      "biases": [
        "Developed primarily from B2C and packaged goods examples (Clayton Christensen
         at HBS) — may not translate directly to B2B SaaS, platforms, or marketplaces
         where the 'job' is held by an organization, not an individual.",
        "Selection bias: the framework's most cited examples are successful products
         (milkshake study, Snickers bar). Failures where JTBD analysis was done
         correctly but the product still failed are rarely discussed."
      ],
      "stress_tests": [
        "What if two competing products do the same job equally well? JTBD gives no
         guidance on differentiation once the functional job is solved — you need
         emotional and social job layers, which are much harder to research reliably.",
        "Apply JTBD to a platform business (e.g. Airbnb): the host and guest have
         completely different jobs. The framework starts breaking down when the
         'customer' is not a single actor but a multi-sided market."
      ]
    }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS NODE EXISTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Before this node existed, limitation/bias/stress_test chunks had to be written
  manually in every seed script. Chunks like km_jtbd_stress_test_breaks,
  km_pmf_bias_flags, and km_sensemaking_vs_jtbd were individually hand-crafted
  for the initial knowledge base. That was only feasible for the seed content —
  it would never scale to everything Sudheer teaches Friday.

  The Critic generates this critical layer automatically for EVERY piece of
  content, regardless of domain or type. The knowledge base develops intellectual
  depth without extra effort.

WHAT BECOMES OF EACH CRITIQUE:
  The Assembler (Agent 6) takes each Critique and builds a separate FinalChunk:
    id         = "{original_chunk_id}_critique"     e.g. "km_jtbd_core_principle_001_critique"
    name       = "{original chunk name} — Critical Analysis"
    collection = same collection as the parent chunk
    chunk_type = "critique"
    content    = formatted text with [Limitations] + [Biases] + [Stress Tests] sections
    metadata   = { parent_id: "km_jtbd_core_principle_001" }

  This means when Friday retrieves "JTBD limitations" it gets the critique chunk
  directly. And when it retrieves "JTBD" it gets the core chunk with enrichment.
  Both are independently searchable.

ONE LLM CALL for all chunks — efficient, and lets the Critic see patterns
across all chunks to avoid repeating the same critique for related chunks.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
import json

from agents.pipeline.state import IngestionState, Critique, PipelineLogEntry
from agents.pipeline.utils import get_llm


# ── Structured output schema ──────────────────────────────────────────────────

class ChunkCritique(BaseModel):
    chunk_id: str = Field(description="Must exactly match one of the input chunk IDs")
    limitations: List[str] = Field(
        description="2-3 specific situations where this idea breaks down, doesn't apply, "
                    "or leads to wrong conclusions. Be concrete, not vague."
    )
    biases: List[str] = Field(
        description="2-3 biases embedded in this knowledge: source bias (who wrote it and why), "
                    "selection bias, Western/US-centric bias, recency bias, survivorship bias, etc."
    )
    stress_tests: List[str] = Field(
        description="2-3 edge cases or counterexamples. 'What if X?' scenarios that challenge "
                    "the chunk's central claim. Useful for stress-testing in consulting or MBA case work."
    )


class CriticOutput(BaseModel):
    critiques: List[ChunkCritique] = Field(
        description="One critique per input chunk. Must cover every chunk_id provided."
    )


SYSTEM_PROMPT = """You are the Critic in Friday's multi-agent knowledge ingestion pipeline.

Friday is a personal second brain for Sudheer — an MBA student / tech professional who uses
frameworks and knowledge in consulting, product, and strategy contexts.

YOUR JOB: Apply rigorous critical thinking to every knowledge chunk.
Act as a senior consultant who has seen frameworks fail in practice.

For each chunk, generate:

  LIMITATIONS — Where does this break down?
    - Under what conditions does this idea not apply?
    - What market contexts, company sizes, or industries is this irrelevant to?
    - When does following this advice lead to worse outcomes?
    Be specific. "Doesn't work in all cases" is useless. "Fails in regulated industries
    where switching costs are artificially low" is useful.

  BIASES — What's embedded in this knowledge?
    - Source bias: who wrote/said this, and what did they want to be true?
    - Selection bias: is this based on successful cases while ignoring failures?
    - Geographic/cultural bias: written from US/Silicon Valley lens?
    - Temporal bias: is this advice only valid for a specific era?
    - Survivorship bias: does this only look at outcomes, not attempts?

  STRESS TESTS — What challenges this?
    - A specific counterexample from industry or history
    - A "what if X?" scenario that breaks the central claim
    - The strongest argument a skeptic would make

IMPORTANT:
  - Use the EXACT chunk_id strings — do not modify them.
  - For personal/reflection chunks, critique should be self-reflective:
    "What assumptions is Sudheer making here?"
  - For framework chunks, critique should be practitioner-level:
    "When would a senior consultant advise AGAINST using this?"
  - Keep each point to 1-2 sentences. Quality over quantity.
  - If context_chunks are provided: mention when a limitation is especially relevant given what
    Friday already knows. E.g. "Given Friday already has a chunk on X, the key limitation here is Y."
  - You can also critique the proposed enrichments — if they're too generic or miss nuances,
    flag it so the Enricher Refiner can improve them."""


def run_critic(state: IngestionState) -> Dict[str, Any]:
    """
    Generates critical analysis for all chunks.
    Single LLM call covering all chunks together.

    READS FROM STATE:  raw_chunks, primary_topic, content_type, domains, enrichments, context_chunks
    WRITES TO STATE:   critiques, pipeline_log
    """
    raw_chunks = state["raw_chunks"]

    # Edge case: no chunks to critique
    if not raw_chunks:
        log_entry: PipelineLogEntry = {
            "stage":   "critic",
            "status":  "done",
            "summary": "No chunks to critique",
            "detail":  [],
        }
        return {
            "critiques":    [],
            "pipeline_log": state["pipeline_log"] + [log_entry],
        }

    llm = get_llm(temperature=0.3)  # some temperature — critique benefits from varied angles
    structured_llm = llm.with_structured_output(CriticOutput)

    # Send chunk content + metadata to the Critic — it needs content to critique
    # and name/domain/chunk_type to calibrate the right critical lens
    chunks_for_llm = [
        {
            "chunk_id":   c["id"],
            "name":       c["name"],
            "domain":     c["domain"],
            "chunk_type": c["chunk_type"],
            "content":    c["content"],
        }
        for c in raw_chunks
    ]

    # Include enrichments in the prompt so Critic can critique them too
    enrichment_lookup = {e["chunk_id"]: e for e in state.get("enrichments", [])}
    chunks_with_enrichments = []
    for c in chunks_for_llm:
        e = enrichment_lookup.get(c["chunk_id"], {})
        chunks_with_enrichments.append({
            **c,
            "proposed_enrichment": {
                "implications":        e.get("implications", []),
                "follow_up_questions": e.get("follow_up_questions", []),
                "use_cases":           e.get("use_cases", []),
            } if e else None,
        })

    context_section = ""
    if state.get("context_chunks"):
        context_lines = [
            f"  - [{c['name']}] ({c['collection']}): {c['content'][:150]}..."
            for c in state["context_chunks"][:4]
        ]
        context_section = "\nWhat Friday already knows about this topic:\n" + "\n".join(context_lines) + "\n"

    # content_type informs the critique lens:
    # "article" → challenge the author's argument; "personal_reflection" → challenge assumptions
    user_message = (
        f"Primary topic: {state['primary_topic']}\n"
        f"Content type: {state['content_type']}\n"
        f"Domains: {', '.join(state['domains'])}\n"
        f"{context_section}\n"
        f"Chunks to critique (with proposed enrichments):\n"
        f"{json.dumps(chunks_with_enrichments, indent=2)}"
    )

    result: CriticOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    # Check for missed chunks and warn in the log
    critique_ids = {c.chunk_id for c in result.critiques}
    missing = [c["id"] for c in raw_chunks if c["id"] not in critique_ids]

    critiques: List[Critique] = [
        {
            "chunk_id":     c.chunk_id,
            "limitations":  c.limitations,
            "biases":       c.biases,
            "stress_tests": c.stress_tests,
        }
        for c in result.critiques
    ]

    # Total critical points = sum of all limitations + biases + stress_tests across all chunks
    total_points = sum(
        len(c["limitations"]) + len(c["biases"]) + len(c["stress_tests"])
        for c in critiques
    )
    summary = f"Generated critique for {len(critiques)}/{len(raw_chunks)} chunks ({total_points} critical points total)"
    if missing:
        summary += f" (missed: {', '.join(missing)})"

    log_entry = {
        "stage":   "critic",
        "status":  "done",
        "summary": summary,
        "detail":  [
            {
                "chunk_id":           c["chunk_id"],
                "limitations_count":  len(c["limitations"]),
                "biases_count":       len(c["biases"]),
                "stress_tests_count": len(c["stress_tests"]),
            }
            for c in critiques
        ],
    }

    return {
        "critiques":    critiques,
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
