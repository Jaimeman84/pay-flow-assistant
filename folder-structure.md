# folder-structure.md — Recommended Project Structure

**Project:** PayFlow GenAI Demo
**Version:** 1.0 (MVP)
**Stack:** Python + FastAPI

---

## 1. Overview

This document defines the recommended folder structure for implementing the PayFlow GenAI Demo. The structure is designed with three priorities:

1. **Teachability** — Every folder and file should have a clear, singular purpose that is easy to explain
2. **Separation of concerns** — Guard, orchestration, specialist, synthesis, and data layers are isolated
3. **Extensibility** — The structure should make it easy to swap sample data for real integrations later

---

## 2. Full Project Tree

```
payflow-genai-demo/
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   │
│   ├── api/                      # API layer — route definitions only
│   │   ├── __init__.py
│   │   └── chat.py               # POST /chat and GET /health endpoints
│   │
│   ├── core/                     # Core system components
│   │   ├── __init__.py
│   │   ├── guard.py              # Guard layer: rules + LLM safety checks
│   │   ├── orchestrator.py       # Institutional knowledge orchestrator
│   │   ├── app_specialist.py     # PayFlow domain app specialist
│   │   └── synthesizer.py        # Synthesis service: merge + answer generation
│   │
│   ├── specialists/              # Specialist agents — one file per agent
│   │   ├── __init__.py
│   │   ├── base.py               # Base specialist interface / abstract class
│   │   ├── jira_specialist.py    # Jira specialist agent
│   │   ├── confluence_specialist.py  # Confluence specialist agent
│   │   ├── figma_specialist.py   # Figma specialist agent
│   │   └── basic_knowledge_specialist.py  # Basic knowledge fallback agent
│   │
│   ├── data/                     # Sample knowledge source data files
│   │   ├── jira.json             # PayFlow Jira ticket data
│   │   ├── confluence.json       # PayFlow Confluence page data
│   │   ├── figma.json            # PayFlow Figma screen data
│   │   └── basic_knowledge.json  # PayFlow general knowledge data
│   │
│   ├── schemas/                  # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── request.py            # ChatRequest schema
│   │   └── response.py           # ChatResponse, RouteInfo, Citation, Debug schemas
│   │
│   └── services/                 # Shared utility services
│       ├── __init__.py
│       ├── llm_client.py         # LLM API wrapper (Claude / OpenAI)
│       └── data_loader.py        # JSON data file loader and cache
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_guard.py             # Unit tests for guard layer
│   ├── test_orchestrator.py      # Unit tests for orchestrator routing
│   ├── test_specialists.py       # Unit tests for each specialist agent
│   ├── test_synthesizer.py       # Unit tests for synthesis service
│   ├── test_api.py               # Integration tests for POST /chat endpoint
│   └── fixtures/                 # Shared test fixtures
│       ├── sample_requests.py    # Sample ChatRequest objects
│       └── sample_data.py        # Minimal in-memory data for tests
│
├── promptfoo/                    # Promptfoo evaluation configuration
│   ├── promptfoo.yaml            # Main Promptfoo config (provider + tests)
│   ├── prompts/                  # Test prompt files (optional)
│   │   └── demo_questions.txt    # One question per line
│   └── results/                  # Output directory for eval results (gitignored)
│
├── docs/                         # Project documentation
│   ├── ARD.md                    # Architecture Requirements Document
│   ├── BRD.md                    # Business Requirements Document
│   ├── ICP.md                    # Ideal Customer Profile
│   ├── workflow.md               # End-to-end workflow guide
│   └── folder-structure.md       # This file
│
├── .env.example                  # Example environment variable file
├── .env                          # Local environment variables (gitignored)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # Setup and usage guide
└── Makefile                      # Common dev commands (optional but helpful)
```

---

## 3. File-by-File Explanation

### `app/main.py`

**Purpose:** Entry point for the FastAPI application. Creates the app instance, registers routers, and sets up CORS and startup configuration.

**Contents:**
- FastAPI app instantiation
- Router registration (`app.include_router(chat_router)`)
- CORS middleware configuration
- Startup event to pre-load JSON data files

**Teaching note:** This file should be minimal. Students should see that the app is just configuration — logic lives in other layers.

---

