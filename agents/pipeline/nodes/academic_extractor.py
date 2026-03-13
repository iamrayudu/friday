"""
Academic Extractor Node
=======================
POSITION: Agent 7 of 12

RECEIVES FROM STATE:
  raw_content    (str)       — the original full text
  primary_topic  (str)       — from Classifier
  content_type   (str)       — from Classifier: "article" | "notes" | etc.
  domains        (List[str]) — from Classifier
  raw_chunks     (List[RawChunk]) — from Chunker: the concept units extracted

ADDS TO STATE:
  academic_analysis (List[AcademicAnalysis]) — 0 or 1 item:
    0 items: for framework_ref or very short personal notes (not analytical)
    1 item:  for article, notes, case_study, personal_reflection, technical_doc

PASSES TO: Connector (Agent 8) via state, then Assembler (Agent 10)
  The Assembler reads academic_analysis to create an "academic_context" companion chunk
  stored in the same collection as the majority of the content's chunks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT: 1500-word article on "SaaS Unit Economics" (from a16z / David Sacks)
  content_type = "article"

  OUTPUT AcademicAnalysis:
    key_claims: [
      "The CAC payback period (not LTV:CAC ratio) is the most operationally actionable SaaS metric.",
      "Net Revenue Retention > 100% is the defining characteristic of a durable SaaS business.",
      "The Magic Number threshold of 0.75 signals whether to accelerate or reduce sales spend."
    ]
    key_authors: [
      "David Sacks (SaaS metrics practitioner, co-founder Yammer/PayPal Mafia)",
      "David Cumming (SaaS Capital, empirical benchmarks for private SaaS)"
    ]
    key_theories: [
      "SaaS unit economics framework",
      "CAC payback period",
      "Net Revenue Retention (NRR)",
      "Magic Number efficiency metric"
    ]
    research_approach: "practitioner"
    debate_position: "Argues that operational SaaS metrics (payback, NRR, Magic Number)
                      are more useful for decision-making than capital-market metrics (LTV:CAC),
                      countering the VC orthodoxy that LTV:CAC is the primary SaaS health signal."
    intellectual_context: "SaaS finance, growth-stage venture metrics, subscription business economics"

  HOW THIS BECOMES A CHUNK IN CHROMADB:
    id: "ak_saas_unit_economics_academic_context"
    collection: "knowledge"  (same as majority of chunks from this ingest)
    chunk_type: "academic_context"
    content: formatted markdown with all 6 fields as sections

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS NODE EXISTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Without this node, Friday knows WHAT each concept says but not:
    - WHO said it and why they're credible (or biased)
    - WHAT intellectual tradition it belongs to
    - WHAT debate it's participating in
    - HOW the knowledge was produced (empirical vs. opinion)

  With this node, Friday can answer:
    "Who are the key thinkers on SaaS metrics?"
      → retrieves academic_context chunk → key_authors
    "What's the theoretical basis of JTBD?"
      → retrieves academic_context chunk → intellectual_context
    "Is this framework empirically validated?"
      → research_approach field answers it

  This is what makes Friday feel like a second brain that understands
  the intellectual landscape — not just a fact retrieval system.

ONE LLM CALL for the whole content. Academic structure is per-content, not per-chunk.
"""

from typing import List, Dict, Any

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from agents.pipeline.state import IngestionState, AcademicAnalysis, PipelineLogEntry
from agents.pipeline.utils import get_llm


# Content types where academic extraction makes sense
ACADEMIC_CONTENT_TYPES = {
    "article", "notes", "case_study", "personal_reflection", "technical_doc", "analysis"
}


# ── Structured output schema ──────────────────────────────────────────────────

class AcademicAnalysisOutput(BaseModel):
    key_claims: List[str] = Field(
        description="3-5 central arguments or findings. Be specific — state what is being claimed, "
                    "not just the topic. E.g. 'NRR > 100% is the single most important SaaS health signal' "
                    "not 'NRR matters'."
    )
    key_authors: List[str] = Field(
        description="Scholars, practitioners, or thinkers whose ideas are central. "
                    "Format: 'Name (role/known for)'. Include 0-5 authors. "
                    "Empty list if no specific authors are referenced."
    )
    key_theories: List[str] = Field(
        description="Named theories, frameworks, or models cited or discussed. "
                    "E.g. 'Jobs-to-be-Done', 'Disruption Theory', 'SaaS unit economics framework'. "
                    "Empty list if none."
    )
    research_approach: str = Field(
        description="How was this knowledge produced? One of: "
                    "empirical | theoretical | case-study | practitioner | synthesis | opinion"
    )
    debate_position: str = Field(
        description="1-2 sentences on what intellectual debate or discourse this content "
                    "is participating in. What conventional wisdom is it supporting or challenging?"
    )
    intellectual_context: str = Field(
        description="What field, tradition, or discipline does this build on? "
                    "E.g. 'Marketing science, consumer behavior, innovation management'"
    )


