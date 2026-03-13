"""
Friday Retrieval Tools
=======================
LangChain @tool functions that the Friday agent uses to search ChromaDB.

HOW TOOLS WORK IN LANGCHAIN:
  The @tool decorator turns a Python function into something the LLM can call.
  LangChain passes the function name + docstring to Gemini so it knows:
  - WHEN to call each tool (based on the docstring description)
  - WHAT to pass as input (based on the function signature)
  The agent doesn't just blindly call all tools — it reads the docstrings
  and decides which ones are relevant for the current question.

  IMPORTANT: Write docstrings as if you're explaining to the LLM when to use it,
  not as traditional Python documentation.

TOOLS IN THIS FILE:
  search_knowledge   — analytical depth: principles, limitations, bias, comparisons
  search_frameworks  — reusable tools: step-by-step processes, mental models
  get_profile        — Sudheer's personal background and context

ADDING NEW TOOLS:
  1. Define a function with @tool decorator
  2. Write a clear docstring (the LLM reads this to decide when to call it)
  3. Import and add it to TOOLS list in agents/friday_agent.py
  That's it — the agent automatically learns to use it.

FUTURE (Phase 2 — Memory Agent):
  Add WRITE tools here:
  - remember(fact: str) → upsert to personal_knowledge
  - log_episode(event: str) → upsert to episodes
  - store_insight(pattern: str) → upsert to insights

CHANGELOG:
- 2026-03-12 | created: LangChain tools wrapping ChromaDB collections
"""

from langchain.tools import tool
from memory.vector_store import get_store


def _format(results: list) -> str:
    """
    Converts ChromaDB similarity search results into a readable string.
    The agent receives this string as the tool's output and uses it as context.

    results format from similarity_search_with_score():
    [(Document(page_content="...", metadata={...}), float_score), ...]

    ChromaDB returns cosine distance (0 = identical, 2 = opposite).
    We convert to similarity: relevance = 1 - distance (higher = more relevant).
    """
    if not results:
        return "No relevant results found."

    parts = []
    for doc, score in results:
        meta = doc.metadata
        # Extract the best available name from the metadata
        name = (
            meta.get("name")
            or meta.get("framework")
            or meta.get("chunk_type")
            or "—"
        )
        relevance = round(1 - score, 3)
        parts.append(f"[{name}] relevance: {relevance}\n{doc.page_content}")

    # Separate chunks with a divider so the LLM can parse them clearly
    return "\n\n---\n\n".join(parts)


@tool
def search_knowledge(query: str) -> str:
    """
    Search the deep analytical knowledge base.
    Use for questions about frameworks in depth: principles, limitations,
    stress tests, bias flags, comparisons, and case study analysis.
    Covers: JTBD, PMF, Sensemaking, and other analytical knowledge.

    Examples of when to call this:
    - "when does JTBD break down?"  → limitations chunk
    - "how does sensemaking compare to JTBD?" → comparison chunk
    - "what biases should I watch for with PMF?" → bias chunk
    - "walk me through the sensemaking process" → principle/application chunk
    """
    # k=4: retrieve top 4 most similar chunks
    # similarity_search_with_score returns (Document, float) pairs
    results = get_store("knowledge").similarity_search_with_score(query, k=4)
    return _format(results)


@tool
def search_frameworks(query: str) -> str:
    """
    Search the standalone frameworks and methodologies collection.
    Use for finding specific tools, step-by-step processes, mental models,
    or frameworks by name or use case.
    Covers: MBA frameworks (SWOT, Porter's, BCG), PM tools (personas, crossing the chasm),
    consulting methodologies (MECE, Harvard case method), sensemaking tools.

    Examples of when to call this:
    - "how do I apply Porter's Five Forces?" → fw_porters_001
    - "what is the three-level diagnostic?" → fw_three_level_diagnostic
    - "explain MECE" → fw_mece_001
    - "what frameworks exist for go-to-market?" → crossing the chasm, non-consumption
    """
    results = get_store("frameworks").similarity_search_with_score(query, k=3)
    return _format(results)


@tool
def get_profile(query: str = "background skills goals experience") -> str:
    """
    Get Sudheer's personal background, skills, goals, and context.
    Use when the response should be personalized — when Sudheer asks
    about his own situation, strengths, weaknesses, or MBA journey.
    Also use when the question implies needing to know who he is.

    Examples of when to call this:
    - "what are my weak areas?"
    - "how does this apply to my situation?"
    - "given my background, which frameworks matter most?"
    - "what should I focus on for my MBA?"

    Note: Currently the personal_knowledge collection has placeholder content.
    Phase 2 (Memory Agent) will fill this automatically from conversations.
    """
    results = get_store("personal_knowledge").similarity_search_with_score(query, k=2)
    return _format(results)
