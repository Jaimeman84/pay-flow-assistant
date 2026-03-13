# BRD.md — Business Requirements Document

**Project:** PayFlow GenAI Demo
**Version:** 1.0 (MVP)
**Status:** Draft
**Audience:** Stakeholders, Instructors, Program Designers, Engineering Leads

---

## 1. Executive Summary

The PayFlow GenAI Demo is a teaching application that demonstrates how specialist agents work inside an orchestrated, multi-agent AI system. It is designed for QA engineers, SDETs, and software testing professionals who need hands-on experience understanding and evaluating AI-powered systems.

The application simulates a realistic enterprise AI assistant for a fictional fintech product called PayFlow. Users can ask natural language questions about project data spanning Jira tickets, Confluence documentation, Figma design screens, and general knowledge. The system routes each question through a guard layer, an LLM orchestrator, and one or more specialist agents, then returns a structured JSON response with citations and a full debug trace.

The MVP is intended to run locally, requires no external service integrations, and is built specifically to support evaluation with Promptfoo — the leading open-source framework for testing and evaluating LLM applications.

This document defines the business case, product requirements, scope, and success criteria for the MVP.

---

## 2. Business Problem

### The Gap in AI Testing Education

AI-powered features are being adopted rapidly across the software industry, but the testing community has not kept pace. QA engineers and SDETs face a new class of software behavior — non-deterministic outputs, multi-step reasoning chains, hidden routing decisions, and grounding failures — for which traditional testing strategies offer limited guidance.

Key problems observed in the field:

**Problem 1: No concrete examples to learn from.**
Most publicly available AI demos are either toy chatbots (too simple to teach real concepts) or full enterprise platforms (too complex for individual learning). There is no middle ground: a realistic, inspectable, locally runnable AI system designed explicitly for educational use.

**Problem 2: Testers don't understand agentic architecture.**
When a multi-agent AI system produces a wrong answer, how does a tester debug it? Without understanding how routing, orchestration, and grounding work, it is nearly impossible to reason about failure modes or write meaningful test cases.

**Problem 3: AI eval tooling is underutilized.**
Promptfoo is a powerful, open-source framework for evaluating LLM applications. However, adoption is limited because most teams don't have a working AI system to connect it to when first learning. There is no "hello world" app for AI evals.

**Problem 4: AI quality is often an afterthought.**
Teams ship AI features without a quality strategy. This results in silent failures — hallucinations, injection vulnerabilities, routing errors — that go undetected until they reach users.

---

## 3. Opportunity

The convergence of three trends creates a clear opportunity for this product:

1. **Rapid AI feature adoption** — Nearly every SaaS product is adding LLM-powered features. The demand for engineers who can test these features is growing faster than the supply.

2. **Rise of AI eval tooling** — Tools like Promptfoo are maturing rapidly and gaining traction. Teams are actively looking for resources to help them adopt these tools.

3. **Educational gap in agentic architecture** — Bootcamps, universities, and corporate training programs need curriculum on GenAI testing, but lack practical, hands-on teaching materials.

By building PayFlow as an open, educational artifact, this project addresses all three trends simultaneously — and establishes a reference implementation that can grow into a broader curriculum or platform.

---

## 4. Product Vision

Build the definitive hands-on teaching application for GenAI testing professionals.

PayFlow demonstrates the full lifecycle of an orchestrated AI request — from user input to structured response — in a way that is transparent, inspectable, and designed for evaluation. It is the application that QA engineers, SDETs, and instructors reach for when they need to teach or learn how AI systems work and how to test them.

**Vision statement:**
> *PayFlow makes the invisible visible — showing exactly how a multi-agent AI system routes, retrieves, and reasons, so testers can understand it, evaluate it, and improve it.*

---

## 5. Business Objectives

| Objective | Measure |
|---|---|
| Provide a working reference architecture for multi-agent AI systems | Architecture documented, implemented, and runnable |
| Enable QA engineers to write their first AI eval test | Users can run a Promptfoo test suite in under 1 hour |
| Support instructor-led learning with a modular, teachable codebase | Instructors can use the app in a curriculum without modification |
| Demonstrate Promptfoo integration on a realistic AI system | A working `promptfoo.yaml` config ships with the app |
| Establish PayFlow as a trusted, open reference for agentic architecture | Community adoption, forks, and curriculum integrations |

---

## 6. User Needs

### QA Engineers and SDETs

