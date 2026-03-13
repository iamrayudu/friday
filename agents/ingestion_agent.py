"""
Friday Ingestion Agent
=======================
Entry point for the Teach Friday feature. Thin wrapper over the multi-agent pipeline.

WHAT THIS FILE DOES:
  Receives raw content + hint from main.py → POST /ingest
  Initializes the pipeline state with all required keys
  Calls the compiled LangGraph pipeline (agents/pipeline/graph.py)
  Returns a response dict that main.py sends to the browser

THE PIPELINE (agents/pipeline/):
  12 specialized agents run in sequence, each with a distinct role:

   1. Classifier          — identifies content_type, domains, is_own_writing, quality_signal
   2. Context Loader      — loads existing related chunks from ChromaDB (no LLM)
   3. Chunker             — splits content into concept-level chunks, routes to collection
   4. Enricher            — first-pass: implications, use cases, follow-up questions per chunk
   5. Critic              — limitations, biases, stress tests (challenges Enricher's output too)
   6. Enricher Refiner    — refines enrichments using Critic's analysis (3-turn dialogue)
   7. Academic Extractor  — extracts key claims, authors, theories, debate position
   8. Connector           — finds connections to existing ChromaDB knowledge (no LLM)
   9. Relationship Typer  — classifies HOW new chunks relate to existing (BUILDS_ON, EXTENDS, etc.)
  10. Assembler           — merges all outputs; creates core + critique + academic_context chunks
  11. Writer              — upserts all final chunks to ChromaDB (knowledge/frameworks/personal)
  12. Synthesizer         — writes the summary shown in the Teach tab UI

RETURN CONTRACT (unchanged from original — main.py depends on this):
  {
    "summary":      str,         ← what was stored, shown in UI
    "chunks":       List[dict],  ← [{id, name, collection, domain, chunk_type, your_analysis}]
    "counts":       dict,        ← {"knowledge": N, "frameworks": N, "personal": N}
    "pipeline_log": List[dict],  ← NEW: [{stage, status, summary, detail}] for UI pipeline trace
  }

NOTE ON IMPORT:
  PIPELINE is imported lazily inside process() to avoid circular import
  issues during FastAPI startup (main.py → ingestion_agent → pipeline.graph → nodes → store).

CHANGELOG:
- 2026-03-12 | created: single-pass Gemini structured output
- 2026-03-12 | replaced: multi-agent LangGraph pipeline (8 specialized agents)
- 2026-03-12 | upgraded: 12-agent pipeline with context_loader, enricher_refiner,
               academic_extractor, relationship_typer; agents now "talk to each other"
"""

from typing import List, Dict, Any

from agents.pipeline.state import IngestionState


def process(content: str, hint: str = "") -> Dict[str, Any]:
    """
    Run the full ingestion pipeline on raw content.

    Args:
        content: raw text to ingest — article, notes, analysis, anything
        hint: optional context that helps agents classify correctly
              e.g. "this is my own analysis of unit economics for SaaS"

    Returns:
        {summary, chunks, counts, pipeline_log}
    """
    # Lazy import — avoids circular import at startup
    from agents.pipeline.graph import PIPELINE

    # Initialize ALL state keys — LangGraph requires every TypedDict key present
    initial_state: IngestionState = {
        "raw_content":    content,
        "hint":           hint,
        # classifier (will be filled by Agent 1)
        "content_type":   "",
        "domains":        [],
        "is_own_writing": False,
        "primary_topic":  "",
        "quality_signal": "high",
        # context_loader (will be filled by Agent 2)
        "context_chunks":    [],
        # chunker (will be filled by Agent 3)
        "raw_chunks":     [],
        # enricher (will be filled by Agent 4, then overwritten by Agent 6)
        "enrichments":    [],
        # critic (will be filled by Agent 5)
        "critiques":      [],
        # academic_extractor (will be filled by Agent 7)
        "academic_analysis": [],
        # connector (will be filled by Agent 8)
        "connection_map": [],
        # relationship_typer (will be filled by Agent 9)
        "relationship_map": [],
        # assembler (will be filled by Agent 10)
        "final_chunks":   [],
        # writer (will be filled by Agent 11)
        "write_log":      [],
        # synthesizer (will be filled by Agent 12)
        "summary":        "",
        # pipeline trace (accumulated across all 12 agents)
        "pipeline_log":   [],
    }

    result = PIPELINE.invoke(initial_state)

    # ── Build response ────────────────────────────────────────────────────────

    # Chunks list for UI — core + critique companions
    chunks_out: List[Dict[str, Any]] = [
        {
            "id":            fc["id"],
            "name":          fc["name"],
            "collection":    fc["collection"],
            "domain":        fc["domain"],
            "chunk_type":    fc["chunk_type"],
            "your_analysis": fc["your_analysis"],
        }
        for fc in result["final_chunks"]
    ]

    # Count stored chunks by collection
    counts: Dict[str, int] = {"knowledge": 0, "frameworks": 0, "personal": 0}
    for w in result["write_log"]:
        if w["status"] == "ok":
            col = w["collection"]
            counts[col] = counts.get(col, 0) + 1

    return {
        "summary":      result["summary"],
        "chunks":       chunks_out,
        "counts":       counts,
        "pipeline_log": result["pipeline_log"],
    }
