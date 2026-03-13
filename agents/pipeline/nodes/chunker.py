"""
Chunker Node
============
POSITION: Agent 3 of 12

RECEIVES FROM STATE:
  raw_content    (str)       — the full original text (never modified)
  hint           (str)       — optional user context
  content_type   (str)       — from Classifier: "article" | "notes" | "framework_ref" | etc.
  domains        (List[str]) — from Classifier: ["finance", "strategy", ...]
  is_own_writing (bool)      — from Classifier: True if Sudheer wrote this himself
  primary_topic  (str)       — from Classifier: e.g. "SaaS unit economics"

ADDS TO STATE:
  raw_chunks (List[RawChunk]) — each chunk is one standalone concept with:
    id            (str)  — unique snake_case ID with km_/fw_/pk_ prefix
    name          (str)  — 3-7 word human-readable label
    collection    (str)  — "knowledge" | "frameworks" | "personal"
    domain        (str)  — primary domain for this specific chunk
    chunk_type    (str)  — principle | framework | experience | analysis | etc.
    your_analysis (bool) — True if this is Sudheer's own writing
    content       (str)  — self-contained chunk text (no surrounding context needed)

PASSES TO: Enricher (Agent 3) AND Critic (Agent 4)
  Both agents receive raw_chunks directly from state. The Enricher adds depth
  to each chunk (implications, questions, use cases). The Critic challenges
  each chunk independently (limitations, biases, stress tests). Neither modifies
  raw_chunks — they only add their own outputs to new state keys.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT (from state, after Classifier ran):
    raw_content  = "SaaS businesses live and die by their unit economics.
                    CAC payback tells you how many months of revenue it takes
                    to recoup the cost of acquiring a customer. LTV:CAC ratio
                    above 3:1 is the benchmark for healthy growth. Net Revenue
                    Retention above 100% means expansion revenue outpaces churn..."
    content_type = "article"
    domains      = ["finance", "strategy"]
    primary_topic = "SaaS unit economics"

  ONE RAW CHUNK OUTPUT (example):
    {
      "id":            "km_saas_cac_payback_001",
      "name":          "CAC Payback Period Mechanics",
      "collection":    "knowledge",
      "domain":        "finance",
      "chunk_type":    "principle",
      "your_analysis": False,
      "content":       "CAC payback period is the number of months of gross-margin
                        revenue needed to recoup the customer acquisition cost. A
                        payback < 12 months means you can reinvest profits quickly.
                        Payback > 18 months signals high risk at scale because you
                        need significant upfront capital to fund growth."
    }

  A 1500-word SaaS article typically yields 4-6 raw_chunks total.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS NODE EXISTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ChromaDB retrieval is concept-level, not document-level. When Friday answers
  a question, it retrieves the 3-4 most semantically relevant chunks — not
  whole documents. If a 2000-word article was stored as one blob, retrieval
  would return the whole thing for every vaguely related question, overwhelming
  the LLM with irrelevant text and diluting the useful signal.

  By splitting into one-concept-per-chunk, each chunk is independently
  retrievable. A question about "CAC payback" retrieves exactly that chunk, not
  the whole article. A question about "LTV:CAC" retrieves a different chunk.
  The granularity of the knowledge base determines the precision of retrieval.

COLLECTION ROUTING RULES:
  "knowledge"  — things LEARNED: principles, how things work, limitations,
                 comparisons, case breakdowns. Any domain: MBA, tech, finance.
  "frameworks" — tools USED: step-by-step processes, reusable methodologies,
                 templates, mental models.
  "personal"   — WHO Sudheer is: background, experience from roles, lessons,
                 his own original analysis/opinions.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from agents.pipeline.state import IngestionState, RawChunk, PipelineLogEntry
from agents.pipeline.utils import get_llm


# ── Structured output schema ──────────────────────────────────────────────────

class ChunkSchema(BaseModel):
    id: str = Field(
        description="Unique snake_case ID. Prefix: km_ (knowledge), fw_ (frameworks), pk_ (personal). "
                    "Format: prefix_short_descriptor_001. E.g. km_saas_unit_economics_001"
    )
    name: str = Field(description="Human-readable name, 3-7 words")
    collection: str = Field(
        description="'knowledge' for learned concepts, 'frameworks' for reusable tools/processes, "
                    "'personal' for background or own analysis"
    )
    domain: str = Field(
        description="Primary domain: mba | tech | product | finance | strategy | marketing | "
                    "operations | consulting | engineering | personal | general"
    )
    chunk_type: str = Field(
        description="What kind of chunk: principle | framework | experience | analysis | "
                    "limitation | comparison | application | case_study | mental_model | lesson | background"
    )
    your_analysis: bool = Field(
        description="True if this is Sudheer's own opinion, analysis, or experience. "
                    "False if it's sourced or learned knowledge."
    )
    content: str = Field(
        description="Full self-contained text. Must make sense without any surrounding context."
    )


class ChunkerOutput(BaseModel):
    chunks: List[ChunkSchema]


SYSTEM_PROMPT = """You are the Chunker in Friday's multi-agent knowledge ingestion pipeline.

