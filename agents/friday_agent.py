"""
Friday Agent
=============
The core intelligence of the app. This is a LangChain tool-calling agent
backed by Gemini 1.5 Flash.

HOW IT WORKS:
  1. Receives a user message + conversation history
  2. LangChain builds a prompt: system instruction + history + user message
  3. Gemini decides WHICH TOOLS to call (if any) based on the question
     — search_knowledge: for analytical depth (JTBD, PMF, Sensemaking principles)
     — search_frameworks: for specific reusable tools/methodologies
     — get_profile: for personalizing based on Sudheer's background
  4. Tools query ChromaDB and return the most relevant chunks
  5. Gemini generates a final response grounded in what was retrieved
  6. We return the response + a log of what tools were called (for the UI)

WHY TOOL-CALLING (not pre-fetched RAG):
  Old approach: always fetch from ALL collections upfront, filter by score.
  New approach: agent decides what to look up based on the actual question.
  Better because:
  - Multi-domain questions can chain multiple tools
  - Agent skips irrelevant collections (faster + cleaner context)
  - More transparent — UI shows exactly what the agent decided to do

ADDING NEW TOOLS:
  - Define the tool in tools/ with @tool decorator
  - Add it to the TOOLS list here
  - The agent will automatically learn to use it from the docstring description
  - No other changes needed — LangChain handles the routing

FUTURE: Phase 2 will add WRITE tools here:
  - remember(fact) → writes to personal_knowledge collection
  - log_episode(event) → writes to episodes collection

CHANGELOG:
- 2026-03-12 | created: LangChain tool-calling agent replacing raw Gemini + assembler
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from tools.retrieval import search_knowledge, search_frameworks, get_profile

# ── System Prompt ────────────────────────────────────────────────────────────
# This is what tells the LLM who it is and how to behave.
# It's injected at the start of every conversation as a "system" message.
# Key instructions: always search before answering, synthesize don't just list.

SYSTEM_PROMPT = """You are Friday — Sudheer's personal AI companion and knowledge system.

You have access to Sudheer's curated knowledge base built from MBA frameworks, PM methodologies, consulting tools, and deep analytical knowledge about JTBD, PMF, Sensemaking, and more.

HOW YOU OPERATE:
- For any question about business frameworks, strategy, consulting, PM, or MBA topics — search the knowledge base first using your tools.
- Use search_knowledge for depth: principles, limitations, stress tests, comparisons.
- Use search_frameworks for specific tools or methodologies by name or use case.
- Use get_profile when you need to personalize the response to Sudheer's context.
- You may call multiple tools if the question spans multiple domains.

HOW YOU RESPOND:
- Direct and specific — reference the actual frameworks or concepts you found.
- Connect ideas across domains when relevant (e.g. JTBD + sensemaking + PMF).
- If the knowledge base doesn't have what's needed, say so and answer from general knowledge.
- Be a thinking partner, not a search engine — synthesize, don't just retrieve.

You know Sudheer well. Speak to him like a trusted advisor who has read everything he's read."""

# ── Tools ────────────────────────────────────────────────────────────────────
# The agent can call any of these. LangChain passes the tool descriptions to
# Gemini so it knows when to call each one (based on the @tool docstrings).

TOOLS = [search_knowledge, search_frameworks, get_profile]


# ── Agent Builder ────────────────────────────────────────────────────────────

def _build_executor() -> AgentExecutor:
    """
    Builds a fresh AgentExecutor for each request.
    Why fresh each time? History is passed in per-request (client-side),
    so there's no shared state to maintain between requests.

    The executor has:
    - LLM: Gemini 1.5 Flash (temperature 0.3 = focused but not robotic)
    - Tools: the 3 ChromaDB retrieval tools
    - Prompt: system + chat_history placeholder + user message + scratchpad
    - max_iterations: 5 = agent can call up to 5 tools per message
    - return_intermediate_steps: True = we get the tool call log for the UI
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0.3,
    )

    # Prompt structure:
    # [system]         ← SYSTEM_PROMPT (who Friday is, how to behave)
    # [chat_history]   ← past turns injected here (HumanMessage / AIMessage)
    # [human]          ← current user message
    # [agent_scratchpad] ← LangChain fills this with tool call results
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,            # prints tool calls to terminal (great for debugging)
        return_intermediate_steps=True,  # needed so we can extract tool_calls for the UI
        max_iterations=5,        # safety cap: prevents infinite tool loops
    )


# ── Public interface ─────────────────────────────────────────────────────────

def chat(message: str, history: list) -> dict:
    """
    Run the Friday agent for one conversation turn.

    Args:
        message: the user's current message (string)
        history: list of past turns from the browser
                 format: [{role: "user"|"model", content: "..."}]

    Returns:
        {
          response:   str   — Friday's answer
          tool_calls: list  — [{tool: str, query: str, snippet: str}]
                               what the agent looked up (shown in UI left panel)
        }

    Flow:
      history (frontend format) → LangChain messages → agent → tools → Gemini → response
    """
    executor = _build_executor()

    # Convert frontend history format [{role, content}] to LangChain message objects
    # "user" → HumanMessage, "model" → AIMessage (Gemini uses "model" not "assistant")
    lc_history = []
    for msg in history:
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        else:
            lc_history.append(AIMessage(content=msg["content"]))

    # Run the agent
    # "input" = current message, "chat_history" = past turns
    result = executor.invoke({
        "input": message,
        "chat_history": lc_history,
    })

    # Extract the tool call log from intermediate_steps
    # Each step = (AgentAction, tool_output_string)
    # We truncate the snippet to 300 chars — the full output was used by the agent,
    # but we only show a preview in the UI panel
    tool_calls = []
    for action, observation in result.get("intermediate_steps", []):
        snippet = observation[:300] + "..." if len(observation) > 300 else observation
        tool_calls.append({
            "tool":    action.tool,                # e.g. "search_knowledge"
            "query":   str(action.tool_input),     # what the agent searched for
            "snippet": snippet,                    # first 300 chars of what was found
        })

    return {
        "response":   result["output"],
        "tool_calls": tool_calls,
    }