### `app/api/chat.py`

**Purpose:** Defines the HTTP endpoints. Receives the request, calls the pipeline, and returns the response. Contains no business logic.

**Contents:**
- `POST /chat` — receives `ChatRequest`, calls pipeline, returns `ChatResponse`
- `GET /health` — returns `{ "status": "ok" }`

**Teaching note:** This file teaches the separation between API routing and business logic. Students should see that the endpoint does almost nothing except delegate.

---

### `app/core/guard.py`

**Purpose:** Implements the guard layer. All safety and input validation logic lives here.

**Contents:**
- `check_message(message: str) -> GuardResult`
- Rules-based checks: length, blocklist keywords, injection regex patterns
- Optional LLM classification call for borderline inputs
- Returns `{ guard_status, guard_reason }`

**Teaching note:** This file is a great starting point for student exercises — add a new blocklist keyword, add a new injection pattern, observe the effect.

---

### `app/core/orchestrator.py`

**Purpose:** Implements the LLM orchestrator. Takes the user message and returns a routing decision.

**Contents:**
- `route_message(message: str) -> RoutingDecision`
- LLM call with routing system prompt (includes few-shot examples)
- Parses LLM output into `{ selected_specialists, orchestrator_decision }`

**Teaching note:** This file demonstrates how an LLM can make routing decisions. Students can inspect the system prompt and understand what instructions drive the routing.

---

### `app/core/app_specialist.py`

**Purpose:** Implements the PayFlow domain specialist. Adds product context to the routing decision before dispatching to data specialists.

**Contents:**
- `build_task(message: str, routing: RoutingDecision) -> TaskDescription`
- LLM call with PayFlow domain system prompt
- Maps intent to PayFlow feature areas (login, payments, cards, dashboard, transactions)
- Returns `{ feature_area, task }`

**Teaching note:** This file shows how domain knowledge is injected into the pipeline. Students can modify the system prompt to expand or restrict the domain.

---

### `app/core/synthesizer.py`

**Purpose:** Merges specialist results and generates the final grounded answer.

**Contents:**
- `synthesize(task: TaskDescription, results: list[SpecialistResult]) -> SynthesisOutput`
- Builds context block from all specialist results
- LLM call with grounding prompt (strict: only use retrieved data)
- Returns `{ answer, citations }`

**Teaching note:** This file demonstrates grounding. Students can test what happens when no data is retrieved (should produce "I don't have information about that" — not a hallucination).

---

### `app/specialists/base.py`

**Purpose:** Defines the abstract base class that all specialist agents must implement.

**Contents:**
```python
from abc import ABC, abstractmethod

class BaseSpecialist(ABC):
    source_name: str

    @abstractmethod
    def retrieve(self, task: TaskDescription) -> list[SpecialistResult]:
        """Query the knowledge source and return matching results."""
        ...
```

**Teaching note:** This file teaches interface design. Students can see that all specialists share the same contract, which makes them interchangeable.

---

### `app/specialists/jira_specialist.py`

**Purpose:** Retrieves Jira ticket data matching the task description.

**Contents:**
- Loads `data/jira.json`
- `retrieve(task)` — filters by `feature_area`, `status`, `priority`, keyword in `title`/`summary`
- Returns list of `SpecialistResult` objects with `source="jira"`

---

### `app/specialists/confluence_specialist.py`

**Purpose:** Retrieves Confluence page data matching the task description.

**Contents:**
- Loads `data/confluence.json`
- `retrieve(task)` — filters by `feature_area`, `type`, keyword in `title`/`content`
- Returns list of `SpecialistResult` objects with `source="confluence"`

---

### `app/specialists/figma_specialist.py`

**Purpose:** Retrieves Figma screen data matching the task description.

**Contents:**
- Loads `data/figma.json`
- `retrieve(task)` — filters by `feature_area`, keyword in `screen_name`, `components`, `design_notes`
- Returns list of `SpecialistResult` objects with `source="figma"`

---

### `app/specialists/basic_knowledge_specialist.py`

**Purpose:** Fallback agent for general institutional knowledge.

**Contents:**
- Loads `data/basic_knowledge.json`
- `retrieve(task)` — keyword match in `topic`, `content`, `tags`
- Returns list of `SpecialistResult` objects with `source="basic"`

