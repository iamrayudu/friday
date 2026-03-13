"""
Classifier Node
===============
POSITION: Agent 1 of 8

RECEIVES FROM STATE:
  raw_content (str) — the full text the user pasted into the Teach tab
  hint        (str) — optional context the user provided (e.g. "this is my MBA analysis")

ADDS TO STATE:
  content_type   (str)       — what kind of content this is
  domains        (List[str]) — which subject areas it covers
  is_own_writing (bool)      — True if Sudheer wrote it himself
  primary_topic  (str)       — the main subject in one short phrase
  quality_signal (str)       — how dense/analytical the content is

PASSES TO: Chunker (Agent 2)
  The Chunker uses content_type to decide chunking strategy (e.g. "personal_reflection"
  maps to the "personal" collection; "framework_ref" maps to "frameworks"). It also
  uses domains to inform collection routing and chunk metadata.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INPUT:
    raw_content = "SaaS businesses live and die by their unit economics.
                   CAC payback tells you how many months of revenue it takes
                   to recoup the cost of acquiring a customer. LTV:CAC ratio
                   above 3:1 is the benchmark for healthy growth..."
    hint        = "article on SaaS metrics from First Round Capital"

  OUTPUT (added to state):
    content_type   = "article"
    domains        = ["finance", "strategy", "tech"]
    is_own_writing = False
    primary_topic  = "SaaS unit economics"
    quality_signal = "high"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS NODE EXISTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Without classification, every downstream agent would have to re-infer the
  same metadata independently — wasting LLM calls and producing inconsistent
  results. By classifying once upfront, the Classifier acts as a shared
  context provider. The Chunker knows which collection to route to, the Critic
  knows what lens to apply (MBA article vs personal reflection vs tech doc),
  and the Enricher knows which domains to draw implications from.

  It is also the only agent that sees the hint alongside the raw content —
  the hint is primarily a classifier signal ("this is my own analysis" changes
  is_own_writing from False to True, which flows through every other agent).

EVERY DOWNSTREAM AGENT BEHAVIOR CHANGES BASED ON THIS OUTPUT:
  - Chunker:    content_type → collection routing; is_own_writing → your_analysis flag
  - Enricher:   domains → contextualize implications for the right field
  - Critic:     content_type → adjust critique lens (framework vs experience vs article)
  - Connector:  domains → search the right area of ChromaDB
  - Synthesizer: content_type + domains → write an informed summary
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from agents.pipeline.state import IngestionState, PipelineLogEntry
from agents.pipeline.utils import get_llm


# ── Structured output schema ──────────────────────────────────────────────────

class ClassifierOutput(BaseModel):
    content_type: str = Field(
        description="One of: article | notes | analysis | framework_ref | personal_reflection | case_study | technical_doc"
    )
    domains: List[str] = Field(
        description="List of domains covered. Choose from: mba | tech | product | finance | strategy | marketing | operations | consulting | engineering | personal | general"
    )
    is_own_writing: bool = Field(
        description="True if this content is written by Sudheer himself (first-person, personal analysis, experience). False if it's sourced content he's reading/learning."
    )
    primary_topic: str = Field(
        description="The main subject in 3-6 words. E.g. 'Jobs-to-be-Done framework' or 'SaaS unit economics'"
    )
    quality_signal: str = Field(
        description="Depth of the content. 'high' = dense, analytical, worth deep processing. 'medium' = moderate depth. 'low' = shallow or very brief."
    )


SYSTEM_PROMPT = """You are the first agent in Friday's multi-agent knowledge ingestion pipeline.

Friday is a personal second brain for Sudheer — an MBA student with a background in web app
development and tech product roles. He adds:
- MBA academic content (cases, strategy, frameworks, finance, marketing, ops)
- His own analysis and opinions
- Tech knowledge (web dev, product, system design, engineering)
- Personal experience from tech career
- Cross-domain insights

YOUR JOB: Classify the incoming content so downstream agents know how to process it.

Be precise. The content_type and is_own_writing fields are especially important:
- 'article' = sourced written content (blog post, paper, book chapter)
- 'notes' = bullet points or condensed summaries from class/reading
- 'analysis' = structured argument or analytical writeup (could be sourced OR own)
- 'framework_ref' = description of a specific reusable methodology or tool
- 'personal_reflection' = Sudheer's own experience, lessons, or observations
- 'case_study' = a narrative case with context, analysis, and outcome
- 'technical_doc' = code, system design, technical reference

is_own_writing = True only if the content uses first-person voice consistently OR is
explicitly described as his own analysis in the hint."""


def run_classifier(state: IngestionState) -> Dict[str, Any]:
    """
    Classifies the raw content and updates the shared state.
    Returns a partial state dict with classifier outputs + updated pipeline_log.

    READS FROM STATE:  raw_content, hint
    WRITES TO STATE:   content_type, domains, is_own_writing, primary_topic,
                       quality_signal, pipeline_log
    """
    llm = get_llm(temperature=0.1)  # low temperature — classification should be deterministic
    structured_llm = llm.with_structured_output(ClassifierOutput)

    # Build the user message: prepend hint if provided so the LLM has explicit context
    user_content = state["raw_content"]
    if state["hint"]:
        # Hint is prepended separately so the LLM can use it as a classification signal
        # without it being confused as part of the content to classify
        user_content = f"HINT FROM USER: {state['hint']}\n\n---\n\n{user_content}"

    result: ClassifierOutput = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ])

    # Build a pipeline log entry so the UI can show classification results
    log_entry: PipelineLogEntry = {
        "stage":   "classifier",
        "status":  "done",
        "summary": f"Identified {result.content_type} about '{result.primary_topic}' "
                   f"({', '.join(result.domains)}) — {result.quality_signal} quality",
        "detail":  {
            "content_type":   result.content_type,
            "domains":        result.domains,
            "is_own_writing": result.is_own_writing,
            "primary_topic":  result.primary_topic,
            "quality_signal": result.quality_signal,
        },
    }

    # Return partial state — LangGraph merges this with existing state
    # All five classifier outputs flow into the Chunker as context
    return {
        "content_type":   result.content_type,
        "domains":        result.domains,
        "is_own_writing": result.is_own_writing,
        "primary_topic":  result.primary_topic,
        "quality_signal": result.quality_signal,
        "pipeline_log":   state["pipeline_log"] + [log_entry],
    }
