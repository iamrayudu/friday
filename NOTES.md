# Friday — Project Notes

> Living document. Update as the project evolves.
> Last updated: 2026-03-12

---

## What is Friday?

Friday is Sudheer's personal AI second brain.
It is NOT a generic chatbot. It is built specifically for him — an MBA student with a
background in web app development and tech roles.

Friday knows everything Sudheer feeds it:
- MBA academics — case studies, strategy, frameworks, finance, marketing, operations
- His own analysis and opinions on topics
- Tech knowledge — web dev, system design, product decisions, engineering patterns
- Personal experience — roles he's had, projects he's built, lessons learned
- Cross-domain thinking — tech + MBA combined

**The two core actions:**
1. **Chat** — ask Friday anything, it retrieves relevant knowledge and answers with depth
2. **Teach** — paste any content, an agent structures it and stores it permanently

The more you teach it, the smarter it gets. No manual scripts, no data engineering.
Just paste and go.

---

## Current Architecture (Phase 1 + Ingestion Agent — complete)

### Chat flow
```
User (browser) — Chat tab
    ↓ HTTP POST /chat
FastAPI (main.py)
    ↓
Friday Agent (agents/friday_agent.py)
    — LangChain tool-calling agent
    — Gemini 2.0 Flash as the LLM
    — Reads question + decides which tools to call
    ↓
Tools (tools/retrieval.py)
    — search_knowledge()   → "knowledge" collection   (things learned)
    — search_frameworks()  → "frameworks" collection  (reusable tools)
    — get_profile()        → "personal" collection    (who Sudheer is)
    ↓
Vector Store (memory/vector_store.py)
    — LangChain Chroma wrapper, all-MiniLM-L6-v2 embeddings
    — reads from memory/db/chroma/
    ↓
{response, tool_calls} → browser
    — left panel: which tools were called and what they retrieved
    — right panel: Friday's answer
```

### Teach flow
```
User (browser) — Teach tab
    ↓ HTTP POST /ingest  (content + optional hint)
FastAPI (main.py)
    ↓
Ingestion Agent (agents/ingestion_agent.py)
    — Gemini reads the raw content with structured output schema
    — Decides: how to chunk it, which collection, what metadata
    — Chunks by CONCEPT (not word count) — each chunk is independently retrievable
    ↓
ChromaDB write via memory/store.py (upsert — no duplicates)
    — "knowledge"   → analytical depth content
    — "frameworks"  → reusable step-by-step tools
    — "personal"    → Sudheer's background, experience, own analysis
    ↓
{summary, chunks, counts} → browser
    — right panel shows: summary + every chunk stored with its collection + metadata
```

---

## Knowledge Base (what's in ChromaDB)

The database grows every time you use the Teach tab.
Initial seed content is listed below. Everything added via Teach tab appears here too.

### Collection: `knowledge`
Deep analytical content. Any domain: MBA, tech, product, finance, strategy.
Each chunk = one retrievable concept (principle, limitation, comparison, case breakdown).

**Seeded content:**

| Framework   | Chunks | Coverage |
|-------------|--------|----------|
| JTBD        | 14     | core, 3-layer model, nonconsumption, stress tests, biases, comparisons |
| PMF         | 15     | core principle, Rachleff hierarchy, B2B/B2C signals, scaling traps |
| Sensemaking | 13     | 5-step process, organizational bias, onion layers, vs JTBD, diagnostic |

### Collection: `frameworks`
Standalone reusable tools. Any domain: MBA, PM, consulting, engineering.
Each chunk = one complete framework with step-by-step application.

**Seeded content (15 frameworks):**

| Framework                   | ID                            |
|-----------------------------|-------------------------------|
| Harvard Case Method         | fw_harvard_case_001           |
| SWOT                        | fw_swot_001                   |
| Porter's Five Forces        | fw_porters_001                |
| BCG Matrix                  | fw_bcg_001                    |
| Porter's Value Chain        | fw_value_chain_001            |
| MECE                        | fw_mece_001                   |
| MBA Boundary Conditions     | fw_boundary_conditions_001    |
| Persona-Based Segmentation  | fw_personas_001               |
| Disruptive Innovation       | fw_disruptive_innovation_001  |
| Crossing the Chasm          | fw_crossing_chasm_001         |
| Non-Consumption Analysis    | fw_nonconsumption_001         |
| PMF Pricing Signal          | fw_pmf_pricing_signal_001     |
| Sensemaking 5-Steps         | fw_sensemaking_5steps         |
| Three-Level Diagnostic      | fw_three_level_diagnostic     |
| Inside-Out Reframe          | fw_inside_out_reframe         |

