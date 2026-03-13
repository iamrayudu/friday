"""
Assembler Node
==============
POSITION: Agent 10 of 12

RECEIVES FROM STATE:
  raw_chunks        (List[RawChunk])        — from Chunker: the original concept units
  enrichments       (List[Enrichment])      — from Enricher Refiner: refined implications/questions/use_cases
  critiques         (List[Critique])        — from Critic: limitations/biases/stress_tests per chunk
  connection_map    (List[Connection])      — from Connector: related_ids from semantic search
  academic_analysis (List[AcademicAnalysis]) — from Academic Extractor: 0 or 1 item
  relationship_map  (List[RelationshipEntry]) — from Relationship Typer: typed relationships

ADDS TO STATE:
  final_chunks (List[FinalChunk]) — TWO or THREE FinalChunks per raw_chunk:
    1. Core chunk: enriched content + standard metadata + related_ids + relationship_types
    2. Critique companion chunk: critique text, id="{original_id}_critique", parent_id metadata
    3. Academic context chunk (optional): one per ingest if academic_analysis is non-empty

PASSES TO: Writer (Agent 11)
  Writer calls upsert() for every FinalChunk in final_chunks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL: HOW ONE RAW CHUNK BECOMES TWO FINAL CHUNKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  raw_chunk "km_saas_cac_payback_001"
       │
       │ content = "CAC payback period is the number of months..."
       │
       ├──────────────────────────────────────────────────────────────────────
       │  + enrichment["km_saas_cac_payback_001"]
       │      implications:        ["Short payback = reinvest faster", ...]
       │      use_cases:           ["Evaluating fundraise readiness", ...]
       │      follow_up_questions: ["How does blended CAC change payback?", ...]
       │
       │  + connection["km_saas_cac_payback_001"]
       │      related_ids: ["km_pmf_growth_metrics_001"]
       │
       ▼
  FinalChunk #1 — CORE (id = "km_saas_cac_payback_001")
       content  = "CAC payback period...
                   \n\n**Implications**\n- Short payback = reinvest faster\n...
                   \n\n**Use Cases**\n- Evaluating fundraise readiness\n...
                   \n\n**Follow-up Questions**\n- How does blended CAC...
                   "
       metadata = { name, domain, chunk_type, your_analysis,
                    source: "ingestion_pipeline",
                    related_ids: "km_pmf_growth_metrics_001" }  ← comma string

       │
       │  + critique["km_saas_cac_payback_001"]
       │      limitations:  ["Ignores blended CAC across channels", ...]
       │      biases:        ["Written from SaaS-VC perspective", ...]
       │      stress_tests:  ["What if payback fine but churn is 20%?", ...]
       │
       ▼
  FinalChunk #2 — CRITIQUE (id = "km_saas_cac_payback_001_critique")
       collection = "knowledge"  ← SAME as parent
       content    = "**Limitations**\n- Ignores blended CAC...\n...
                    \n\n**Biases**\n- Written from SaaS-VC perspective\n...
                    \n\n**Stress Tests**\n- What if payback fine but churn...\n..."
       metadata   = { name: "CAC Payback ... — Critical Analysis",
                      chunk_type: "critique",
                      parent_id: "km_saas_cac_payback_001" }  ← links to core

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY TWO CHUNKS, NOT ONE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Option A — store critique in metadata (JSON string):
    → Bad: ChromaDB metadata is not embedded. Semantic search can't find
      "limitations of JTBD" if the text is in metadata, not content.

  Option B — append critique to the core chunk content:
    → Bad: Every retrieval of the core concept also drags in the critique.
      You can't ask "What is JTBD?" without getting limitations every time.
      Also bloats the content, reducing embedding signal quality.

  Option C — separate chunk with parent_id (what we do here):
    → "What is JTBD?" retrieves km_jtbd_core_principle_001 — clean knowledge.
    → "What are the limitations of JTBD?" retrieves km_jtbd_core_principle_001_critique
      — the critique chunk surfaces directly by semantic match.
    → Both are in the same collection, independently searchable.
    → parent_id links them if Friday wants to show core + critique together.
    → This is exactly what the seed scripts did manually for early chunks
      (e.g. km_jtbd_stress_test_breaks, km_pmf_bias_flags). Now it's automatic.

NO LLM CALL — pure Python lookup and string construction.
"""

