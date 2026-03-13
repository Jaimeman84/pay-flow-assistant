# ARD.md — Architecture Requirements Document

**Project:** PayFlow GenAI Demo
**Version:** 1.0 (MVP)
**Status:** Draft
**Audience:** Developers, Instructors, Students

---

## 1. Document Purpose

This Architecture Requirements Document (ARD) defines the technical architecture, component responsibilities, and system requirements for the PayFlow GenAI Demo — a teaching application that demonstrates how specialist agents work inside an orchestrated, multi-agent AI system.

The document is intended to guide implementation and serve as a reference for instructors and students learning about:
- Agentic AI architecture
- Guardrail and safety layers
- Orchestration and routing logic
- Specialist agent design
- Grounded, structured AI responses
- Evaluation with Promptfoo

---

## 2. System Overview

PayFlow is a fictional fintech application used as the product domain for this demo. The GenAI assistant built on top of PayFlow allows users to ask natural language questions about project data spanning Jira-style tickets, Confluence-style documentation, Figma-style design screens, and general institutional knowledge.

The system accepts a user question via a REST API, runs it through a guard layer, routes it through an orchestrator and app specialist, dispatches to one or more specialist agents, retrieves grounded data from local JSON files, and returns a structured JSON response.

**Core capabilities demonstrated:**
- Input safety and guardrail enforcement
- LLM-based orchestration and routing
- Deterministic specialist retrieval from sample data
- Multi-source synthesis and citation
- Structured JSON output designed for evaluation
- Promptfoo-compatible API endpoint

---

## 3. Architecture Goals

| Goal | Description |
|---|---|
| Educational clarity | Every component should be easy to explain and understand in a classroom or demo context |
| Determinism where possible | Specialist retrieval should use keyword/filter logic, not probabilistic search, for predictable eval results |
| Structured outputs | All API responses must return structured JSON, not plain prose only |
| Guardrails first | Safety checks run before any LLM processing |
| Grounded answers | All answers must cite specific data from the sample knowledge sources |
| Promptfoo compatibility | The API must support automated evaluation using Promptfoo |
| Extensibility | Architecture should make it easy to swap mock data for live integrations later |
| Observability | Every routing decision and step must be traceable in the response |

---

## 4. Scope of MVP

The MVP includes:

- A single REST endpoint: `POST /chat`
- A rules-based + LLM hybrid guard layer
- An LLM-based orchestrator that selects specialists
- An app specialist (PayFlow domain context)
- Three specialist agents: Jira, Confluence, Figma
- A basic knowledge fallback agent
- Local JSON files as all knowledge sources
- Structured JSON responses with citations and debug trace
- Promptfoo test configuration

---

## 5. Out of Scope (MVP)

- Real Jira, Confluence, or Figma API integrations
- User authentication and session management
- Persistent conversation history
- Vector database or semantic search
- Streaming responses
- Frontend / UI
- Multi-tenant or role-based access control
- Production deployment infrastructure
- Fine-tuned models

---

## 6. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          User                               │
│              POST /chat  { message, session_id }            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Guard Layer                             │
│   Rules-based + LLM hybrid safety and relevance check       │
│   → BLOCKED or ALLOWED                                      │
└────────────────────────────┬────────────────────────────────┘
                             │ ALLOWED
                             ▼
┌─────────────────────────────────────────────────────────────┐
│            Institutional Knowledge Orchestrator             │
│   LLM-based routing: selects specialist agent(s)            │
│   Understands cross-source queries                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  App Specialist (PayFlow)                   │
│   Domain context: understands PayFlow features/terminology  │
│   Prepares task description for specialist agents           │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Jira    │  │Confluence│  │  Figma   │
        │Specialist│  │Specialist│  │Specialist│
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
             ▼             ▼             ▼
        jira.json  confluence.json  figma.json

                    basic_knowledge.json (fallback)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Synthesis & Response                       │
│   Merges results, generates grounded answer, cites sources  │
│   Returns structured JSON                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Component Definitions

### 7.1 Guard Layer

**Role:** First line of defense. Validates all incoming user messages before any LLM processing.

**Responsibilities:**
- Detect prompt injection attempts
- Block harmful, off-topic, or policy-violating inputs
- Enforce message length limits
- Classify message as `allowed`, `blocked`, or `flagged`
- Attach a `guard_status` and `guard_reason` to the request context