- Need to understand how multi-agent AI systems behave
- Need a structured, testable API to write assertions against
- Need to see what a guardrail, routing decision, and specialist agent look like in practice
- Need a starting point for learning Promptfoo

### Instructors and Bootcamp Designers

- Need a complete, self-contained demo application
- Need modular architecture that maps to lesson topics
- Need sample data that students can inspect and modify
- Need a codebase that is clean, readable, and well-documented

### Engineering Teams

- Need a reference architecture for orchestration, routing, and grounding
- Need a working example of structured AI output for CI/CD integration
- Need to see how Promptfoo can be applied to a realistic AI system

---

## 7. MVP Scope

The MVP delivers a working, locally runnable application with the following capabilities:

### In Scope

- `POST /chat` API endpoint accepting natural language questions
- Guard layer with rules-based + LLM hybrid safety checks
- LLM orchestrator for routing to specialist agents
- App specialist for PayFlow domain context
- Three specialist agents: Jira, Confluence, Figma
- Basic knowledge fallback agent
- Local JSON sample data for all knowledge sources
- Structured JSON response with answer, route, citations, and debug trace
- `GET /health` endpoint
- Promptfoo test configuration with example test cases
- Clear project folder structure designed for teaching
- Documentation: ARD, BRD, ICP, workflow guide, folder structure guide

### Out of Scope for MVP

- Real Jira, Confluence, or Figma API integrations
- Frontend / UI
- User authentication
- Persistent session history
- Vector search
- Streaming responses
- Production deployment

---

## 8. Key Features

### Feature 1: Guard Layer
Validates every incoming user message before processing. Detects prompt injection, harmful content, and off-topic requests. Returns a structured `guard_status` field in every response, making safety behavior observable and testable.

**Educational value:** Teaches safety as a first-class concern, not an afterthought. Students can write Promptfoo test cases specifically for guard behavior.

---

### Feature 2: LLM Orchestrator with Named Routing
Routes each question to the correct specialist agent(s) based on intent analysis. Returns a named `orchestrator_decision` string in every response, making routing decisions explicit and traceable.

**Educational value:** Teaches how orchestration works. Students can observe how the same system handles single-source vs. multi-source queries differently.

---

### Feature 3: Specialist Agents (Jira, Confluence, Figma, Basic)
Each specialist agent retrieves grounded data from its designated JSON file. Agents are isolated — Jira can only access Jira data, Confluence can only access Confluence data.

**Educational value:** Teaches data isolation, specialist design, and the principle that grounding reduces hallucination. Students can inspect exactly what data each agent retrieved.

---

### Feature 4: Structured JSON Response with Citations
Every response includes a structured JSON body with the answer, routing metadata, source citations, and a debug trace. Citations reference specific records from the data files.

**Educational value:** Teaches why structured output matters for testing. Students can write assertions targeting specific fields, not just checking that a response "looks right."

---

### Feature 5: Debug Trace
Every response includes a `debug.steps` array that lists every processing stage the request passed through — from guard check to specialist retrieval to synthesis.

**Educational value:** Makes the internal behavior of the AI system visible. Students can use the debug trace to reason about failures without reading source code.

---

### Feature 6: Promptfoo Integration
A working `promptfoo/` directory ships with the app, including a configuration file and example test cases covering single-source queries, multi-source queries, and blocked inputs.

**Educational value:** Gives students a complete, runnable example of AI evaluation using industry-standard tooling.

---

## 9. Functional Business Requirements

| ID | Requirement | Priority |
|---|---|---|
| FBR-01 | The system must accept a natural language question and return a structured JSON response | Must Have |
| FBR-02 | The guard layer must run before any LLM or data retrieval step | Must Have |
| FBR-03 | The orchestrator must route each question to at least one specialist | Must Have |
| FBR-04 | Specialists must retrieve data only from their designated source | Must Have |
| FBR-05 | All responses must include source citations referencing actual data records | Must Have |
| FBR-06 | All responses must include a routing metadata object | Must Have |
| FBR-07 | All responses must include a debug step trace | Must Have |
| FBR-08 | Blocked requests must return a safe message, not an error | Must Have |
| FBR-09 | The system must handle multi-source queries by merging specialist results | Must Have |
| FBR-10 | The system must handle questions with no matching data gracefully | Must Have |
| FBR-11 | A `GET /health` endpoint must return system status | Must Have |
| FBR-12 | A Promptfoo configuration with working test cases must ship with the app | Must Have |
| FBR-13 | The system must run fully on a local machine with a single startup command | Must Have |
| FBR-14 | All sample data must cover all PayFlow features | Must Have |
| FBR-15 | LLM API keys must be configurable via `.env` file | Must Have |