---

### `app/data/jira.json`

**Purpose:** Sample Jira ticket data for PayFlow. All Jira specialist responses are grounded in this file.

**Schema per record:**
```json
{
  "id": "PF-104",
  "title": "Payment confirmation button unresponsive on iOS",
  "status": "blocked",
  "priority": "critical",
  "feature_area": "payments",
  "assignee": "Jordan Kim",
  "sprint": "Sprint 14",
  "summary": "Users on iOS 16+ cannot complete payment confirmation. Button does not respond to tap events.",
  "blockers": ["PF-098"]
}
```

---

### `app/data/confluence.json`

**Purpose:** Sample Confluence documentation for PayFlow.

**Schema per record:**
```json
{
  "id": "CF-014",
  "title": "Payment Confirmation Flow — Requirements",
  "feature_area": "payments",
  "type": "requirements",
  "content": "The payment confirmation screen must display the recipient name, amount, and a confirmation button. The button must be accessible via keyboard and touch. Confirmation must trigger a transaction record within 2 seconds..."
}
```

---

### `app/data/figma.json`

**Purpose:** Sample Figma screen data for PayFlow.

**Schema per record:**
```json
{
  "id": "FG-003",
  "screen_name": "Card Management Screen",
  "feature_area": "cards",
  "components": ["card_list", "freeze_card_toggle", "report_lost_button", "card_details_panel"],
  "design_notes": "The freeze card toggle is a prominent switch component at the top of each card row. When activated, the card visual dims to indicate frozen state."
}
```

---

### `app/data/basic_knowledge.json`

**Purpose:** General institutional knowledge about PayFlow, its team, and terminology.

**Schema per record:**
```json
{
  "id": "BK-001",
  "topic": "PayFlow Product Vision",
  "content": "PayFlow is a fintech application that enables users to manage payments, track transactions, and control card settings from a single dashboard. The product is targeted at individual consumers and small business owners.",
  "tags": ["product", "vision", "overview"]
}
```

---

### `app/schemas/request.py`

**Purpose:** Pydantic model for the incoming API request.

**Contents:**
```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=1000)
    session_id: str | None = None
    user_role: str = "student"
```

---

### `app/schemas/response.py`

**Purpose:** Pydantic models for the structured API response.

**Contents:**
```python
class Citation(BaseModel):
    source: str
    id: str
    title: str

class RouteInfo(BaseModel):
    guard_status: str
    guard_reason: str | None
    selected_specialists: list[str]
    orchestrator_decision: str | None

class DebugInfo(BaseModel):
    app_specialist_task: str | None
    steps: list[str]

class ChatResponse(BaseModel):
    answer: str
    route: RouteInfo
    citations: list[Citation]
    debug: DebugInfo
```

---

### `app/services/llm_client.py`

**Purpose:** Thin wrapper around the LLM API. All LLM calls in the system go through this module.

**Contents:**
- `complete(system_prompt: str, user_message: str) -> str`
- Reads `LLM_API_KEY` and `LLM_MODEL` from environment
- Handles basic retry logic and timeout

**Teaching note:** Centralizing LLM calls here makes it easy to swap providers (Claude → OpenAI → Ollama) by changing one file.

---

### `app/services/data_loader.py`

**Purpose:** Loads and caches all JSON data files at startup.

**Contents:**
- `load_all() -> DataStore`
- Returns a `DataStore` object with `.jira`, `.confluence`, `.figma`, `.basic` attributes
- Data is loaded once at startup and shared across requests

**Teaching note:** This pattern avoids reading files on every request. It also makes it easy to replace file loading with a database or API call later.

---

### `tests/`

**Purpose:** Test suite for all system components.

**Testing strategy:**
- `test_guard.py` — unit tests: each blocklist pattern, injection regex, length limit, allowable inputs
- `test_orchestrator.py` — unit tests with mocked LLM: verify routing decisions for each query type
- `test_specialists.py` — unit tests: verify each filter condition produces expected results from sample data
- `test_synthesizer.py` — unit tests with mocked LLM: verify grounding logic, empty-data handling
- `test_api.py` — integration tests: send real HTTP requests to the running app

**Naming convention:** Test files mirror the module they test (`guard.py` → `test_guard.py`).