**Implementation approach (MVP):**
- Rules-based checks only: message length limit, keyword blocklist, regex injection patterns
- Returns early with a safe refusal response if blocked
- No LLM call in the guard layer — fast, free, and deterministic
- LLM-based classification is a future enhancement (see §21)

---

### 7.2 Institutional Knowledge Orchestrator

**Role:** Central coordinator. Decides which specialist agents to invoke based on the user's question.

**Responsibilities:**
- Analyze the user message and infer intent using keyword matching
- Select one or more specialist agents (Jira, Confluence, Figma, Basic)
- Detect the relevant PayFlow feature area (login, payments, cards, dashboard, transactions)
- Assign a named decision type (e.g., `jira_blocker_query`, `cross_source_comparison`)
- Produce a task description passed directly to each selected specialist

**Implementation approach (MVP):**
- **Keyword-based routing — no LLM call.** Scans the message for specialist signal words and feature area signals.
- Returns a structured routing object: `{ selected_specialists, orchestrator_decision, feature_area, keywords, task_description }`
- Fallback to basic knowledge if no specialist signals are detected
- See `implementation-decisions.md` §2 Issue 1 for rationale

> **Note:** The App Specialist (originally a separate LLM call) has been merged into the orchestrator. The orchestrator now handles both specialist selection and task description generation in a single deterministic step. See §7.3.

---

### 7.3 App Specialist (PayFlow Domain) — Merged into Orchestrator

**Status:** Merged into `orchestrator.py` for MVP. No separate component or LLM call.

**Original role:** Map user intent to PayFlow feature areas and produce a task description for specialist agents.

**MVP decision:** This mapping is handled deterministically by the orchestrator using `FEATURE_AREA_SIGNALS` keyword matching. The orchestrator returns a `task_description` string alongside the routing decision. This eliminates a separate LLM call, reduces latency, and makes task description generation fully deterministic.

**Future enhancement:** Restore as a standalone LLM-based component when richer intent understanding is needed (e.g., ambiguous domain terminology, multi-language support).

---

### 7.4 Jira Specialist Agent

**Role:** Retrieves and interprets Jira-style ticket data for the PayFlow project.

**Data access:** `data/jira.json`

**Capabilities:**
- Filter tickets by status (open, closed, in-progress, blocked)
- Filter by priority (critical, high, medium, low)
- Filter by feature area (login, payments, cards, dashboard, transactions)
- Retrieve blocker relationships
- Retrieve assignee and sprint information

**Output:** A list of matching ticket objects with title, status, priority, assignee, and summary.

---

### 7.5 Confluence Specialist Agent

**Role:** Retrieves and interprets Confluence-style documentation for the PayFlow project.

**Data access:** `data/confluence.json`

**Capabilities:**
- Search pages by topic, feature, or keyword
- Retrieve requirements documentation
- Retrieve release notes and changelogs
- Retrieve process flows and decision rationale

**Output:** A list of matching page objects with title, section, and relevant excerpt.

---

### 7.6 Figma Specialist Agent

**Role:** Retrieves and interprets Figma-style design data for the PayFlow project.

**Data access:** `data/figma.json`

**Capabilities:**
- Search screens by name or feature area
- Identify UI components on a given screen
- Retrieve design notes and annotations
- Map user actions to screen elements (e.g., "freeze card toggle" on "Card Management" screen)

**Output:** A list of matching screen objects with screen name, components, and design notes.

---

### 7.7 Basic Knowledge Agent

**Role:** Fallback agent for general institutional knowledge that does not belong to Jira, Confluence, or Figma.

**Data access:** `data/basic_knowledge.json`

**Capabilities:**
- Answer general questions about PayFlow's purpose, teams, and product vision
- Answer questions about processes, definitions, and terminology
- Used when no domain-specific specialist is applicable

**Output:** A list of matching knowledge entries with topic and content.

---

### 7.8 Synthesis Service

**Role:** Merges results from all activated specialists into a single grounded answer.

**Responsibilities:**
- Combine results from multiple specialists into coherent context
- Generate a natural language answer using an LLM call grounded in retrieved data
- Produce the final structured JSON response with citations and debug trace

---

## 8. Guard Layer Requirements