---

## 10. Success Metrics

### Learning Outcomes

| Metric | Target |
|---|---|
| Time for a QA engineer to write their first passing Promptfoo test | < 60 minutes from first run |
| Percentage of architecture concepts coverable in one session | 100% (guard, route, retrieve, synthesize, evaluate) |
| Student comprehension of routing decisions | Students can trace a request using the debug trace without reading code |

### Technical Quality

| Metric | Target |
|---|---|
| API response time | < 10 seconds per query on local hardware |
| Promptfoo test suite pass rate on known demo questions | 100% |
| Guard layer block rate on injection test cases | 100% |
| Answer citation accuracy | All answers cite only real records from data files |

### Adoption

| Metric | Target |
|---|---|
| Successful local setup by a new user | < 15 minutes from clone to first response |
| Instructor adoption (bootcamps or courses using the app) | At least 1 curriculum integration within 3 months |
| Community forks or adaptations | Meaningful engagement within 6 months |

---

## 11. Constraints

| Constraint | Detail |
|---|---|
| No real external integrations | MVP uses local JSON files only — no Jira, Confluence, or Figma API calls |
| No frontend | The application is API-only for MVP |
| No persistent storage | No database; all data is loaded from JSON at startup |
| Local execution only | No deployment infrastructure required for MVP |
| LLM dependency | Requires an LLM API key (e.g., Claude, OpenAI) for orchestration and synthesis |
| Python + FastAPI only | No alternative framework choices for MVP |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM routing non-determinism | Medium | High | Use few-shot examples in prompts; validate with Promptfoo |
| Hallucination in synthesis | Medium | High | Ground synthesis strictly in retrieved data |
| High LLM API cost for classroom use | Low | Medium | Cache responses for known demo questions; document cost expectations |
| Setup friction for non-developer students | Low | Medium | Provide a step-by-step `README.md`; test setup on fresh machines |
| Outdated sample data becoming confusing | Low | Low | Keep sample data simple; version it alongside the codebase |
| Incomplete Promptfoo test coverage | Low | Medium | Ship at least 10 test cases covering all major query types |

---

## 13. Dependencies

| Dependency | Type | Notes |
|---|---|---|
| LLM API (Claude or OpenAI) | External | Required for orchestration, app specialist, synthesis |
| Python 3.10+ | Runtime | Must be installed locally |
| FastAPI + Uvicorn | Framework | Installed via `requirements.txt` |
| Promptfoo | Evaluation tool | Installed separately; npm-based |
| python-dotenv | Library | For `.env` API key management |

---

## 14. Rollout Considerations

### Phase 1 — Internal / Instructor Review
- Complete the MVP implementation
- Run the Promptfoo test suite and confirm all cases pass
- Validate local setup instructions on a clean machine
- Share with 1–2 instructors for feedback

### Phase 2 — Soft Launch
- Publish to GitHub as an open-source repository
- Write a clear `README.md` with setup instructions
- Add a `CONTRIBUTING.md` for community contributions
- Announce in relevant QA/SDET communities (e.g., Ministry of Testing, LinkedIn, Reddit)

### Phase 3 — Curriculum Integration
- Develop companion lesson plans mapped to PayFlow components
- Create exercise prompts and expected outputs for each lesson
- Offer to co-develop curriculum with interested bootcamps or instructors

---

## 15. Future Opportunities

| Opportunity | Description |
|---|---|
| Live API integrations | Replace JSON files with real Jira, Confluence, and Figma API clients |
| Vector search | Add semantic retrieval using ChromaDB or Pinecone for richer queries |
| Frontend visualization | Build a React or Streamlit UI showing routing decisions and agent activity in real time |
| Multiple product domains | Add domains beyond PayFlow (e.g., e-commerce, healthcare, HR) |
| Eval regression suite | Expand the Promptfoo test suite into a full regression suite with CI integration |
| Certification or course | Bundle PayFlow with a structured course on AI testing and Promptfoo |
| Adversarial test library | Build a library of injection, jailbreak, and edge-case prompts for safety testing practice |
| Multi-LLM comparison | Add support for multiple LLM backends to compare routing and synthesis behavior |
