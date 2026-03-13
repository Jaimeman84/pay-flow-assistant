# implementation-decisions.md — Final MVP Implementation Decisions

**Project:** PayFlow GenAI Demo
**Version:** 1.0 (MVP)
**Status:** Final
**Purpose:** Captures the concrete decisions that govern the build, resolving ambiguities and conflicts found across the planning documents.

---

## 1. Document Review Summary

All five planning documents (ARD, BRD, ICP, workflow, folder-structure) are aligned on purpose, product domain, API shape, and data strategy. The following issues were identified and resolved before the build began.

---

## 2. Issues Found and Decisions Made

### Issue 1: Orchestrator uses an LLM call — contradicts determinism goal

**Found in:** ARD §7.2, workflow §2, §3

**Problem:** The ARD and workflow describe the orchestrator as making an LLM call to select specialists. This directly conflicts with the stated goals of "determinism where possible" and "routing decisions must be reproducible given the same input" (ORC-07). Non-deterministic routing makes Promptfoo evals flaky and harder to teach.

**Decision:** The orchestrator uses **keyword-based intent matching** — no LLM call. It scans the user message for specialist signal words (e.g., "jira", "bug", "ticket" → Jira; "screen", "design", "toggle" → Figma) and feature area signals (e.g., "payment", "freeze card", "login"). This is deterministic, fast, and inspectable.

**Impact:** Routing is now 100% deterministic for the same input. Promptfoo evals are reliable. Students can read the routing logic directly in `orchestrator.py`.

---

### Issue 2: App Specialist is a separate LLM call

**Found in:** ARD §7.3, folder-structure §3, workflow §2 steps 11-13

**Problem:** The App Specialist was described as making an LLM call to map user intent to PayFlow feature areas and produce a task description. This is an extra LLM call, extra latency, extra non-determinism, and extra complexity — for a job that keyword matching can do directly.

**Decision:** The App Specialist layer is **folded into the orchestrator**. The orchestrator's `route()` function returns both the selected specialists AND a task description (feature area + formatted task string). No separate `app_specialist.py` file is needed.

**Impact:** Simpler architecture, fewer LLM calls, faster responses. The orchestrator is now the single routing and task-building component.

---

### Issue 3: Guard layer is "LLM hybrid" — runs on every request

**Found in:** ARD §7.1, workflow §4 step 5

**Problem:** A "rules-based + LLM hybrid" guard would make an LLM API call on every single request including blocked ones. This adds cost and latency for the most common path (normal user questions) and makes the guard dependent on external infrastructure.

**Decision:** The guard layer is **purely rules-based** for MVP. It uses:
- Message length check (max 1000 chars)
- Regex injection pattern detection
- Keyword blocklist

This is fast, free, and completely deterministic. The LLM classification option is noted as a future enhancement.

**Impact:** Zero LLM calls on blocked requests. Guard is always instant. Guard tests are deterministic and require no mocking.

---

### Issue 4: Synthesis has no graceful fallback when LLM is unavailable

**Found in:** ARD §7.8, workflow §6

**Problem:** The synthesis step requires an LLM API call to generate a natural language answer. If no API key is configured, the app cannot return any answer — it would fail or return an error. This creates a barrier for students who want to explore the app before setting up an API key.

**Decision:** Synthesis uses **LLM if configured, template fallback if not**. When `LLM_API_KEY` is not set, the synthesizer formats the retrieved records into a structured readable answer using a template. The app is fully functional without an LLM API key — only the natural language answer quality differs.

**Impact:** The app runs completely without any API key. Students can explore routing, retrieval, and guard behavior before touching LLM configuration. LLM synthesis is an enhancement, not a requirement.

---

### Issue 5: Data file naming inconsistency

**Found in:** ARD §11 vs user project spec

**Decision:** Use `jira.json`, `confluence.json`, `figma.json`, `basic_knowledge.json` inside `app/data/`. These names match the ARD and folder-structure document. The JSON data files have top-level arrays named `tickets`, `pages`, `screens`, and `entries` respectively.

---

### Issue 6: Docs are at root, not in `docs/` subdirectory

**Found in:** folder-structure.md §2

**Decision:** Documentation files (ARD.md, BRD.md, ICP.md, workflow.md, folder-structure.md, implementation-decisions.md) remain at the **project root**. This is where they were created and it is simpler for students to find them. The `docs/` folder listed in folder-structure.md is removed from the implementation.

---

### Issue 7: `app_specialist.py` listed as a separate file

**Found in:** folder-structure.md §2, §3

**Decision:** `app_specialist.py` is **not created**. Its functionality is merged into `orchestrator.py`. The `core/` directory contains: `guard.py`, `orchestrator.py`, `synthesizer.py`, `pipeline.py`.

---

### Issue 8: Promptfoo `contains` assertion works poorly against JSON output

**Found in:** workflow.md §15

**Problem:** When using Promptfoo's HTTP provider with `transformResponse: "json"`, the output is a parsed JSON object. The `contains` assertion type converts the output to a string (e.g., `[object Object]`) rather than checking the answer text.

**Decision:** All Promptfoo assertions use `type: javascript`. For text checks on the answer field, use `output.answer.toLowerCase().includes("keyword")`. This is explicit, educational, and works reliably.