---

### `tests/fixtures/`

**Purpose:** Shared test data and object factories used across multiple test files.

**Contents:**
- `sample_requests.py` — factory functions for `ChatRequest` objects
- `sample_data.py` — minimal in-memory data used by specialist unit tests (avoids reading actual JSON files in unit tests)

---

### `promptfoo/promptfoo.yaml`

**Purpose:** Main Promptfoo configuration file. Connects to the `POST /chat` endpoint and defines test cases.

**Minimum test cases to include:**

| Test Case | Asserts |
|---|---|
| Jira blocker query | `guard_status: allowed`, `selected_specialists` contains `jira`, `citations` non-empty |
| Confluence docs query | `guard_status: allowed`, `selected_specialists` contains `confluence` |
| Figma screen query | `guard_status: allowed`, `selected_specialists` contains `figma` |
| Multi-source query (Jira + Confluence) | Both specialists in `selected_specialists` |
| Blocked injection | `guard_status: blocked`, `citations` empty |
| Off-topic question | `orchestrator_decision: unknown_topic_fallback` |
| No data found | `citations` empty, `answer` contains polite no-data message |

---

### `.env.example`

**Purpose:** Documents all required environment variables without exposing real values.

**Contents:**
```
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=your_api_key_here
APP_ENV=development
LOG_LEVEL=INFO
```

---

### `requirements.txt`

**Purpose:** Python dependencies for the project.

**Minimum contents:**
```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.6.0
python-dotenv>=1.0.0
anthropic>=0.25.0     # or openai>=1.0.0
httpx>=0.27.0         # for async HTTP in tests
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

### `Makefile`

**Purpose:** Developer shortcuts for common tasks.

**Recommended targets:**
```makefile
run:
    uvicorn app.main:app --reload --port 8000

test:
    pytest tests/ -v

eval:
    cd promptfoo && promptfoo eval

install:
    pip install -r requirements.txt

lint:
    ruff check app/ tests/
```

---

## 4. Naming Conventions

| Convention | Rule |
|---|---|
| Python files | `snake_case.py` |
| Python classes | `PascalCase` |
| Python functions | `snake_case()` |
| JSON data fields | `snake_case` |
| JSON record IDs | Source prefix + number (e.g., `PF-104`, `CF-014`, `FG-003`, `BK-001`) |
| Specialist class names | `{Source}Specialist` (e.g., `JiraSpecialist`) |
| Test files | `test_{module_name}.py` |
| Promptfoo test descriptions | Lowercase, descriptive (e.g., `"jira blocker query returns allowed status"`) |

---

## 5. What Goes Where — Quick Reference

| Concern | Location |
|---|---|
| HTTP routing | `app/api/` |
| Guard logic | `app/core/guard.py` |
| Orchestration / routing | `app/core/orchestrator.py` |
| Domain context (PayFlow) | `app/core/app_specialist.py` |
| Answer generation | `app/core/synthesizer.py` |
| Data retrieval per source | `app/specialists/` |
| Sample knowledge data | `app/data/` |
| Request/response schemas | `app/schemas/` |
| LLM API calls | `app/services/llm_client.py` |
| Data file loading | `app/services/data_loader.py` |
| Unit and integration tests | `tests/` |
| AI evaluation tests | `promptfoo/` |
| Project documentation | `docs/` |
| Environment config | `.env` / `.env.example` |

---

## 6. Future-Ready Folders

These folders do not exist in the MVP but are the natural next additions as the project grows:

```
payflow-genai-demo/
│
├── app/
│   ├── integrations/             # Future: live Jira, Confluence, Figma API clients
│   │   ├── jira_client.py
│   │   ├── confluence_client.py
│   │   └── figma_client.py
│   │
│   ├── memory/                   # Future: conversation history / session context
│   │   └── session_store.py
│   │
│   └── vector_store/             # Future: semantic search with ChromaDB or Pinecone
│       └── embeddings.py
│
├── frontend/                     # Future: React or Streamlit UI
│   └── ...
│
└── docker/                       # Future: containerized deployment
    ├── Dockerfile
    └── docker-compose.yml
```

**Teaching note:** Showing students these future folders helps them see how the MVP architecture scales without requiring them to implement all of it upfront.