SYSTEM_PROMPT = """You are the Academic Analyst — the 7th agent in Friday's knowledge pipeline.

Friday is a personal second brain for Sudheer — an MBA student / tech professional.

YOUR JOB: Extract the intellectual and academic structure of the content.

This is NOT about summarizing the content. You are mapping the intellectual landscape:
  - What central claims are being made?
  - Whose ideas does this draw from?
  - What theoretical tradition does this belong to?
  - What debate is this participating in?
  - How was this knowledge produced?

WHY THIS MATTERS:
  When Sudheer asks "who are the key thinkers on PMF?" or "is this empirically validated?",
  Friday needs this structured metadata to answer accurately.
  When he's in a case interview, knowing the intellectual genealogy of a framework
  lets him apply it more confidently and defend it against challenges.

BE SPECIFIC:
  For key_claims: state the actual claim, not the topic.
    BAD:  "The article discusses CAC payback"
    GOOD: "CAC payback < 12 months is the threshold that separates capital-efficient from capital-dependent SaaS"

  For key_authors: include what they're known for in THIS context.
    BAD:  "David Sacks"
    GOOD: "David Sacks (SaaS metrics practitioner, coined the Magic Number efficiency metric)"

If content_type is "personal_reflection" (Sudheer's own writing):
  - key_authors = [] (it's his own analysis)
  - research_approach = "opinion" or "practitioner"
  - debate_position should reflect what existing thinking his analysis responds to"""


def run_academic_extractor(state: IngestionState) -> Dict[str, Any]:
    """
    Extracts the academic/intellectual structure from the ingested content.
    Only runs for analytical content types — skips for framework_ref.

    READS FROM STATE:  raw_content, primary_topic, content_type, domains, raw_chunks
    WRITES TO STATE:   academic_analysis, pipeline_log
    """
    content_type = state.get("content_type", "")

    # Skip for pure framework references — no academic structure to extract
    if content_type not in ACADEMIC_CONTENT_TYPES:
        log_entry: PipelineLogEntry = {
            "stage":   "academic_extractor",
            "status":  "done",
            "summary": f"Skipped — content_type '{content_type}' is not analytical content",
            "detail":  [],
        }
        return {
            "academic_analysis": [],
            "pipeline_log":      state["pipeline_log"] + [log_entry],
        }

    llm = get_llm(temperature=0.2)  # low temperature — factual extraction
    structured_llm = llm.with_structured_output(AcademicAnalysisOutput)

    chunk_names = [c["name"] for c in state["raw_chunks"]]

    user_message = (
        f"Primary topic: {state['primary_topic']}\n"
        f"Content type: {content_type}\n"
        f"Domains: {', '.join(state['domains'])}\n"
        f"Concepts already extracted from this content: {', '.join(chunk_names)}\n\n"
        f"Full content to analyze:\n\n{state['raw_content']}"
    )

    result: AcademicAnalysisOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    academic_analysis: List[AcademicAnalysis] = [{
        "key_claims":           result.key_claims,
        "key_authors":          result.key_authors,
        "key_theories":         result.key_theories,
        "research_approach":    result.research_approach,
        "debate_position":      result.debate_position,
        "intellectual_context": result.intellectual_context,
    }]

    summary_parts = [
        f"{len(result.key_claims)} key claims",
        f"{len(result.key_authors)} authors" if result.key_authors else "",
        f"{len(result.key_theories)} theories" if result.key_theories else "",
        f"approach: {result.research_approach}",
    ]
    summary = "Extracted academic structure: " + ", ".join(p for p in summary_parts if p)

    log_entry = {
        "stage":   "academic_extractor",
        "status":  "done",
        "summary": summary,
        "detail":  {
            "key_claims":        result.key_claims,
            "key_authors":       result.key_authors,
            "key_theories":      result.key_theories,
            "research_approach": result.research_approach,
        },
    }

    return {
        "academic_analysis": academic_analysis,
        "pipeline_log":      state["pipeline_log"] + [log_entry],
    }