---

## 3. Final Architecture Summary

```
POST /chat
    │
    ▼
Guard Layer (rules-only, always instant)
    │ blocked → return refusal
    │ allowed/flagged
    ▼
Orchestrator (keyword-based, no LLM)
    → selected_specialists: ["jira", "confluence", ...]
    → orchestrator_decision: "jira_blocker_query"
    → feature_area: "payments"
    → keywords: ["payment", "blocked", "release"]
    │
    ▼
Specialist Agents (deterministic retrieval, no LLM)
    Jira: filter jira.json by feature_area + keywords + status
    Confluence: filter confluence.json by feature_area + type + keywords
    Figma: filter figma.json by feature_area + component keywords
    Basic: keyword match in basic_knowledge.json
    │
    ▼
Synthesis (LLM if available, template fallback)
    → grounded answer from retrieved data only
    │
    ▼
Structured JSON Response
    { answer, route, citations, debug }
```

---

## 4. Component Decisions

| Component | Approach | LLM Required? |
|---|---|---|
| Guard layer | Rules-only: regex + blocklist + length check | No |
| Orchestrator | Keyword intent matching + feature area detection | No |
| App Specialist | Merged into orchestrator | Removed |
| Jira Specialist | Keyword + field scoring against `jira.json` | No |
| Confluence Specialist | Keyword + field scoring against `confluence.json` | No |
| Figma Specialist | Keyword + component scoring against `figma.json` | No |
| Basic Specialist | Keyword scoring against `basic_knowledge.json` | No |
| Synthesis | LLM-grounded answer OR template fallback | Optional |

---

## 5. Data Model Decisions

### Jira ticket schema
```json
{
  "id": "PF-101",
  "title": "string",
  "status": "open | blocked | in-progress | closed",
  "priority": "critical | high | medium | low",
  "feature_area": "login | payments | cards | dashboard | transactions",
  "assignee": "string",
  "sprint": "string",
  "summary": "string",
  "blockers": ["PF-xxx"]
}
```

### Confluence page schema
```json
{
  "id": "CF-001",
  "title": "string",
  "feature_area": "login | payments | cards | dashboard | transactions | general",
  "type": "requirements | release_notes | process_flow",
  "content": "string"
}
```

### Figma screen schema
```json
{
  "id": "FG-001",
  "screen_name": "string",
  "feature_area": "login | payments | cards | dashboard | transactions",
  "components": ["component_name"],
  "design_notes": "string"
}
```

### Basic knowledge entry schema
```json
{
  "id": "BK-001",
  "topic": "string",
  "content": "string",
  "tags": ["string"]
}
```

---

## 6. API Response Shape (Final)

```json
{
  "answer": "string",
  "route": {
    "guard_status": "allowed | blocked | flagged",
    "guard_reason": "string | null",
    "selected_specialists": ["jira", "confluence"],
    "orchestrator_decision": "string | null"
  },
  "citations": [
    { "source": "jira", "id": "PF-104", "title": "string" }
  ],
  "debug": {
    "app_specialist_task": "string | null",
    "steps": ["string"]
  }
}
```

---

## 7. Orchestrator Decision Names (Locked)

| `orchestrator_decision` | Triggered when |
|---|---|
| `jira_ticket_query` | Message has Jira signals, no specific blocker/release context |
| `jira_blocker_query` | Message has Jira signals AND "blocker/blocking/blocked/release" |
| `confluence_docs_query` | Message has Confluence signals, non-release-notes context |
| `confluence_release_notes_query` | Message has Confluence signals AND "release notes/what changed/changelog" |
| `figma_screen_query` | Message has Figma signals, screen-level context |
| `figma_component_query` | Message has Figma signals AND "component/toggle/button/element" |
| `cross_source_comparison` | Message triggers 2+ specialists |
| `basic_knowledge_query` | Message routes to basic knowledge only |
| `unknown_topic_fallback` | No specialist signals detected, falls back to basic |

---

## 8. Environment Variables

```
LLM_PROVIDER=anthropic        # or: openai
LLM_MODEL=claude-3-5-haiku-20241022
LLM_API_KEY=                  # optional — app works without it
APP_ENV=development
LOG_LEVEL=INFO
```

---

## 9. Promptfoo Integration

- HTTP provider connects to `POST /chat`
- `transformResponse: "json"` makes the full JSON object available as `output`
- All assertions use `type: javascript` for reliable field access
- Example: `output.route.guard_status === 'allowed'`
- Example: `output.route.selected_specialists.includes('jira')`
- Example: `output.answer.toLowerCase().includes('payment')`

---

## 10. What Is and Is Not Mocked

| Item | Status |
|---|---|
| Jira data | Sample JSON — no real Jira API |
| Confluence data | Sample JSON — no real Confluence API |
| Figma data | Sample JSON — no real Figma API |
| Basic knowledge | Sample JSON — no database |
| Guard layer | Fully real (rules-based) |
| Orchestrator | Fully real (keyword-based) |
| Specialist retrieval | Fully real (against sample JSON) |
| LLM synthesis | Real if API key set; template fallback if not |
| Authentication | None — open API for demo use |
| Persistent storage | None — data loaded at startup |
