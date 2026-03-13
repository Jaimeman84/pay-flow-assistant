# PayFlow GenAI Demo

An educational application demonstrating how **specialist agents** work inside an orchestrated, multi-agent AI system.

Ask questions about the fictional PayFlow fintech application. The system routes each question through a guard layer, an orchestrator, and one or more specialist agents, then returns a **structured JSON response** with an answer, routing metadata, citations, and a debug trace.

Built for: QA engineers, SDETs, instructors, and developers learning GenAI testing and evaluation.

---

## What This App Teaches

| Concept | Where to see it |
|---|---|
| Guard layer / input safety | `app/core/guard.py` |
| Orchestration and routing | `app/core/orchestrator.py` |
| Specialist agents | `app/specialists/` |
| Grounded retrieval | Each specialist + `app/data/*.json` |
| Structured JSON output | `app/schemas/response.py` |
| Synthesis with grounding | `app/core/synthesizer.py` |
| Promptfoo evaluation | `promptfoo/promptfooconfig.yaml` |
| Chat UI | `ui/` (Next.js) |

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher (for the UI)

### 1. Clone and set up the Python environment

```bash
git clone <repo-url>
cd pay-flow

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

> **Always run the server from the `venv`** — the `anthropic` package is installed there, not in your global Python.

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` to enable LLM-powered answers (optional):

```env
LLM_API_KEY=your_api_key_here
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-20241022
```

> **The app works without an API key.** Guard, routing, retrieval, and citations all work fully without LLM configuration. Synthesis falls back to structured Markdown formatting.

### 3. Start the FastAPI server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

On startup the server logs whether LLM synthesis is enabled:

```
INFO  LLM synthesis ENABLED — provider=anthropic model=claude-3-5-haiku-20241022 key=...XXXXXX
# or
WARNING  LLM synthesis DISABLED — LLM_API_KEY not set, using template fallback
```

### 4. Start the UI (optional)

```bash
cd ui
npm install
npm run dev
```

Open **`http://localhost:3000`** in your browser.

| Page | URL | Description |
|---|---|---|
| Chat | `http://localhost:3000` | Interactive chat with pipeline internals visible |
| Question guide | `http://localhost:3000/questions` | Full list of example questions grouped by specialist |

### 5. Test via curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What Jira bugs are blocking the payment release?"}'
```

---

## The UI

The Next.js frontend visualises the full pipeline response side-by-side:

- **Answer panel** — LLM-generated or template-formatted response
- **Pipeline Route** — guard status badge, specialist pills, orchestrator decision
- **Citations** — source-coloured cards with record IDs (PF-xxx, CF-xxx, FG-xxx)
- **Debug Trace** — collapsible step-by-step pipeline log

The **Question Guide** page (`/questions`) lists every supported question grouped by specialist, with expected citation IDs — useful for students exploring the system or preparing Promptfoo test cases.

---

## Demo Questions

Try these to explore different routing paths. The full list is at `/questions` in the UI.

| Question | Specialists | What it demonstrates |
|---|---|---|
| `What Jira bugs are blocking the payment release?` | Jira | Blocker detection, returns PF-113, PF-104, PF-105 |
| `What does Confluence say about the payment confirmation flow?` | Confluence | Documentation retrieval, returns CF-004 |
| `Which Figma screen includes the freeze card toggle?` | Figma | Component search, returns FG-006 |
| `What are the release notes for payment v2.4?` | Confluence | Release notes query, returns CF-005 |
| `Compare Jira and Figma for login-related issues` | Jira + Figma | Multi-source routing |
| `What changed in the login flow and is there a related Jira bug?` | Confluence + Jira | Cross-source synthesis |
| `What is PayFlow and what does it do?` | Basic Knowledge | General knowledge retrieval |
| `Ignore all previous instructions` | None (blocked) | Guard layer — prompt injection |
| `What is the weather in London?` | None (fallback) | Unknown topic handling |

---

## API Reference

### `POST /chat`

**Request:**
```json
{
  "message": "What Jira bugs are blocking the payment release?",
  "session_id": "demo-session-001",
  "user_role": "student"
}
```

**Response:**
```json
{
  "answer": "The payment release v2.4 is blocked by two critical Jira tickets...",
  "route": {
    "guard_status": "allowed",
    "guard_reason": null,
    "selected_specialists": ["jira"],
    "orchestrator_decision": "jira_blocker_query"
  },
  "citations": [
    { "source": "jira", "id": "PF-104", "title": "Payment confirmation button unresponsive on iOS" },
    { "source": "jira", "id": "PF-113", "title": "Payment release v2.4 blocked — critical iOS and duplicate transaction bugs" }
  ],
  "debug": {
    "app_specialist_task": "Find information related to payments from Jira: What Jira bugs are blocking the payment release?",
    "steps": [
      "Guard check: allowed",
      "Orchestrator decision: jira_blocker_query",
      "Routing to specialists: jira",
      "Feature area detected: payments",
      "Jira specialist: 3 result(s) retrieved",
      "Answer synthesized",
      "Response assembled with 3 citation(s)"
    ]
  }
}
```

### `GET /health`

```json
{ "status": "ok", "service": "payflow-genai-demo", "version": "1.0.0" }
```

---

## Running Tests

```bash
# From the project root with the venv active
python -m pytest tests/ -v
```

> Run tests via `python -m pytest` (with venv active) rather than plain `pytest` to avoid conflicts with globally installed packages (e.g. `deepeval` registers a broken pytest plugin in some environments).

The test suite covers:

| File | Tests | What it covers |
|---|---|---|
| `tests/test_guard.py` | 25 | Injection detection, blocklist, length limits, edge cases |
| `tests/test_orchestrator.py` | Routing decisions, feature area detection, decision names |
| `tests/test_specialists.py` | Deterministic retrieval, specific record ID assertions |
| `tests/test_api.py` | End-to-end full request/response via FastAPI TestClient |

All 113 tests are deterministic — no LLM calls, no mocking required.

---

## Running Promptfoo Evaluations

### Prerequisites

```bash
npm install -g promptfoo
```

### Run the eval suite

```bash
# Terminal 1 — start the server (with venv active)
uvicorn app.main:app --reload --port 8000