from collections import Counter
from typing import List, Dict, Any, Optional

from agents.pipeline.state import (
    IngestionState, RawChunk, Enrichment, Critique, Connection,
    FinalChunk, PipelineLogEntry,
)


def _find_enrichment(chunk_id: str, enrichments: List[Enrichment]) -> Optional[Enrichment]:
    for e in enrichments:
        if e["chunk_id"] == chunk_id:
            return e
    return None


def _find_critique(chunk_id: str, critiques: List[Critique]) -> Optional[Critique]:
    for c in critiques:
        if c["chunk_id"] == chunk_id:
            return c
    return None


def _find_connection(chunk_id: str, connection_map: List[Connection]) -> Optional[Connection]:
    for c in connection_map:
        if c["chunk_id"] == chunk_id:
            return c
    return None


def _build_enriched_content(chunk: RawChunk, enrichment: Optional[Enrichment]) -> str:
    """Append enrichment sections to the core chunk content."""
    content = chunk["content"]
    if not enrichment:
        return content

    sections = []

    if enrichment["implications"]:
        implications = "\n".join(f"- {i}" for i in enrichment["implications"])
        sections.append(f"\n\n**Implications**\n{implications}")

    if enrichment["use_cases"]:
        use_cases = "\n".join(f"- {u}" for u in enrichment["use_cases"])
        sections.append(f"\n\n**Use Cases**\n{use_cases}")

    if enrichment["follow_up_questions"]:
        questions = "\n".join(f"- {q}" for q in enrichment["follow_up_questions"])
        sections.append(f"\n\n**Follow-up Questions**\n{questions}")

    return content + "".join(sections)


def _build_critique_content(critique: Critique) -> Optional[str]:
    """Build the critique companion chunk content. Returns None if all lists are empty."""
    sections = []

    if critique["limitations"]:
        lims = "\n".join(f"- {l}" for l in critique["limitations"])
        sections.append(f"**Limitations**\n{lims}")

    if critique["biases"]:
        biases = "\n".join(f"- {b}" for b in critique["biases"])
        sections.append(f"**Biases**\n{biases}")

    if critique["stress_tests"]:
        tests = "\n".join(f"- {t}" for t in critique["stress_tests"])
        sections.append(f"**Stress Tests**\n{tests}")

    if not sections:
        return None

    return "\n\n".join(sections)