### Collection: `personal`
Who Sudheer is. His background, experience, and his own analysis/opinions.
Currently has placeholder text ([FILL IN]) in the seeded chunks.

**How to fill it:**
Option A — use the Teach tab: paste your bio, career background, and what you know.
Option B — edit `scripts/populate.py` directly and re-run it.
Option A is better because the ingestion agent will chunk and classify it properly.

### Collections: `episodes`, `insights`, `case_memory` (empty)
Reserved for Phase 3+ (auto-memory from conversations, behavioral patterns).

---

## Tech Stack

| Component         | Technology                          | Notes                              |
|-------------------|-------------------------------------|------------------------------------|
| Backend           | FastAPI + uvicorn                   | async, production-ready            |
| LLM               | Gemini 2.0 Flash (Google AI Studio) | free tier: 1500 req/day            |
| Agent framework   | LangChain (tool-calling agent)      | ReAct-style with function calling  |
| Structured output | LangChain with_structured_output()  | Gemini returns typed Pydantic JSON |
| Vector store      | ChromaDB (local)                    | SQLite + HNSW index                |
| Embeddings        | all-MiniLM-L6-v2 (HuggingFace)     | local, no API cost                 |
| Frontend          | Vanilla JS + CSS                    | no framework, dark theme           |
| Environment       | Python 3.9.6 venv                   | note: 3.10+ preferred for typing   |

---

## File Map

```
friday/
├── main.py                      ← FastAPI entry: /chat and /ingest routes
├── agents/
│   ├── friday_agent.py          ← Chat agent: LangChain + tools + conversation history
│   └── ingestion_agent.py       ← Teach agent: Gemini structured output → ChromaDB write
├── tools/
│   └── retrieval.py             ← @tool functions: search ChromaDB collections (used by friday_agent)
├── memory/
│   ├── store.py                 ← low-level ChromaDB read/write (used by ingestion_agent + scripts)
│   ├── schema.py                ← collection definitions and metadata contracts
│   └── vector_store.py          ← LangChain Chroma wrapper (used by retrieval tools)
├── scripts/
│   ├── populate.py              ← seeds personal + MBA frameworks (initial seed, run once)
│   ├── ingest_jtbd.py           ← JTBD knowledge → `knowledge` collection (initial seed)
│   ├── ingest_pmf_article.py    ← PMF knowledge → `knowledge` collection (initial seed)
│   ├── ingest_sensemaking_frameworks.py  ← 3 sensemaking tools → `frameworks` (initial seed)
│   ├── ingest_sensemaking_article.py     ← 13 sensemaking chunks → `knowledge` (initial seed)
│   └── inspect_memory.py        ← debug: inspect ChromaDB contents and counts
├── docs/
│   ├── conversation_flow.txt    ← explains Chat and Teach flows end-to-end
│   └── data_storage.txt         ← explains ChromaDB, collections, embeddings, ingestion
├── templates/
│   └── index.html               ← frontend: Chat tab + Teach Friday tab
├── .env                         ← GOOGLE_API_KEY (never commit)
├── .gitignore
├── requirements.txt             ← all Python dependencies
└── NOTES.md                     ← this file
```

**Note on scripts/:** The `ingest_*.py` and `populate.py` scripts were used for the initial
knowledge seed before the Ingestion Agent existed. New content should go through the
Teach tab. The scripts are kept for reference and for re-seeding from scratch.

---

## Design Decisions (and why)

**Three collections cover everything: knowledge / frameworks / personal**
Instead of splitting by domain (MBA vs tech vs PM), we use metadata (domain field).
This lets cross-domain queries retrieve across everything in one search.
A tech + MBA question can pull from both in a single tool call.

**Ingestion agent chunks by concept, not word count**
Word-count chunking creates arbitrary splits mid-idea. Bad for retrieval.
Concept chunking means each stored unit is independently meaningful.
Gemini reads the full content and decides where ideas begin and end.

**your_analysis flag on personal chunks**
When you write "I think..." or paste your own analysis, those chunks are marked
`your_analysis: true`. Friday knows to treat these as your perspective, not sourced
knowledge. Important for how it frames responses.

