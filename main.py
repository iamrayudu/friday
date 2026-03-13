"""
Friday — FastAPI Entry Point
==============================
This is the HTTP layer. It receives requests from the browser and routes them
to the right agent. It does NOT contain any AI logic — that lives in agents/.

REQUEST FLOW:
  Chat:
    Browser  →  POST /chat    →  friday_agent.chat()     →  ChromaDB + Gemini  →  {response, tool_calls}
  Teach:
    Browser  →  POST /ingest  →  ingestion_agent.process() →  Gemini structures → ChromaDB write → {summary, chunks}

ADDING NEW CAPABILITIES:
  - New agent → create agents/<name>_agent.py
  - New endpoint → add @app.post("/<route>") here, import the agent
  - e.g. Phase 3: POST /checkin → memory_agent.log_checkin()

CHANGELOG:
- 2026-03-12 | created: FastAPI replacing Flask, wired to LangChain agent
- 2026-03-12 | added: POST /ingest → ingestion_agent for the Teach tab
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load .env BEFORE importing agents (they read GOOGLE_API_KEY at import time)
load_dotenv()

from agents.friday_agent import chat as friday_chat           # noqa: E402
from agents.ingestion_agent import process as ingest_process  # noqa: E402

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ── Request / Response models ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    # History managed client-side (browser tracks it, sends with each request)
    # Format: [{role: "user"|"model", content: "..."}]
    # Why client-side? Server stays stateless — no session storage needed yet.
    history: list = []


class IngestRequest(BaseModel):
    content: str        # raw text — article, notes, your analysis, anything
    hint:    str = ""   # optional: brief context to help the agent classify correctly
                        # e.g. "this is my own analysis of Porter's Five Forces for SaaS"


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def index(request: Request):
    # Serves the chat UI (templates/index.html)
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(body: ChatRequest):
    """
    Main conversation endpoint.

    What happens here:
    1. Request validated by Pydantic (message + history)
    2. Handed to friday_agent.chat() — the LangChain tool-calling agent
    3. Agent searches ChromaDB via tools, generates response via Gemini
    4. Returns {response: str, tool_calls: [{tool, query, snippet}]}
    """
    try:
        result = friday_chat(
            message=body.message,
            history=body.history,
        )
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/ingest")
async def ingest(body: IngestRequest):
    """
    Teach Friday endpoint — adds new knowledge to ChromaDB.

    What happens here:
    1. Raw content + optional hint validated by Pydantic
    2. Handed to ingestion_agent.process() — Gemini reads and structures the content
    3. Agent decides how to chunk it, which collection, and what metadata to attach
    4. Each chunk is upserted into ChromaDB (safe to run twice — no duplicates)
    5. Returns {summary, chunks: [{id, name, collection, domain, chunk_type}], counts}
    """
    try:
        result = ingest_process(
            content=body.content,
            hint=body.hint,
        )
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Server ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("Friday is starting...")
    print("Open http://localhost:8000")
    # reload=True means the server restarts automatically on file changes
    # Great for development — turn off in production
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
