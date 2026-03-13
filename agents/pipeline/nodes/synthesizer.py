"""
Synthesizer Node
================
POSITION: Agent 12 of 12

RECEIVES FROM STATE (reads everything — the only agent with full context):
  primary_topic   (str)            — from Classifier: e.g. "SaaS unit economics"
  content_type    (str)            — from Classifier: e.g. "article"
  domains         (List[str])      — from Classifier: e.g. ["finance", "strategy"]
  is_own_writing  (bool)           — from Classifier: True if Sudheer wrote this
  raw_chunks      (List[RawChunk]) — from Chunker: original concept units
  final_chunks    (List[FinalChunk])— from Assembler: core + critique pairs
  connection_map  (List[Connection])— from Connector: related_ids per chunk
  write_log       (List[Dict])     — from Writer: success/error per chunk

ADDS TO STATE:
  summary (str) — 2-3 sentence synthesis shown in the Teach tab results panel.
    Answers: "What did I just teach Friday, and why does it matter?"

PASSES TO: END
  The /ingest FastAPI endpoint reads state["summary"] and returns it to the UI.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT (assembled pipeline_summary dict sent to Gemini):
    {
      "primary_topic":      "SaaS unit economics",
      "content_type":       "article",
      "domains":            ["finance", "strategy"],
      "is_own_writing":     False,
      "chunks_created":     5,
      "final_chunks_total": 10,   ← 5 core + 5 critique companions
      "critique_chunks":    5,
      "connections_found":  3,
      "chunk_names": [
        "CAC Payback Period Mechanics",
        "LTV:CAC Ratio Benchmarks",
        "Net Revenue Retention Definition",
        "Magic Number for SaaS Efficiency",
        "Burn Multiple and Capital Efficiency"
      ],
      "write_log_ok": 10
    }

  OUTPUT SUMMARY (shown in Teach tab):
    "Added 5 foundational concepts on SaaS unit economics — covering CAC payback,
     LTV:CAC, NRR, and capital efficiency — with critical limitations and biases
     generated for each. Connected to 3 existing chunks in your knowledge base,
     including your earlier PMF and growth metrics notes."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS NODE IS LAST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  The Synthesizer needs data from every prior agent to write a meaningful summary:
    - Classifier: what was the topic? (primary_topic, content_type)
    - Chunker:    what concepts were found? (chunk_names)
    - Enricher:   (implicitly, through final_chunks length)
    - Critic:     how many critique companions were made? (final_chunks - raw_chunks)
    - Connector:  how many connections to existing knowledge? (connection_map)
    - Assembler:  how many total chunks? (final_chunks_total)
    - Writer:     did everything write successfully? (write_log_ok)

  Running it earlier would give it incomplete information.
  Running it last gives it the full picture to write a truly informed summary.

  The summary answers Sudheer's implicit question every time he clicks
  "Teach Friday": "What did you just learn, and how does it fit with what
  you already know?"

temperature=0.2 — allows natural language fluency while staying grounded in facts.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
import json

from agents.pipeline.state import IngestionState, PipelineLogEntry
from agents.pipeline.utils import get_llm


# ── Structured output schema ──────────────────────────────────────────────────

class SynthesizerOutput(BaseModel):
    summary: str = Field(
        description="2-3 sentence synthesis. Cover: (1) what the primary topic was and "
                    "what was learned, (2) any notable connections to existing knowledge, "
                    "(3) one insight about how this fits into Sudheer's broader knowledge base."
    )


SYSTEM_PROMPT = """You are the Synthesizer — the final agent in Friday's knowledge ingestion pipeline.

Friday is a personal second brain for Sudheer — an MBA student / tech professional.

YOUR JOB: Write a concise summary of what was just ingested and why it matters.

Your summary will be shown in the UI so Sudheer can quickly understand what was stored.
It should be insightful, not just descriptive. Don't say "5 chunks were created."
Say what was learned and why it's valuable for his knowledge base.

Write like a knowledgeable advisor who has just read this content and is briefing Sudheer.
2-3 sentences max."""


def run_synthesizer(state: IngestionState) -> Dict[str, Any]:
    """
    Generates a final synthesis summary of the ingestion run.
    Has full access to all pipeline outputs to craft an informed summary.
    """
    llm = get_llm(temperature=0.2)
    structured_llm = llm.with_structured_output(SynthesizerOutput)

    # Give the synthesizer a structured view of everything that happened
    pipeline_summary = {
        "primary_topic":      state["primary_topic"],
        "content_type":       state["content_type"],
        "domains":            state["domains"],
        "is_own_writing":     state["is_own_writing"],
        "chunks_created":     len(state["raw_chunks"]),
        "final_chunks_total": len(state["final_chunks"]),
        "critique_chunks":    len(state["final_chunks"]) - len(state["raw_chunks"]),
        "connections_found":  sum(len(c["related_ids"]) for c in state["connection_map"]),
        "chunk_names":        [c["name"] for c in state["raw_chunks"]],
        "write_log_ok":       sum(1 for w in state["write_log"] if w["status"] == "ok"),
    }

    user_message = (
        f"Here is what was just ingested into Friday's knowledge base:\n\n"
        f"{json.dumps(pipeline_summary, indent=2)}\n\n"
        f"Write a 2-3 sentence synthesis for Sudheer."
    )

    result: SynthesizerOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    log_entry: PipelineLogEntry = {
        "stage":   "synthesizer",
        "status":  "done",
        "summary": "Generated synthesis summary",
        "detail":  None,
    }

    return {
        "summary":      result.summary,
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