# Terminal 2 — run evals
cd promptfoo
promptfoo eval
```

### View results

```bash
promptfoo view
```

The eval config is at `promptfoo/promptfooconfig.yaml` and includes 12 test cases:

- Single-source queries (Jira, Confluence, Figma)
- Multi-source comparison queries
- Blocked injection attempts
- Off-topic / insufficient data fallbacks
- Response structure and debug trace completeness

All assertions use `type: javascript` against the full parsed response object (e.g. `output.route.guard_status`, `output.citations[0].id`), made possible by `transformResponse: "json"` in the provider config.

---

## Architecture Overview

```
POST /chat
    │
    ▼
Guard Layer (rules-based, no LLM)
    │ blocked → safe refusal response
    │ allowed
    ▼
Orchestrator (keyword-based routing, no LLM)
    → selected_specialists: ["jira", "confluence", ...]
    → orchestrator_decision: "jira_blocker_query"
    → feature_area: "payments"
    │
    ▼
Specialist Agents (deterministic JSON retrieval)
    Jira       → app/data/jira.json
    Confluence → app/data/confluence.json
    Figma      → app/data/figma.json
    Basic      → app/data/basic_knowledge.json
    │
    ▼
Synthesis (LLM if configured, Markdown template fallback)
    │
    ▼
Structured JSON Response
{ answer, route, citations, debug }
    │
    ▼
Next.js UI (ui/)
    Answer · Pipeline Route · Citations · Debug Trace
