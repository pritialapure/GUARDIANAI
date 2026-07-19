# Guardian Council AI

**An Agentic AI Emergency Decision Support System.**

Multi-agent orchestration (LangGraph) + Retrieval-Augmented Generation (ChromaDB)
+ Google Gemini 2.5 Flash, built for emergency responders who need fast,
grounded, structured incident response plans.

> **Status: All 7 build phases complete.** Full-stack, end-to-end functional.

---

## Tech Stack

| Layer      | Technology                                      |
|------------|--------------------------------------------------|
| Frontend   | React + Vite + TailwindCSS v4                    |
| Backend    | Python + FastAPI                                 |
| AI         | Google Gemini 2.5 Flash via LangChain            |
| Orchestration | LangGraph                                     |
| Vector DB  | ChromaDB                                         |
| Embeddings | Gemini Embeddings (HuggingFace fallback)         |
| PDF Loader | PyPDFLoader                                      |
| Splitter   | RecursiveCharacterTextSplitter                   |

---

## Project Structure

```
guardian-council-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint
│   │   ├── config/             # Settings (pydantic-settings)
│   │   ├── routes/             # health, chat, ingest, agents, documents, report
│   │   ├── agents/             # Coordinator, Classification, RAG Retrieval, Planning, Validation, Memory
│   │   ├── rag/                 # Loader, splitter, embeddings, retriever, ingestion, QA pipeline
│   │   ├── graph/               # LangGraph StateGraph (workflow.py)
│   │   ├── memory/              # Conversation checkpointer (in-memory / SQLite)
│   │   ├── prompts/             # RAG + agent system prompt templates
│   │   ├── mcp/                 # Weather, Maps, Hospital/Fire/Police finders, Contacts, GPS
│   │   ├── models/              # Internal domain models
│   │   ├── schemas/             # Pydantic request/response + agent-output schemas
│   │   ├── services/            # chat, ingestion, agent_status, documents, report
│   │   └── utils/               # Logger, exceptions, helpers
│   ├── knowledge_base/          # Drop PDFs here for ingestion
│   ├── chroma_db/                # Persisted vector store (generated)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css             # Tailwind v4 + dark command-center theme tokens
│   │   ├── pages/Dashboard.jsx   # Full layout: sidebar + chat + status panels
│   │   ├── components/           # Sidebar, ChatWindow, MessageBubble, AgentPipeline,
│   │   │                         # AgentStatusPanel, KnowledgeBaseStatus, QuickPrompts
│   │   ├── hooks/useChat.js      # Conversation state, typing animation, pipeline state
│   │   ├── services/api.js       # Fetch wrappers for all 6 backend endpoints
│   │   └── constants/dashboard.js
│   ├── vite.config.js            # Tailwind plugin + /api proxy to :8000
│   └── .env.example
└── .gitignore
```

---

## Installation & Running

### Requirements
- **Python 3.11 or 3.12** (not 3.13 — `chromadb` and parts of the ML stack have known build failures on 3.13). Check your version with `python --version`.
- Node.js 18+

### Backend — Windows (PowerShell)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```
If PowerShell blocks the activation script, run this once first:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```
Your prompt should now start with `(.venv)` — that confirms the venv is active. Then:
```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
```
Open `.env` and set `GOOGLE_API_KEY`, then:
```powershell
uvicorn app.main:app --reload --port 8000
```

### Backend — macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then edit GOOGLE_API_KEY
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API docs.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # Windows: Copy-Item .env.example .env
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api/*` requests
to `http://localhost:8000`.

---

## Environment Variables

See `backend/.env.example` and `frontend/.env.example` for the full list.
At minimum you need:

- `GOOGLE_API_KEY` — Google Gemini API key
- `TAVILY_API_KEY` — optional, enables live web search in the Tool Agent
- MCP placeholder keys (`WEATHER_API_KEY`, `MAPS_API_KEY`, `HOSPITAL_FINDER_API_KEY`)
  can stay blank in development; tools degrade gracefully.

