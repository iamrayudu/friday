"""
Ingestion Pipeline State
========================
The shared TypedDict that flows through every node in the LangGraph pipeline.
Each node reads only what it needs and writes only its own output keys.
No node overwrites a sibling node's keys.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL PIPELINE DATA FLOW DIAGRAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT (from /ingest POST request):
    raw_content  — the full text the user pasted (article, notes, analysis, etc.)
    hint         — optional context the user typed ("this is my own MBA analysis")

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 1: CLASSIFIER]                                          │
  │  Reads:  raw_content, hint                                      │
  │  Writes: content_type, domains, is_own_writing,                 │
  │          primary_topic, quality_signal                          │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  content_type    = "article"
  domains         = ["finance", "strategy"]
  is_own_writing  = False
  primary_topic   = "SaaS unit economics"
  quality_signal  = "high"

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 2: CONTEXT LOADER]                                      │
  │  Reads:  primary_topic, domains                                 │
  │  Writes: context_chunks (List[ContextChunk])                    │
  │  Method: vector search against existing ChromaDB                │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  context_chunks = [
    { id: "km_pmf_growth_metrics_001", name: "PMF Growth Metrics",
      collection: "knowledge", content: "Product-market fit...", score: 0.81 },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 3: CHUNKER]                                             │
  │  Reads:  raw_content, hint, content_type, domains,             │
  │          is_own_writing, primary_topic, context_chunks          │
  │  Writes: raw_chunks (List[RawChunk])                            │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  raw_chunks = [
    { id: "km_saas_cac_payback_001",
      name: "CAC Payback Period Mechanics",
      collection: "knowledge",
      domain: "finance",
      chunk_type: "principle",
      your_analysis: False,
      content: "CAC payback period is the number of months..." },
    { id: "km_saas_ltv_cac_ratio_001", ... },
    ...
  ]

        ↓  (raw_chunks flow into agents in sequence)
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 4: ENRICHER]                                            │
  │  Reads:  raw_chunks, primary_topic, domains, context_chunks     │
  │  Writes: enrichments (List[Enrichment]) — one per chunk         │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  enrichments = [
    { chunk_id: "km_saas_cac_payback_001",
      implications: ["Short payback = reinvest faster", ...],
      follow_up_questions: ["How does payback change at scale?", ...],
      use_cases: ["Evaluating SaaS fundraise readiness", ...] },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 5: CRITIC]                                              │
  │  Reads:  raw_chunks, primary_topic, content_type, enrichments,  │
  │          context_chunks                                         │
  │  Writes: critiques (List[Critique]) — one per chunk             │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  critiques = [
    { chunk_id: "km_saas_cac_payback_001",
      limitations: ["Ignores blended CAC from multiple channels", ...],
      biases: ["Written from SaaS-VC growth model perspective", ...],
      stress_tests: ["What if payback is fine but churn is high?", ...] },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 6: ENRICHER REFINER]                                    │
  │  Reads:  raw_chunks, enrichments, critiques, context_chunks,    │
  │          primary_topic, domains                                 │
  │  Writes: enrichments (List[Enrichment]) — REPLACES initial      │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  enrichments = [refined, critique-aware version of enrichments]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 7: ACADEMIC EXTRACTOR]                                  │
  │  Reads:  raw_content, primary_topic, content_type, domains,     │
  │          raw_chunks                                             │
  │  Writes: academic_analysis (List[AcademicAnalysis]) — 0 or 1   │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  academic_analysis = [{ key_claims: [...], key_authors: [...],
                         key_theories: [...], research_approach: "practitioner",
                         debate_position: "...", intellectual_context: "..." }]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 8: CONNECTOR]                                           │
  │  Reads:  raw_chunks, primary_topic, domains                     │
  │  Writes: connection_map (List[Connection]) — one per chunk      │
  │  Method: semantic vector search against existing ChromaDB       │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  connection_map = [
    { chunk_id: "km_saas_cac_payback_001",
      related_ids: ["km_pmf_growth_metrics_001", "km_jtbd_retention_001"],
      relationship_notes: "km_pmf_growth_metrics_001 (score: 0.81, collection: knowledge)" },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 9: RELATIONSHIP TYPER]                                  │
  │  Reads:  raw_chunks, connection_map                             │
  │  Writes: relationship_map (List[RelationshipEntry])             │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  relationship_map = [
    { chunk_id: "km_saas_cac_payback_001",
      related_id: "km_pmf_growth_metrics_001",
      relationship_type: "BUILDS_ON",
      explanation: "CAC payback assumes a working PMF..." },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 10: ASSEMBLER]                                          │
  │  Reads:  raw_chunks, enrichments, critiques, connection_map,    │
  │          academic_analysis, relationship_map                    │
  │  Writes: final_chunks (List[FinalChunk])                        │
  │  Logic:  each raw_chunk → TWO FinalChunks (core + critique)     │
  │          + optional academic_context chunk                      │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  final_chunks = [
    { id: "km_saas_cac_payback_001",       (core chunk, enriched)  },
    { id: "km_saas_cac_payback_001_critique", (companion, critique text) },
    { id: "ak_saas_unit_economics_academic_context", (academic context) },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 11: WRITER]                                             │
  │  Reads:  final_chunks                                           │
  │  Writes: write_log (List[Dict]) — one entry per chunk written   │
  │  Method: upsert() into ChromaDB — safe to run twice             │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  write_log = [
    { id: "km_saas_cac_payback_001",           collection: "knowledge", status: "ok" },
    { id: "km_saas_cac_payback_001_critique",   collection: "knowledge", status: "ok" },
    ...
  ]

        ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  [Agent 12: SYNTHESIZER]                                        │
  │  Reads:  primary_topic, content_type, domains, raw_chunks,      │
  │          final_chunks, connection_map, write_log                │
  │  Writes: summary (str) — shown in the Teach tab UI              │
  └─────────────────────────────────────────────────────────────────┘
        ↓
  summary = "Added 5 foundational concepts on SaaS unit economics with their
             critical limitations, connecting to 3 existing PMF and JTBD chunks
             already in your database."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PIPELINE_LOG PATTERN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  pipeline_log is accumulated across nodes. LangGraph replaces list fields
  by default (not appends). So each node must:
    1. Read state["pipeline_log"]
    2. Build a new PipelineLogEntry
    3. Return {"pipeline_log": existing_log + [new_entry]}
  This explicit concat avoids the operator.add annotation complexity.
"""