| Requirement | Detail |
|---|---|
| GRD-01 | Must run before any orchestrator or LLM call |
| GRD-02 | Must block prompt injection patterns (e.g., "ignore previous instructions") |
| GRD-03 | Must block requests containing profanity or harmful intent |
| GRD-04 | Must block off-topic requests unrelated to PayFlow or software development |
| GRD-05 | Must enforce a maximum message length of 1000 characters |
| GRD-06 | Must return `guard_status: "blocked"` with a `guard_reason` in the response |
| GRD-07 | Must allow borderline questions to pass with `guard_status: "flagged"` for logging |
| GRD-08 | Guard decisions must be included in the response debug trace |

---

## 9. Orchestrator Requirements

| Requirement | Detail |
|---|---|
| ORC-01 | Must analyze the user message and select one or more specialists |
| ORC-02 | Must support single-specialist and multi-specialist routing |
| ORC-03 | Must assign a named `orchestrator_decision` string to each routing choice |
| ORC-04 | Must fall back to basic knowledge if no specialist matches |
| ORC-05 | Must pass the routing decision to the response debug output |
| ORC-06 | Must handle cross-source queries (e.g., "compare Jira and Figma for login") |
| ORC-07 | Routing decisions must be reproducible given the same input |

---

## 10. Specialist Agent Requirements

| Requirement | Detail |
|---|---|
| SPE-01 | Each specialist must only access its designated data file |
| SPE-02 | Each specialist must accept a task description and return a list of matching results |
| SPE-03 | Each specialist must return structured result objects, not plain text |
| SPE-04 | Each specialist must support keyword-based filtering for MVP determinism |
| SPE-05 | Each specialist must include a `source` and `id` field in every result for citation |
| SPE-06 | Specialists must return an empty list if no matches are found |
| SPE-07 | Specialists must not hallucinate — answers must be grounded in retrieved data only |

---

## 11. Knowledge Source Requirements

| Source | File | Content |
|---|---|---|
| Jira | `data/jira.json` | Tickets: id, title, status, priority, feature_area, assignee, sprint, summary, blockers |
| Confluence | `data/confluence.json` | Pages: id, title, feature_area, type (requirements/release_notes/process), content |
| Figma | `data/figma.json` | Screens: id, screen_name, feature_area, components[], design_notes |
| Basic Knowledge | `data/basic_knowledge.json` | Entries: id, topic, content, tags[] |

**Requirements:**
- All data files must be valid JSON
- Data must cover all PayFlow features: login, payments, card management, dashboard, transaction history
- Data must contain enough entries to support at least 10 distinct demo queries
- Data must include cross-source relationships (e.g., a Jira ticket referencing a Confluence page)

---

## 12. API Requirements

### Endpoint

```
POST /chat
Content-Type: application/json
```

### Request Schema

```json
{
  "message": "string (required, max 1000 chars)",
  "session_id": "string (optional)",
  "user_role": "string (optional, default: 'student')"
}
```

### Response Schema

```json
{
  "answer": "string",
  "route": {
    "guard_status": "allowed | blocked | flagged",
    "guard_reason": "string (if blocked/flagged)",
    "selected_specialists": ["jira", "confluence", "figma", "basic"],
    "orchestrator_decision": "string"
  },
  "citations": [
    {
      "source": "jira | confluence | figma | basic",
      "id": "string",
      "title": "string"
    }
  ],
  "debug": {
    "app_specialist_task": "string",
    "steps": ["string"]
  }
}
```

### Additional Requirements

| Requirement | Detail |
|---|---|
| API-01 | Must return HTTP 200 for all handled requests, including blocked ones |
| API-02 | Must return HTTP 422 for malformed request bodies |
| API-03 | Must return HTTP 500 with a safe error message for unhandled exceptions |
| API-04 | Response must always include `answer`, `route`, `citations`, and `debug` fields |
| API-05 | Must include a `GET /health` endpoint returning `{ "status": "ok" }` |
| API-06 | Must support CORS for local testing environments |

---

## 13. Data Requirements

### Jira Sample Data — Minimum Coverage

- At least 15 tickets across all PayFlow features
- At least 3 tickets with status `blocked`
- At least 2 tickets with `blocker` relationships to other tickets
- At least 1 critical-priority ticket per major feature area

### Confluence Sample Data — Minimum Coverage

- At least 10 pages covering requirements, release notes, and process flows
- At least 1 page per feature area
- Pages must contain enough prose to generate a grounded excerpt

### Figma Sample Data — Minimum Coverage

- At least 8 screens covering all major PayFlow features
- Each screen must list at least 3 UI components
- At least 2 screens with design annotations relevant to demo questions

