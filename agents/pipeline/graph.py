"""
Ingestion Pipeline Graph
========================
Wires all 12 agent nodes into a compiled LangGraph StateGraph.

PIPELINE ORDER:
  classifier → context_loader → chunker → enricher → critic → enricher_refiner
  → academic_extractor → connector → relationship_typer → assembler → writer → synthesizer

WHY THIS ORDER:
  classifier first        — every other node needs content_type, domains, is_own_writing
  context_loader second   — loads existing DB knowledge before chunking; gives all downstream
                            agents awareness of what Friday already knows
  chunker third           — produces raw_chunks; uses context_chunks to avoid re-chunking
  enricher                — first-pass enrichment; uses context_chunks for non-redundancy
  critic                  — challenges enrichments in light of context; feeds the refiner
  enricher_refiner        — refines enrichments using the Critic's analysis (3-turn dialogue)
  academic_extractor      — extracts intellectual structure; runs after chunking so it can
                            reference chunk names; before connector so assembler has full picture
  connector               — queries ChromaDB with chunk content; needs raw_chunks
  relationship_typer      — classifies HOW chunks relate to existing knowledge (needs connection_map)
  assembler               — merges all outputs; needs enrichments + critiques + connection_map
                            + academic_analysis + relationship_map
  writer                  — needs final_chunks from assembler
  synthesizer last        — needs everything: topic, chunks, connections, write_log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT HANDOFF TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  FROM                → TO                  KEYS TRANSFERRED                   EXAMPLE DATA
  ──────────────────────────────────────────────────────────────────────────────────────────────
  START               → classifier          raw_content, hint                  "SaaS article text...",
                                                                               "MBA finance article"

  classifier          → context_loader      content_type, domains,             "article", ["finance","strategy"],
                                            is_own_writing, primary_topic,     False, "SaaS unit economics",
                                            quality_signal                     "high"

  context_loader      → chunker             context_chunks                     [{id:"km_pmf_001",
                                                                                 name:"PMF Growth Metrics",
                                                                                 collection:"knowledge",
                                                                                 content:"PMF can be...",
                                                                                 score:0.81}]

  chunker             → enricher            raw_chunks                         [{id:"km_saas_cac_001",
                                            (context_chunks still in state)     name:"CAC Payback",
                                                                                 collection:"knowledge",
                                                                                 domain:"finance",
                                                                                 chunk_type:"principle",
                                                                                 your_analysis:False,
                                                                                 content:"CAC payback..."}]

  enricher            → critic              enrichments                        [{chunk_id:"km_saas_cac_001",
                                            (raw_chunks, context_chunks          implications:["Short payback..."],
                                             still in state)                     follow_up_questions:[...],
                                                                                 use_cases:[...]}]

  critic              → enricher_refiner    critiques                          [{chunk_id:"km_saas_cac_001",
                                            (raw_chunks, enrichments,            limitations:["Ignores blended..."],
                                             context_chunks still in state)      biases:["VC-funded lens"],
                                                                                 stress_tests:["What if churn..."]}]

  enricher_refiner    → academic_extractor  enrichments (REPLACED with         [{chunk_id:"km_saas_cac_001",
                                            refined version)                     implications:["Refined, critique-aware..."],
                                                                                 follow_up_questions:[...],
                                                                                 use_cases:["Conditional: use when..."]}]

  academic_extractor  → connector           academic_analysis                  [{key_claims:["CAC payback < 12mo..."],
                                            (all prior keys still in state)      key_authors:["David Sacks (...)"],
                                                                                 key_theories:["SaaS unit economics"],
                                                                                 research_approach:"practitioner",
                                                                                 debate_position:"...",
                                                                                 intellectual_context:"..."}]

  connector           → relationship_typer  connection_map                     [{chunk_id:"km_saas_cac_001",
                                            (raw_chunks still in state)          related_ids:["km_pmf_growth_001"],
                                                                                 relationship_notes:"score 0.81"}]

  relationship_typer  → assembler           relationship_map                   [{chunk_id:"km_saas_cac_001",
                                            (raw_chunks, enrichments,            related_id:"km_pmf_growth_001",
                                             critiques, connection_map,          relationship_type:"BUILDS_ON",
                                             academic_analysis still in state)   explanation:"CAC payback assumes..."}]

  assembler           → writer              final_chunks                       [{id:"km_saas_cac_001",
                                                                                 content:"CAC payback...\n\n**Implications**...",
                                                                                 metadata:{related_ids:"km_pmf_growth_001",
                                                                                           relationship_types:"BUILDS_ON:km_pmf_growth_001"}},
                                                                                {id:"km_saas_cac_001_critique",
                                                                                 content:"**Limitations**...",
                                                                                 metadata:{parent_id:"km_saas_cac_001"}},
                                                                                {id:"ak_saas_unit_economics_academic_context",
                                                                                 content:"**Key Claims**\n- ...",
                                                                                 chunk_type:"academic_context"}]

  writer              → synthesizer         write_log                          [{id:"km_saas_cac_001",
                                            (all prior keys still in state)     collection:"knowledge",
                                                                                 status:"ok"},
                                                                                {id:"km_saas_cac_001_critique",
                                                                                 ...}]

  synthesizer         → END                 summary                            "Added 5 foundational concepts
                                                                               on SaaS unit economics with
                                                                               critical limitations, connecting
                                                                               to 3 existing PMF chunks."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUTURE OPTIMIZATION:
  Enricher and Critic could run in parallel (both only read raw_chunks).
  LangGraph supports this via the Send API. Not implemented here to keep the
  pipeline debuggable. The 3-turn dialogue (Enricher → Critic → Enricher Refiner)
  requires sequential ordering, so parallelization would only apply if Enricher
  Refiner is removed and we revert to single-pass enrichment.

SINGLETON:
  PIPELINE is compiled once at module import time and reused across all requests.
  Compilation is cheap (just graph validation), but doing it once is cleaner.
"""