from typing import TypedDict, List, Dict, Any


# ── Intermediate types ────────────────────────────────────────────────────────

class RawChunk(TypedDict):
    """
    One concept chunk produced by the Chunker (Agent 2).
    Contains the raw, un-enriched content straight from the LLM's chunking pass.

    FILLED BY: Chunker
    READ BY:   Enricher (for depth), Critic (for critique), Connector (for search),
               Assembler (as the base for FinalChunks)
    """
    id: str               # km_ / fw_ / pk_ prefixed snake_case unique ID
    name: str             # 3-7 word human-readable label
    collection: str       # "knowledge" | "frameworks" | "personal"
    domain: str           # mba | tech | product | finance | strategy | ...
    chunk_type: str       # principle | framework | experience | analysis | ...
    your_analysis: bool   # True = Sudheer's own writing, not sourced
    content: str          # self-contained chunk text — must make sense alone


class Enrichment(TypedDict):
    """
    Enrichment data added to one raw chunk by the Enricher (Agent 3).
    Turns a flat fact into layered knowledge with depth and forward-looking context.

    FILLED BY: Enricher
    READ BY:   Assembler — appends these sections to the core FinalChunk content
    """
    chunk_id: str
    implications: List[str]        # 2-3 second-order consequences of this idea
    follow_up_questions: List[str] # 2-3 questions this chunk raises for further research
    use_cases: List[str]           # 2-3 concrete application scenarios


class Critique(TypedDict):
    """
    Critical analysis added to one raw chunk by the Critic (Agent 4).
    Challenges the chunk's central claims and exposes when/where they break down.

    FILLED BY: Critic
    READ BY:   Assembler — turns this into a separate "_critique" companion FinalChunk
    """
    chunk_id: str
    limitations: List[str]   # where/when this idea breaks down or doesn't apply
    biases: List[str]        # source, perspective, geographic, temporal biases
    stress_tests: List[str]  # edge cases and counterexamples that challenge the idea


class Connection(TypedDict):
    """
    Links between a new chunk and existing ChromaDB chunks, found by the Connector (Agent 5).
    Built using vector similarity search — no LLM involved.

    FILLED BY: Connector (semantic search against existing ChromaDB)
    READ BY:   Assembler — writes related_ids as comma-separated string in FinalChunk metadata
    """
    chunk_id: str
    related_ids: List[str]   # IDs of existing chunks that relate to this one
    relationship_notes: str  # brief description of how they connect (score, collection)