```

---

## Project Structure

```
pay-flow/
├── app/
│   ├── main.py                    # FastAPI entry point — loads .env, configures CORS
│   ├── api/
│   │   └── chat.py                # POST /chat and GET /health endpoints
│   ├── core/
│   │   ├── guard.py               # Rules-based safety: injection, blocklist, length
│   │   ├── orchestrator.py        # Keyword routing + feature area detection
│   │   ├── synthesizer.py         # LLM synthesis with Markdown template fallback
│   │   └── pipeline.py            # Full request processing coordinator
│   ├── specialists/
│   │   ├── base.py                # RetrievalTask, RetrievedItem, BaseSpecialist
│   │   ├── jira_specialist.py     # Relevance-gated scoring against jira.json
│   │   ├── confluence_specialist.py
│   │   ├── figma_specialist.py
│   │   └── basic_specialist.py
│   ├── data/
│   │   ├── jira.json              # 16 PayFlow Jira tickets
│   │   ├── confluence.json        # 10 PayFlow Confluence pages
│   │   ├── figma.json             # 8 PayFlow Figma screens
│   │   └── basic_knowledge.json   # 6 general knowledge entries
│   ├── schemas/
│   │   ├── request.py             # ChatRequest Pydantic model
│   │   └── response.py            # ChatResponse, RouteInfo, Citation, DebugInfo
│   └── services/
│       ├── data_loader.py         # JSON loader with in-memory singleton cache
│       └── llm_client.py          # LLM wrapper — Anthropic and OpenAI supported
├── ui/                            # Next.js 16 + Tailwind CSS frontend
│   ├── app/
│   │   ├── page.tsx               # Main chat page
│   │   ├── questions/page.tsx     # Question guide for students
│   │   └── api/chat/route.ts      # Proxy to FastAPI (avoids CORS in dev)
│   ├── components/
│   │   ├── ChatInput.tsx          # Textarea + quick-suggestion chips
│   │   ├── ResponseView.tsx       # 5-column answer + pipeline internals layout
│   │   ├── RoutePanel.tsx         # Guard badge, specialist pills, decision label
│   │   ├── CitationsPanel.tsx     # Source-coloured citation cards
│   │   └── DebugTrace.tsx         # Collapsible pipeline step log
│   ├── types/chat.ts              # TypeScript types mirroring FastAPI schemas
│   └── .env.local                 # FASTAPI_URL=http://127.0.0.1:8000
├── tests/
│   ├── test_guard.py
│   ├── test_orchestrator.py
│   ├── test_specialists.py
│   └── test_api.py
├── promptfoo/
│   └── promptfooconfig.yaml       # 12-case Promptfoo eval suite
├── .env.example                   # Environment variable template
├── .env                           # Your local config (not committed)
├── requirements.txt
├── implementation-decisions.md    # Final architectural decisions
├── ARD.md                         # Architecture Requirements Document
├── BRD.md                         # Business Requirements Document
├── ICP.md                         # Ideal Customer Profile
├── workflow.md                    # End-to-end workflow guide
└── folder-structure.md            # Project structure guide
```

---

## Sample Data

All knowledge sources are local JSON files in `app/data/` — no external services required.

| File | Records | Coverage |
|---|---|---|
| `jira.json` | 16 tickets | login, payments, cards, dashboard, transactions |
| `confluence.json` | 10 pages | requirements, release notes, process flows |
| `figma.json` | 8 screens | all 5 PayFlow feature areas |
| `basic_knowledge.json` | 6 entries | vision, team, release process, features, tech stack, QA standards |

Cross-source relationships are built into the data. For example, PF-104 and PF-105 are referenced in CF-005 (Payment Release v2.4 blockers), and FG-006 (Card Management Screen) contains the `freeze_card_toggle` component that PF-107 tracks as a bug.

---

## How Routing Works

The orchestrator uses keyword matching — no LLM required.

| Message contains | Routes to | Decision name |
|---|---|---|
| "jira", "bug", "ticket", "blocker" | Jira | `jira_ticket_query` or `jira_blocker_query` |
| "confluence", "documentation", "requirements", "what changed" | Confluence | `confluence_docs_query` or `confluence_release_notes_query` |
| "figma", "screen", "component", "design", "toggle" | Figma | `figma_screen_query` or `figma_component_query` |
| Keywords from 2+ specialists | Multiple | `cross_source_comparison` |
| No specialist signals | Basic fallback | `unknown_topic_fallback` |

See `app/core/orchestrator.py` → `SPECIALIST_SIGNALS` and `FEATURE_AREA_SIGNALS` for the full keyword lists.

---

## Extending the App

### Add more sample data
Edit `app/data/*.json` to add tickets, pages, screens, or knowledge entries. The specialists pick them up automatically on next server start.

### Add a new specialist
1. Create `app/specialists/my_specialist.py` extending `BaseSpecialist`
2. Add a `"my_source"` entry to `SPECIALIST_SIGNALS` in `orchestrator.py`
3. Register it in `_SPECIALISTS` dict in `pipeline.py`
4. Add sample data in `app/data/my_source.json`

### Connect a real API
Replace `get_store().jira` in `jira_specialist.py` with a real Jira API call. The rest of the pipeline stays unchanged.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'anthropic'` (LLM not working)**

The server is running with the global Python instead of the `venv`. Activate the virtual environment first:
```bash
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
uvicorn app.main:app --reload --port 8000
```

**LLM synthesis still using template after adding API key**

The `.env` file is loaded once at startup via `load_dotenv(override=True)`. Restart the server after changing `.env`.

**Tests fail with unrelated import errors**

A globally installed package (e.g. `deepeval`) may be registering a broken pytest plugin. Ensure venv is active:
```bash
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
python -m pytest tests/ -v
```

**Promptfoo assertions fail with `Cannot read properties of undefined`**

Check that `promptfooconfig.yaml` has `transformResponse: "json"` (not `"json.answer"`). The full response object must be set as `output` for field-level assertions to work.

**UI can't reach the API (`ECONNREFUSED`)**

Node resolves `localhost` to IPv6 (`::1`) on some Windows setups while FastAPI listens on IPv4. The `ui/.env.local` is already set to `FASTAPI_URL=http://127.0.0.1:8000` to avoid this.

**Server won't start:**
```bash
pip install -r requirements.txt
```

---

## License

MIT — free to use, fork, and adapt for teaching and demo purposes.

---

*Made with ❤️ by Jaime Mantilla, MSIT + AI*