def run_assembler(state: IngestionState) -> Dict[str, Any]:
    """
    Assembles all agent outputs into FinalChunks ready for ChromaDB.
    Produces core chunks + critique companions + optional academic_context chunk.
    """
    raw_chunks        = state["raw_chunks"]
    enrichments       = state["enrichments"]
    critiques         = state["critiques"]
    connection_map    = state["connection_map"]

    final_chunks: List[FinalChunk] = []

    for chunk in raw_chunks:
        enrichment  = _find_enrichment(chunk["id"], enrichments)
        critique    = _find_critique(chunk["id"], critiques)
        connection  = _find_connection(chunk["id"], connection_map)

        # ── Build core chunk ──────────────────────────────────────────
        enriched_content = _build_enriched_content(chunk, enrichment)

        related_ids_str = (
            ",".join(connection["related_ids"]) if connection and connection["related_ids"] else ""
        )

        # Build relationship_types string from relationship_map
        relationship_entries = [
            r for r in state.get("relationship_map", [])
            if r["chunk_id"] == chunk["id"]
        ]
        relationship_types_str = ",".join(
            f"{r['relationship_type']}:{r['related_id']}"
            for r in relationship_entries
        ) if relationship_entries else ""

        core_metadata: Dict[str, Any] = {
            "name":               chunk["name"],
            "domain":             chunk["domain"],
            "chunk_type":         chunk["chunk_type"],
            "your_analysis":      str(chunk["your_analysis"]),  # ChromaDB needs strings
            "source":             "ingestion_pipeline",
            "related_ids":        related_ids_str,
            "relationship_types": relationship_types_str,
        }

        final_chunks.append({
            "id":            chunk["id"],
            "name":          chunk["name"],
            "collection":    chunk["collection"],
            "domain":        chunk["domain"],
            "chunk_type":    chunk["chunk_type"],
            "your_analysis": chunk["your_analysis"],
            "content":       enriched_content,
            "metadata":      core_metadata,
        })

        # ── Build critique companion chunk ───────────────────────────
        if critique:
            critique_content = _build_critique_content(critique)
            if critique_content:
                critique_metadata: Dict[str, Any] = {
                    "name":          chunk["name"] + " — Critical Analysis",
                    "domain":        chunk["domain"],
                    "chunk_type":    "critique",
                    "your_analysis": "False",
                    "source":        "ingestion_pipeline",
                    "parent_id":     chunk["id"],  # link back to the core chunk
                }

                final_chunks.append({
                    "id":            chunk["id"] + "_critique",
                    "name":          chunk["name"] + " — Critical Analysis",
                    "collection":    chunk["collection"],  # same collection as parent
                    "domain":        chunk["domain"],
                    "chunk_type":    "critique",
                    "your_analysis": False,
                    "content":       critique_content,
                    "metadata":      critique_metadata,
                })

    # ── Build academic context chunk (if academic analysis was produced) ──────
    academic_analysis_list = state.get("academic_analysis", [])
    if academic_analysis_list:
        aa = academic_analysis_list[0]

        # Build formatted content
        sections = []
        if aa["key_claims"]:
            claims = "\n".join(f"- {c}" for c in aa["key_claims"])
            sections.append(f"**Key Claims**\n{claims}")
        if aa["key_authors"]:
            authors = "\n".join(f"- {a}" for a in aa["key_authors"])
            sections.append(f"**Key Authors & Thinkers**\n{authors}")
        if aa["key_theories"]:
            theories = "\n".join(f"- {t}" for t in aa["key_theories"])
            sections.append(f"**Theories & Frameworks Referenced**\n{theories}")
        if aa["research_approach"]:
            sections.append(f"**Research Approach**\n{aa['research_approach']}")
        if aa["debate_position"]:
            sections.append(f"**Debate Position**\n{aa['debate_position']}")
        if aa["intellectual_context"]:
            sections.append(f"**Intellectual Context**\n{aa['intellectual_context']}")

        if sections:
            academic_content = "\n\n".join(sections)

            # Determine dominant collection from raw_chunks
            collection_counts = Counter(c["collection"] for c in raw_chunks)
            dominant_collection = collection_counts.most_common(1)[0][0] if collection_counts else "knowledge"

            # Slug the primary_topic for the ID
            topic_slug = state["primary_topic"].lower().replace(" ", "_").replace("/", "_")[:40]
            academic_id = f"ak_{topic_slug}_academic_context"

            academic_metadata: Dict[str, Any] = {
                "name":              f"{state['primary_topic']} — Academic Context",
                "domain":            state["domains"][0] if state["domains"] else "general",
                "chunk_type":        "academic_context",
                "your_analysis":     "False",
                "source":            "ingestion_pipeline",
                "research_approach": aa["research_approach"],
            }

            final_chunks.append({
                "id":            academic_id,
                "name":          f"{state['primary_topic']} — Academic Context",
                "collection":    dominant_collection,
                "domain":        state["domains"][0] if state["domains"] else "general",
                "chunk_type":    "academic_context",
                "your_analysis": False,
                "content":       academic_content,
                "metadata":      academic_metadata,
            })

    core_count     = len(raw_chunks)
    critique_count = sum(1 for c in final_chunks if c["chunk_type"] == "critique")
    academic_count = sum(1 for c in final_chunks if c["chunk_type"] == "academic_context")
    summary = (
        f"Assembled {core_count} core + {critique_count} critique"
        f" + {academic_count} academic_context = {len(final_chunks)} total chunks"
    )

    log_entry: PipelineLogEntry = {
        "stage":   "assembler",
        "status":  "done",
        "summary": summary,
        "detail":  None,
    }

    return {
        "final_chunks": final_chunks,
        "pipeline_log": state["pipeline_log"] + [log_entry],
    }