from langgraph.graph import StateGraph, START, END

from agents.pipeline.state import IngestionState
from agents.pipeline.nodes.classifier        import run_classifier
from agents.pipeline.nodes.context_loader    import run_context_loader
from agents.pipeline.nodes.chunker           import run_chunker
from agents.pipeline.nodes.enricher          import run_enricher
from agents.pipeline.nodes.critic            import run_critic
from agents.pipeline.nodes.enricher_refiner  import run_enricher_refiner
from agents.pipeline.nodes.academic_extractor import run_academic_extractor
from agents.pipeline.nodes.connector         import run_connector
from agents.pipeline.nodes.relationship_typer import run_relationship_typer
from agents.pipeline.nodes.assembler         import run_assembler
from agents.pipeline.nodes.writer            import run_writer
from agents.pipeline.nodes.synthesizer       import run_synthesizer


def build_graph():
    """
    Builds and compiles the 12-node ingestion pipeline graph.
    Each node function receives the full IngestionState and returns a
    partial dict — LangGraph merges it with the current state automatically.
    """
    graph = StateGraph(IngestionState)

    # Register all 12 nodes
    graph.add_node("classifier",          run_classifier)
    graph.add_node("context_loader",      run_context_loader)
    graph.add_node("chunker",             run_chunker)
    graph.add_node("enricher",            run_enricher)
    graph.add_node("critic",              run_critic)
    graph.add_node("enricher_refiner",    run_enricher_refiner)
    graph.add_node("academic_extractor",  run_academic_extractor)
    graph.add_node("connector",           run_connector)
    graph.add_node("relationship_typer",  run_relationship_typer)
    graph.add_node("assembler",           run_assembler)
    graph.add_node("writer",              run_writer)
    graph.add_node("synthesizer",         run_synthesizer)

    # Wire the 12-node pipeline sequentially
    # START → classifier: raw_content + hint enter the pipeline
    graph.add_edge(START,                "classifier")

    # classifier → context_loader: content_type, domains, primary_topic now available
    # context_loader loads existing related chunks from ChromaDB before any processing
    graph.add_edge("classifier",         "context_loader")

    # context_loader → chunker: context_chunks now in state
    # chunker uses them to avoid re-chunking already-known concepts
    graph.add_edge("context_loader",     "chunker")

    # chunker → enricher: raw_chunks now available
    # enricher uses context_chunks to produce non-redundant implications
    graph.add_edge("chunker",            "enricher")

    # enricher → critic: enrichments (first pass) now in state
    # critic sees both raw_chunks AND enrichments, challenges both
    graph.add_edge("enricher",           "critic")

    # critic → enricher_refiner: critiques now in state
    # enricher_refiner reads initial enrichments + critiques → produces refined enrichments
    # OVERWRITES state["enrichments"] with the improved version
    graph.add_edge("critic",             "enricher_refiner")

    # enricher_refiner → academic_extractor: refined enrichments now in state
    # academic_extractor runs on full raw_content to extract intellectual structure
    graph.add_edge("enricher_refiner",   "academic_extractor")

    # academic_extractor → connector: academic_analysis now in state (0 or 1 item)
    # connector searches ChromaDB using raw_chunk content — pure vector search
    graph.add_edge("academic_extractor", "connector")

    # connector → relationship_typer: connection_map now in state
    # relationship_typer classifies HOW each pair of chunks relate (BUILDS_ON, EXTENDS, etc.)
    graph.add_edge("connector",          "relationship_typer")

    # relationship_typer → assembler: relationship_map now in state
    # assembler has all inputs: raw_chunks, refined enrichments, critiques,
    # connection_map, academic_analysis, relationship_map → builds final_chunks
    graph.add_edge("relationship_typer", "assembler")

    # assembler → writer: final_chunks ready (core + critique + academic_context)
    graph.add_edge("assembler",          "writer")

    # writer → synthesizer: write_log complete; synthesizer writes the UI summary
    graph.add_edge("writer",             "synthesizer")

    # synthesizer → END: pipeline complete; /ingest endpoint returns to UI
    graph.add_edge("synthesizer",        END)

    return graph.compile()


# Compiled once at import time — reused for all /ingest requests
PIPELINE = build_graph()