class FinalChunk(TypedDict):
    """
    A fully assembled chunk ready for ChromaDB storage, produced by the Assembler (Agent 6).

    Each raw chunk produces TWO FinalChunks:
      1. Core chunk:
           id       = original chunk id (e.g. "km_saas_cac_payback_001")
           content  = original text + [Implications] + [Use Cases] + [Follow-up Questions]
           metadata = standard fields + related_ids from connection_map

      2. Critique companion chunk:
           id         = original id + "_critique" (e.g. "km_saas_cac_payback_001_critique")
           content    = [Limitations] + [Biases] + [Stress Tests] from Critic
           chunk_type = "critique"
           metadata   = parent_id pointing back to the core chunk

    FILLED BY: Assembler
    READ BY:   Writer — calls upsert() for each FinalChunk into ChromaDB
    """
    id: str
    name: str
    collection: str
    domain: str
    chunk_type: str       # "critique" for companion chunks; original type for core chunks
    your_analysis: bool
    content: str          # enriched for core; critique text for companion
    metadata: Dict[str, Any]  # full metadata dict ready for store.upsert()


class PipelineLogEntry(TypedDict):
    """
    One entry in the pipeline trace. Accumulated by every node across the full run.
    Displayed in the Teach tab UI to show progress of the pipeline.

    FILLED BY: every node (each appends one entry to pipeline_log)
    READ BY:   UI rendering in the Teach tab results panel
    """
    stage: str    # node name: "classifier", "chunker", etc.
    status: str   # "done" | "error"
    summary: str  # 1-sentence description of what happened
    detail: Any   # the node's primary output (shown in UI on expand)


class ContextChunk(TypedDict):
    """
    An existing chunk from ChromaDB, loaded before processing begins.
    Gives all downstream agents awareness of what Friday already knows.

    FILLED BY: context_loader (Agent 2)
    READ BY:   chunker (avoids re-chunking existing concepts),
               enricher (non-redundant implications),
               critic (comparative critique — how does new knowledge relate?),
               enricher_refiner (distinguishes new insight from known insight)
    """
    id: str
    name: str
    collection: str
    content: str    # truncated to 400 chars max
    score: float    # cosine similarity score (0-1) — how related to current topic


class AcademicAnalysis(TypedDict):
    """
    Academic/intellectual structure extracted from the content by the Academic Extractor (Agent 7).
    Only populated for article/notes/case_study/personal_reflection content types.
    Empty list in state for non-academic content.

    FILLED BY: academic_extractor (Agent 7)
    READ BY:   assembler — turns this into an "academic_context" FinalChunk
    """
    key_claims: List[str]           # 3-5 central arguments or findings
    key_authors: List[str]          # scholars/practitioners referenced and what they're known for
    key_theories: List[str]         # named theories, frameworks, models cited
    research_approach: str          # empirical | theoretical | case-study | practitioner | synthesis | opinion
    debate_position: str            # what intellectual debate is this participating in?
    intellectual_context: str       # what field/tradition does this build on?


class RelationshipEntry(TypedDict):
    """
    A classified relationship between a new chunk and an existing related chunk.
    Produced by the Relationship Typer (Agent 9) after Connector finds related IDs.

    Relationship types:
      BUILDS_ON   — new chunk extends/deepens the existing; knowing existing enriches new
      EXTENDS     — new chunk adds a dimension not covered by existing
      APPLIES     — new chunk demonstrates how to use existing framework in specific context
      CONTRADICTS — new chunk challenges the existing chunk's central claim
      PARALLELS   — both address the same question from different angles
      EXEMPLIFIES — new chunk is a concrete case/instance of existing general principle

    FILLED BY: relationship_typer (Agent 9)
    READ BY:   assembler — stores relationship_type in FinalChunk metadata
    """
    chunk_id: str           # the new chunk's ID
    related_id: str         # the existing chunk's ID
    relationship_type: str  # one of the 6 types above
    explanation: str        # 1-2 sentences explaining why this relationship holds


# ── Main State ────────────────────────────────────────────────────────────────