---

## Adding PDFs to the Knowledge Base

1. Drop trusted disaster-management PDFs into `backend/knowledge_base/`.
2. Run the ingestion CLI from inside `backend/`:

   ```bash
   python -m app.scripts.ingest_cli
   ```

   Add `--force` to re-embed files that are already indexed (e.g. after
   replacing a PDF with an updated version but keeping the same filename).

3. The pipeline (`app/rag/loader.py` → `splitter.py` → `embeddings.py` →
   `vector_store.py`) automatically picks up any PDF in that folder — no
   code changes required. Already-indexed files are skipped on re-runs.
4. Query the knowledge base directly (used internally by the RAG Retrieval
   Agent in Phase 3):

   ```python
   from app.rag.qa_pipeline import ask_knowledge_base
   result = ask_knowledge_base("What should responders do during a flood?")
   print(result.answer)
   print(result.source_references)
   ```

**Embedding provider:** Gemini embeddings are used by default
(`EMBEDDING_PROVIDER=gemini`). If you hit quota/compatibility issues, set
`EMBEDDING_PROVIDER=huggingface` in `.env` — no other code changes needed,
since every module calls the shared `get_embedding_function()`.

---

## Project Workflow

Once your `.env` and knowledge base are set up, run one full conversation
turn through the agent graph directly (this is exactly what the `/chat`
route will call in Phase 6):

```python
from app.graph.workflow import invoke_workflow

result = invoke_workflow(
    user_query="There is a gas leak smell in my kitchen",
    thread_id="demo-session-1",
)
print(result["final_response"])
print(result.get("emergency_type"))
print(result.get("final_report"))
```

The same `thread_id` on a later call continues the same conversation —
prior turns are automatically restored from the checkpointer.

**Flow:** `Coordinator` decides if this is a real emergency. If not, a
`Simple Response` is returned directly. If it is, `Classification` tags
the emergency type, `RAG Retrieval` pulls trusted context, `Planning`
drafts a grounded action plan, `Validation` checks every recommendation
against that context (retrying planning once if it fails), and the
`Report Generator` produces the final structured report and responder
message. `Memory` records the turn either way.

---

## MCP Tools

Seven modular tools live in `backend/app/mcp/`, each implementing the same
`MCPTool` interface (`app/mcp/base.py`) so the Tool Agent can call any of
them uniformly:

| Tool | Purpose | Real API (when key is set) |
|---|---|---|
| `weather_tool` | Current conditions at a location | OpenWeatherMap (`WEATHER_API_KEY`) |
| `hospital_finder_tool` | Nearest hospitals | Google Places (`MAPS_API_KEY`) |
| `police_finder_tool` | Nearest police stations | Google Places (`MAPS_API_KEY`) |
| `fire_station_finder_tool` | Nearest fire stations | Google Places (`MAPS_API_KEY`) |
| `maps_tool` | Route distance / ETA between two points | Google Directions (`MAPS_API_KEY`) |
| `emergency_contacts_tool` | Correct police/fire/medical numbers by country | Built-in static directory |
| `gps_location_tool` | Reverse-geocode lat/lng into an address | Google Geocoding (`MAPS_API_KEY`) |

**Every tool works with zero API keys configured** — it returns clearly
labeled placeholder data (`is_live: false`) with the exact same shape a
real response would have, so the rest of the app never has to special-case
"no key yet." Add the relevant key to `.env` and the tool automatically
switches to live data (`is_live: true`) — no other code changes needed.

The **Tool Agent** (`app/agents/tool_agent.py`) sits between RAG Retrieval
and Planning in the graph. It picks which tools are relevant based on the
classified `emergency_type` (e.g. Medical → hospital finder, Violence →
police finder) and calls them automatically; results feed into both the
Planning Agent (for concrete resource recommendations) and the final
incident report.