Friday is a personal second brain for Sudheer — an MBA student / tech professional.

YOUR JOB: Split the content into retrievable knowledge chunks.

COLLECTION RULES:
  "knowledge"  — things LEARNED: principles, how things work, limitations, comparisons,
                 case breakdowns. Any domain.
  "frameworks" — tools USED: step-by-step processes, reusable methodologies, templates,
                 mental models.
  "personal"   — WHO Sudheer is: his background, experience from roles, lessons learned,
                 his own original analysis/opinions.

CHUNKING RULES:
  1. One chunk = one standalone concept. Must make complete sense independently.
  2. Do NOT split a single idea across two chunks.
  3. Do NOT merge two distinct ideas into one chunk.
  4. 3-8 chunks per content piece is typical. Short notes may yield 2.
  5. Skip filler, repetition, preamble — only chunk what's worth retrieving later.
  6. Content written in first person ("I think...", "In my experience...") → collection: "personal", your_analysis: true

ID FORMAT:
  km_descriptor_001 for knowledge chunks
  fw_descriptor_001 for framework chunks
  pk_descriptor_001 for personal chunks
  Make IDs specific: "km_jtbd_vs_personas_001" not "km_chunk_001"

You have been given the content_type and domains from the Classifier agent.
Use this context to inform how you chunk:
  - 'personal_reflection' → likely personal collection, your_analysis: true
  - 'framework_ref' → likely frameworks collection
  - 'notes' → may yield fewer, denser chunks than a full article"""


def run_chunker(state: IngestionState) -> Dict[str, Any]:
    """
    Chunks the content into raw knowledge units.
    Uses classifier context to inform collection routing and chunk strategy.

    READS FROM STATE:  raw_content, hint, content_type, domains, is_own_writing, primary_topic
    WRITES TO STATE:   raw_chunks, pipeline_log
    """
    llm = get_llm(temperature=0.1)  # low temperature — chunking should be consistent
    structured_llm = llm.with_structured_output(ChunkerOutput)

    # Build context from classifier for the LLM
    # This tells the Chunker exactly what the Classifier determined — prevents re-inference
    context = (
        f"Content type: {state['content_type']}\n"
        f"Domains: {', '.join(state['domains'])}\n"
        f"Primary topic: {state['primary_topic']}\n"
        f"Is Sudheer's own writing: {state['is_own_writing']}\n"
    )
    if state["hint"]:
        context += f"User hint: {state['hint']}\n"

    user_message = f"{context}\n---\n\n{state['raw_content']}"

    result: ChunkerOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    # Convert Pydantic models to TypedDicts for state storage
    raw_chunks: List[RawChunk] = [
        {
            "id":            c.id,
            "name":          c.name,
            "collection":    c.collection,
            "domain":        c.domain,
            "chunk_type":    c.chunk_type,
            "your_analysis": c.your_analysis,
            "content":       c.content,
        }
        for c in result.chunks
    ]

    # Count by collection for the log summary
    counts: Dict[str, int] = {}
    for c in raw_chunks:
        counts[c["collection"]] = counts.get(c["collection"], 0) + 1
    counts_str = ", ".join(f"{col}: {n}" for col, n in counts.items())

    log_entry: PipelineLogEntry = {
        "stage":   "chunker",
        "status":  "done",
        "summary": f"Produced {len(raw_chunks)} raw chunks ({counts_str})",
        # detail shows id/name/collection for each chunk — useful for debugging routing
        "detail":  [{"id": c["id"], "name": c["name"], "collection": c["collection"]} for c in raw_chunks],
    }

    return {
        "raw_chunks":   raw_chunks,
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