### Basic Knowledge — Minimum Coverage

- At least 5 entries covering product vision, team structure, and terminology
- At least 1 entry per PayFlow feature area

---

## 14. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system must accept a user message and return a structured JSON response |
| FR-02 | The guard layer must run and complete before orchestration begins |
| FR-03 | The orchestrator must select at least one specialist per allowed request |
| FR-04 | Each selected specialist must query its designated data source |
| FR-05 | The synthesis service must produce an answer grounded only in retrieved data |
| FR-06 | All citations must reference real records from the data files |
| FR-07 | The response must include a full debug trace of steps taken |
| FR-08 | Blocked requests must return a safe refusal message, not an error |
| FR-09 | Multi-source queries must merge results from all selected specialists |
| FR-10 | The system must handle questions with no matching data gracefully |

---

## 15. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | Response time must be under 10 seconds for all queries (MVP target) |
| NFR-02 | The system must run fully on a local machine without external dependencies |
| NFR-03 | Code must be readable and well-commented for educational use |
| NFR-04 | The system must not require a database for MVP |
| NFR-05 | All LLM calls must use environment variable configuration for API keys |
| NFR-06 | The system must start with a single `uvicorn` command |
| NFR-07 | JSON data files must be human-readable and easy to edit |

---

## 16. Security and Safety Requirements

| ID | Requirement |
|---|---|
| SEC-01 | API keys must never be hardcoded; use `.env` and `python-dotenv` |
| SEC-02 | User input must be sanitized before inclusion in LLM prompts |
| SEC-03 | Prompt injection patterns must be detected and blocked by the guard layer |
| SEC-04 | LLM system prompts must use clear role boundaries to limit scope |
| SEC-05 | The system must not expose raw LLM prompts in the API response |
| SEC-06 | Error messages must not expose internal implementation details |

---

## 17. Observability and Debugging Requirements

| ID | Requirement |
|---|---|
| OBS-01 | Every API response must include a `debug.steps` array listing each processing stage |
| OBS-02 | The `route` object must expose the guard status and all selected specialists |
| OBS-03 | The orchestrator decision name must be included in every response |
| OBS-04 | The system must log each request to stdout with timestamp and routing decision |
| OBS-05 | Failed specialist retrievals must be logged without crashing the system |
| OBS-06 | The `debug` field must be present even for blocked requests |

---

## 18. Promptfoo / Evaluation Requirements

| ID | Requirement |
|---|---|
| EVAL-01 | The `POST /chat` endpoint must be directly testable with Promptfoo HTTP provider |
| EVAL-02 | Responses must include structured fields that Promptfoo assertions can target |
| EVAL-03 | A `promptfoo/` directory must contain at least one example test config |
| EVAL-04 | Test cases must cover: single-source queries, multi-source queries, blocked inputs |
| EVAL-05 | Assertions must validate `answer` content, `route.guard_status`, and `citations` |
| EVAL-06 | The system must behave deterministically enough to support repeatable evals |

---

## 19. Assumptions

- The Claude API (or another LLM API) is used for orchestration, app specialist, and synthesis LLM calls
- Local JSON files are sufficient for MVP knowledge retrieval
- Keyword-based filtering is acceptable for specialist retrieval at MVP scale
- Students will run the system locally on their own machines
- A single `.env` file will manage all API key configuration
- The system does not need to maintain conversation history across sessions for MVP

---

## 20. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM routing inconsistency | Medium | High | Seed routing prompts with few-shot examples; test with Promptfoo |
| Hallucination in synthesis | Medium | High | Ground synthesis strictly in retrieved data; validate with citation checks |
| Guard layer over-blocking | Low | Medium | Tune blocklist carefully; test with edge-case inputs |
| Slow LLM response times | Medium | Low | Set timeouts; cache responses for known demo questions |
| Student setup friction | Low | Medium | Provide a clear `README.md` with exact setup commands |

---

## 21. Future Enhancements

- Replace local JSON files with live Jira, Confluence, and Figma API integrations
- Add vector search for semantic retrieval (e.g., ChromaDB, Pinecone)
- Add streaming response support via Server-Sent Events
- Add a lightweight frontend (Next.js or Streamlit) for demo visualization
- Add persistent conversation history with session context
- Add role-based routing (e.g., different response depth for `admin` vs `student`)
- Add a feedback loop to capture eval results back into the system
- Support multiple product domains beyond PayFlow