---

## API Endpoints

Visit `http://localhost:8000/docs` for the full interactive schema. Summary:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check + config/index status |
| `POST` | `/chat` | Send a message; runs the full LangGraph workflow |
| `POST` | `/ingest` | Ingest new PDFs from `knowledge_base/` |
| `GET` | `/agents` | List all agents + registered MCP tools |
| `GET` | `/documents` | Indexed vs. pending knowledge base files |
| `POST` | `/report` | Fetch the final incident report for a `thread_id` |

Example `/chat` request:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "There is a gas leak smell in my kitchen", "thread_id": "session-1"}'
```

---

## Deployment

### Fastest path: Render (backend) + Vercel (frontend), both free tier

**1. Push to GitHub** (if not already):
```bash
git init
git add .
git commit -m "Guardian Council AI"
git remote add origin <your-repo-url>
git push -u origin main
```
Your PDFs in `backend/knowledge_base/` get committed (that's intentional —
see below). `chroma_db/`, `.venv/`, `.env`, and `node_modules/` are already
excluded via `.gitignore`.

**2. Backend on Render:**
- Go to render.com → New → Blueprint → connect your repo. It will detect
  `render.yaml` at the repo root and pre-fill everything.
- When prompted, set the `GOOGLE_API_KEY` secret (your Gemini key) and
  `ALLOWED_ORIGINS` (leave blank for now — you'll fill this in after step 3
  once you have your frontend URL, then redeploy).
- Deploy. **Cold-disk platforms wipe local files on restart** — the app
  handles this automatically: on every startup it re-ingests any PDFs in
  `knowledge_base/` in the background (see `_start_background_ingestion`
  in `app/main.py`), so the knowledge base rebuilds itself with zero manual
  steps. `EMBEDDING_PROVIDER=huggingface` is set in `render.yaml` by default
  so this doesn't hit Gemini's embedding rate limits on every restart.
- Once live, note your backend URL, e.g. `https://guardian-council-ai-backend.onrender.com`.

**3. Frontend on Vercel:**
- Go to vercel.com → New Project → import your repo → set **Root Directory**
  to `frontend`.
- Framework preset: Vite. Build command `npm run build`, output `dist`
  (Vercel usually detects this automatically).
- Add environment variable `VITE_API_BASE_URL` = your Render backend URL
  from step 2.
- Deploy. Note your frontend URL, e.g. `https://guardian-council-ai.vercel.app`.

**4. Close the loop:** go back to Render → your backend service →
Environment → set `ALLOWED_ORIGINS` to your Vercel URL from step 3 →
redeploy. This is what makes CORS allow your live frontend to call the API.

**First request after a cold start may be slow** (free tier spins down
after inactivity, and background ingestion needs a minute to finish on
first boot) — this is normal, not a bug.

### Fallback if you're out of time: run locally + tunnel

```bash
# backend running locally (uvicorn ... --port 8000)
npx localtunnel --port 8000
# frontend running locally (npm run dev), separately:
npx localtunnel --port 5173
```
Gives you two temporary public URLs without any cloud setup. Good enough
for a live demo if deployment isn't working with time running out.

---

## Roadmap (build order)

1. ✅ Architecture, folder structure, environment, FastAPI + React scaffolding
2. ✅ Knowledge base: loader, chunking, embeddings, ChromaDB, retriever
3. ✅ Agents: Coordinator, Classification, Memory, RAG Retrieval, Planning, Validation, Report Generator, Simple Response
4. ✅ LangGraph workflow wiring all agents together
5. ✅ MCP tools: Weather, Maps, Hospital/Fire/Police finders, Emergency Contacts, GPS
6. ✅ FastAPI routes, schemas, services
7. ✅ React dashboard: sidebar, chat UI, agent pipeline visual, KB status, quick prompts
8. ⏳ Testing, final README, verification pass

---

## License

Hackathon project — internal use.