**all-MiniLM-L6-v2 for embeddings (not Google's embedding API)**
All existing data was ingested with this model. Switching requires re-embedding everything.
Kept local — no API cost, no latency, no dependency.

**Ingestion uses upsert() not add()**
Same content pasted twice → same IDs → updated in place, no duplicates.
Safe to re-teach content if it changes.

**Client-side history management**
Browser tracks conversation history and sends it with each request.
Server stays stateless. No session storage needed yet.

**Agent decides what to retrieve (not pre-fetched RAG)**
Old approach: always fetch from all 3 collections upfront, filter by score.
New approach: LangChain tool-calling agent reads the question and decides which tools to call.
Better: multi-domain questions chain tools; agent skips irrelevant collections.

---

## Phases — Build Roadmap

### Phase 1 — Foundation (DONE)
- [x] ChromaDB local store
- [x] Knowledge ingestion (JTBD, PMF, Sensemaking) via scripts
- [x] LangChain tool-calling agent (Friday Agent)
- [x] FastAPI backend
- [x] Chat UI with tool call transparency panel

### Phase 2 — Ingestion Agent (DONE)
- [x] `agents/ingestion_agent.py` — Gemini structured output chunks any content into ChromaDB
- [x] `POST /ingest` endpoint in main.py
- [x] Teach Friday tab in the UI — paste content, see what gets stored
- [x] Three-collection routing: knowledge / frameworks / personal
- [x] your_analysis flag distinguishes sourced knowledge from Sudheer's own writing

### Phase 3 — Memory Agent (NEXT)
After every conversation turn, a background Gemini call reads the exchange
and extracts what's worth remembering → upserts to `personal` + `episodes`.
Personal profile builds automatically from conversations.

What to build:
- `agents/memory_agent.py` — extracts facts + episodes from a conversation turn
- FastAPI `BackgroundTasks` to run it after each `/chat` response (async, no latency hit)
- Profile display in the UI (what Friday currently knows about you)

### Phase 4 — Pattern Recognition (PLANNED)
Daily check-ins stored as episodes. Periodic Gemini call reads episodes
and generates behavioral insights → stored in `insights` collection.

What to build:
- `/checkin` endpoint
- `agents/insight_agent.py` — reads episodes, generates patterns
- Scheduled job (APScheduler or similar)
- Check-in panel in the UI

### Phase 5 — Proactive Intelligence (PLANNED)
Friday surfaces things without you asking.
- Morning brief: what's relevant today based on goals + recent context
- Weekly review: what shifted, what to focus on
- `/brief` and `/review` endpoints

---

## Known Issues / TODOs

- [ ] `personal` collection has [FILL IN] placeholders — use Teach tab to add real background
- [ ] Python 3.9.6 EOL — Google APIs warn about it. Upgrade venv to 3.11+ eventually
- [ ] No error handling for Gemini rate limits (429) yet
- [ ] No streaming responses — long answers feel slow
- [ ] Ingestion agent's chunk IDs are Gemini-generated — could occasionally collide if Gemini reuses a common name. Consider appending a short hash.
- [ ] scripts/ingest_standalone_frameworks.py may overlap with populate.py — worth auditing

---

## Brainstorm / Open Questions

- **Teach tab UX**: Should there be a preview step before committing chunks to ChromaDB?
  → Shows chunks before storing: "Does this look right?" → confirm or discard
  → Useful once the knowledge base is large and you care about quality

- **Memory Agent timing**: After every message or only on session end?
  → After every message is safer (crash-proof), but adds background processing
  → BackgroundTasks solves this — response returns first, memory writes async

- **Personal collection quality**: The ingestion agent writes Sudheer's analysis as `personal` chunks.
  → Over time this becomes the richest collection — his unique perspective on everything
  → Should get_profile() search this too, not just background/bio chunks?

- **Cross-collection retrieval**: Currently the three @tool functions search separately.
  → Could add a search_all() tool that searches knowledge + frameworks + personal in one call
  → Useful for "what do I know about X?" type questions

- **Conversation history persistence**: Currently lives only in the browser.
  → Phase 3 Memory Agent will extract key moments → `episodes` collection
  → Eventually: Friday remembers past conversations, references them when relevant

- **Voice interface**:
  → Gemini supports audio natively. Could add a `/voice` endpoint later.