class IngestionState(TypedDict):
    """
    Full state flowing through the entire pipeline.
    LangGraph passes this between every node. Each node receives the full state
    and returns a partial dict — LangGraph merges it with the existing state.

    Initialize ALL keys before calling PIPELINE.invoke() — LangGraph requires
    all TypedDict keys to be present in the initial state dict.

    The state grows progressively as agents run:
      After Classifier:       raw inputs + content_type/domains/is_own_writing/primary_topic/quality_signal
      After Context Loader:   + context_chunks (what Friday already knows)
      After Chunker:          + raw_chunks
      After Enricher:         + enrichments (first pass)
      After Critic:           + critiques
      After Enricher Refiner: enrichments replaced with refined version
      After Academic Extractor: + academic_analysis (0 or 1 item)
      After Connector:        + connection_map
      After Relationship Typer: + relationship_map
      After Assembler:        + final_chunks
      After Writer:           + write_log
      After Synthesizer:      + summary  (pipeline complete)
    """

    # ── Inputs (set at PIPELINE.invoke() call time) ────────────────────────
    raw_content: str    # the original pasted text (never modified by any agent)
    hint: str           # optional user context hint (e.g. "this is my MBA analysis")

    # ── Classifier output (Agent 1) ────────────────────────────────────────
    # Filled by: run_classifier()
    # Read by:   Chunker (to inform chunking strategy), Critic (adjusts lens),
    #            Synthesizer (for the final summary)
    content_type: str   # "article" | "notes" | "analysis" | "framework_ref" | "personal_reflection" | "case_study" | "technical_doc"
    domains: List[str]  # ["pm", "strategy", "tech", ...] — up to 3 primary domains
    is_own_writing: bool
    primary_topic: str  # e.g. "SaaS unit economics" — used by Enricher and Synthesizer
    quality_signal: str # "high" | "medium" | "low" — guides depth of processing

    # ── Chunker output (Agent 2) ───────────────────────────────────────────
    # Filled by: run_chunker()
    # Read by:   Enricher, Critic, Connector (all read this), Assembler, Synthesizer
    raw_chunks: List[RawChunk]

    # ── Enricher output (Agent 3) ──────────────────────────────────────────
    # Filled by: run_enricher()
    # Read by:   Assembler — merges implications/use_cases/questions into core chunk content
    enrichments: List[Enrichment]   # one per raw_chunk, matched by chunk_id

    # ── Critic output (Agent 4) ────────────────────────────────────────────
    # Filled by: run_critic()
    # Read by:   Assembler — turns each critique into a "_critique" companion FinalChunk
    critiques: List[Critique]       # one per raw_chunk, matched by chunk_id

    # ── Connector output (Agent 8) ─────────────────────────────────────────
    # Filled by: run_connector() — vector search, no LLM
    # Read by:   Assembler — writes related_ids into FinalChunk metadata
    connection_map: List[Connection]  # one per raw_chunk, matched by chunk_id

    # ── Assembler output (Agent 10) ────────────────────────────────────────
    # Filled by: run_assembler()
    # Read by:   Writer — upserts each FinalChunk to ChromaDB
    # Note: len(final_chunks) >= 2 * len(raw_chunks) in the normal case
    #       (one core + one critique per input chunk + optional academic_context)
    final_chunks: List[FinalChunk]   # core chunks + critique companions + academic_context

    # ── Writer output (Agent 11) ───────────────────────────────────────────
    # Filled by: run_writer()
    # Read by:   Synthesizer — uses ok count and error count for the summary
    write_log: List[Dict[str, str]]  # [{"id": ..., "collection": ..., "status": "ok"}]

    # ── Synthesizer output (Agent 12) ──────────────────────────────────────
    # Filled by: run_synthesizer()
    # Read by:   /ingest endpoint — returned to the UI as the Teach tab result message
    summary: str

    # ── Context Loader output (Agent 2) ────────────────────────────────────────
    # Filled by: run_context_loader()
    # Read by:   Chunker, Enricher, Critic, Enricher Refiner
    # Empty list on first run (empty DB)
    context_chunks: List[ContextChunk]

    # ── Academic Extractor output (Agent 7) ───────────────────────────────────
    # Filled by: run_academic_extractor()
    # Read by:   Assembler — creates "academic_context" companion chunk
    # Empty list for non-academic content
    academic_analysis: List[AcademicAnalysis]

    # ── Relationship Typer output (Agent 9) ───────────────────────────────────
    # Filled by: run_relationship_typer()
    # Read by:   Assembler — enriches FinalChunk metadata with relationship types
    relationship_map: List[RelationshipEntry]

    # ── Pipeline trace (accumulated across all nodes) ──────────────────────
    # Each node appends one PipelineLogEntry. Shown in Teach tab as a progress log.
    pipeline_log: List[PipelineLogEntry]
