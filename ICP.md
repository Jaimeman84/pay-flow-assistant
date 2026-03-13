# ICP.md — Ideal Customer Profile

**Project:** PayFlow GenAI Demo
**Version:** 1.0 (MVP)
**Status:** Draft
**Audience:** Product, Marketing, Instructors, Program Designers

---

## 1. Overview

The PayFlow GenAI Demo is a teaching and demonstration application. Its ideal audience consists of technical professionals who need hands-on experience understanding, testing, or evaluating AI systems — particularly agentic architectures built with large language models.

This is not a production SaaS product. Its value is educational and enabling: it gives people a realistic, working example of a multi-agent AI system they can run locally, explore, and evaluate using real tooling like Promptfoo.

The ICP therefore spans three overlapping groups:
1. Individual learners — QA engineers, SDETs, and testers moving into AI testing
2. Instructors and program designers — bootcamps, courses, and enterprise training teams
3. Engineering teams — developers and quality engineers evaluating agentic architectures

---

## 2. Primary Audience

### QA Engineers and SDETs Upskilling in AI Testing

**Who they are:**
- QA engineers with 2–8 years of experience in manual or automated testing
- SDETs who are comfortable with code but new to LLM systems
- Manual testers transitioning into automation or AI quality roles
- Test engineers at companies beginning to adopt GenAI tools

**What they need:**
- A concrete, working example of an AI system they can actually test
- Hands-on experience writing assertions against structured AI outputs
- Familiarity with tools like Promptfoo without needing to build an AI system from scratch
- A mental model for how agentic systems behave differently from traditional software

**Why this product fits them:**
- The `POST /chat` endpoint behaves like a real API — they can test it the same way they test any backend
- Structured JSON responses give them clear assertion targets
- The guard layer demonstrates safety testing as a first-class quality concern
- The debug trace lets them see exactly what the system did, which builds intuition for failure modes

---

## 3. Secondary Audience

### Instructors, Bootcamps, and Training Program Designers

**Who they are:**
- Instructors designing AI testing curricula for bootcamps or enterprise training
- Learning and development (L&D) professionals at tech companies
- University or college instructors teaching software quality or AI systems
- Authors writing courses on Promptfoo, LLM testing, or GenAI quality

**What they need:**
- A self-contained, easy-to-run demo application
- A system complex enough to teach real concepts but simple enough to explain in a session
- Sample data that students can inspect and extend
- A codebase that can serve as a starting point for exercises or assignments

**Why this product fits them:**
- The fictional PayFlow domain is familiar (fintech apps) and immediately relatable
- The architecture is modular — instructors can focus on one component at a time
- The folder structure is clean and annotated for learning
- It ships with Promptfoo test configs that instructors can use as exercises

---

### Engineering Teams Exploring AI Evals and Agent Architecture

**Who they are:**
- Developers at companies building or evaluating their first AI-powered features
- Platform engineers responsible for AI quality and safety tooling
- Tech leads assessing how to structure multi-agent systems
- DevOps or QA leads evaluating Promptfoo for CI/CD integration

**What they need:**
- A reference architecture they can adapt for their own use case
- A working example of guardrails, routing, and structured output
- A starting point for setting up Promptfoo in their own pipeline
- Evidence that deterministic evals on LLM outputs are achievable

**Why this product fits them:**
- The architecture is explicitly designed to be extensible — swap JSON files for live APIs
- The guard layer and routing patterns are directly transferable to production designs
- The structured output format makes CI/CD integration with Promptfoo straightforward
- The codebase is clean Python/FastAPI, which most engineering teams can read and modify

---

## 4. Roles and Personas

### Persona 1: Alex — The QA Engineer Going AI

- **Role:** Senior QA Engineer at a mid-size SaaS company
- **Experience:** 5 years in test automation (Selenium, pytest, Postman)
- **Situation:** Their team is adopting Copilot-style AI features; their manager wants them to "figure out how to test these things"
- **Pain:** Alex doesn't know where to start. AI outputs are non-deterministic. There's no clear testing strategy.
- **Goal:** Build confidence in testing AI systems using familiar approaches (API testing, assertions, structured outputs)
- **How PayFlow helps:** Alex can run the demo locally, hit `POST /chat` with Postman or Promptfoo, inspect the structured response, and write their first AI eval test in under an hour

---

### Persona 2: Sofia — The SDET Transitioning Into AI Quality

- **Role:** SDET at a fintech company, primarily writing integration tests in Python
- **Experience:** 4 years in test engineering, familiar with CI/CD pipelines
- **Situation:** Her team is building a customer support chatbot. She's been asked to own quality for the AI layer.
- **Pain:** She doesn't understand how the AI layer works — what it does, what can go wrong, how to catch regressions
- **Goal:** Understand agentic AI architecture well enough to design a quality strategy
- **How PayFlow helps:** Sofia can trace exactly how a question flows from guard → orchestrator → specialist → synthesis. The debug trace makes invisible system behavior visible.

---

### Persona 3: Marcus — The AI Testing Instructor

- **Role:** Instructor at a QA/SDET bootcamp, developing a new module on AI testing
- **Experience:** 10+ years in QA, started teaching 3 years ago
- **Situation:** Students keep asking "how do I test ChatGPT-style features?" He needs a real example, not just slides.
- **Pain:** Most demo apps are either too simple (toy chatbots) or too complex (full enterprise systems)
- **Goal:** A realistic, inspectable AI system that students can run, break, and fix
- **How PayFlow helps:** The modular architecture maps directly to lesson topics. Week 1: guard layer. Week 2: routing. Week 3: specialist agents. Week 4: Promptfoo evals.

---

### Persona 4: Jordan — The Engineering Tech Lead

- **Role:** Tech Lead at a startup building a document Q&A feature using LLMs
- **Experience:** 8 years in backend engineering, evaluating multi-agent frameworks
- **Situation:** The team disagrees on how to structure their AI pipeline. Jordan needs a reference design.
- **Pain:** Most reference architectures are either toy examples or over-engineered frameworks
- **Goal:** A clean, readable implementation of orchestration + routing + grounding to use as a blueprint
- **How PayFlow helps:** The ARD, codebase structure, and specialist agent pattern give Jordan a concrete starting point to adapt

---

## 5. Pain Points

| Pain Point | Who Feels It |
|---|---|
| "I don't know how to test AI outputs — they're not deterministic" | QA engineers, SDETs |
| "I don't understand what an agent actually does in code" | Testers, junior developers |
| "I can't explain multi-agent architecture to my team without a working example" | Tech leads, instructors |
| "I've heard of Promptfoo but don't know how to set up a real test suite" | QA engineers, SDETs, DevOps |
| "My students need hands-on work, not just theory" | Instructors, bootcamp designers |
| "Every demo app I find is either too simple or too complex to learn from" | All audiences |
| "I need to justify AI quality investment to my manager" | QA leads, engineering managers |
| "I don't know what guardrails look like in practice" | Developers, QA engineers |

---

## 6. Goals and Motivations

| Audience | Primary Goal | Motivation |
|---|---|---|
| QA engineers | Learn to test AI APIs with real tools | Stay relevant as teams adopt GenAI |
| SDETs | Own the AI quality layer at their company | Career growth, job security |
| Instructors | Deliver effective AI testing curriculum | Student outcomes, course credibility |
| Tech leads | Get a reference architecture for agentic systems | Faster, safer product development |
| Bootcamp designers | Differentiate curriculum with AI content | Enrollment, employer partnerships |
| Engineering managers | Build team capability in AI quality | Reduce production AI incidents |

---

## 7. Why This Product Matters to Them

**For testers:** The gap between knowing how to test a REST API and knowing how to test an AI system is large. PayFlow bridges that gap with a familiar API surface (JSON in, JSON out) backed by an explainable AI architecture. Testers can apply what they already know while learning what's new.

**For instructors:** A teaching tool is only as good as the discussion it enables. PayFlow is designed around teachable moments — every component exists to illustrate a concept. The guard layer teaches safety. The orchestrator teaches routing. The specialists teach grounding. The Promptfoo config teaches evaluation. That's a full curriculum in one application.

**For engineering teams:** Most agentic AI architectures are documented in blog posts, not working code. PayFlow gives teams a clean, documented, runnable reference they can fork and adapt. The structured output format and Promptfoo integration show how AI quality can be automated, not just manual.

---

## 8. Use Cases

| Use Case | Audience |
|---|---|
| Run the demo and write your first Promptfoo eval test | QA engineers, SDETs |
| Teach a 4-week module on AI system testing | Instructors |
| Walk through the guard layer and discuss prompt injection | Students, QA engineers |
| Compare how single-source vs. multi-source queries behave | SDETs, developers |
| Fork the repo and replace JSON files with live API calls | Engineering teams |
| Use PayFlow as a capstone project in an AI testing bootcamp | Bootcamp designers |
| Demonstrate agentic architecture to a non-technical stakeholder | Tech leads, managers |
| Run Promptfoo in CI and catch routing regressions | DevOps, QA leads |

---

## 9. Buying / Adoption Triggers

This is an open-source or free educational tool, so "buying" means adoption. The following events trigger adoption:

- A team is tasked with testing an AI feature for the first time
- A bootcamp is designing a new AI testing or GenAI engineering course
- A QA engineer sees "Promptfoo" mentioned in a job listing and wants to learn it
- An instructor is looking for a demo app that is more realistic than toy examples
- A tech lead is evaluating whether to adopt a multi-agent architecture
- An engineering team ships a GenAI feature and has no quality strategy for it
- A developer attends a talk on LLM evals and wants a hands-on starting point

---

## 10. Objections or Concerns

| Objection | Response |
|---|---|
| "This is too simple to be useful for production" | It's designed for learning, not production. The architecture is explicitly extensible. |
| "I already know how to test APIs" | AI APIs behave differently — non-determinism, grounding failures, injection risks. This teaches the new failure modes. |
| "I don't want to learn another framework" | PayFlow uses plain FastAPI and standard Python. Promptfoo is optional but valuable. |
| "The fake data won't reflect my real use case" | The patterns (guard, route, retrieve, synthesize) transfer directly. Replace the JSON files with your own data. |
| "I'm not sure my students are ready for this level of complexity" | The architecture is modular. Start with the guard layer. Add one component at a time. |
| "Is this maintained?" | For MVP, it is a self-contained teaching artifact. Students can maintain their own fork. |

---

## 11. Success Criteria

| Audience | Success Looks Like |
|---|---|
| QA engineer | Writes a working Promptfoo test suite against the PayFlow API in under one day |
| SDET | Can explain orchestration, routing, and specialist agents to a colleague without referring to docs |
| Instructor | Delivers a session using PayFlow where students leave with a passing eval test |
| Tech lead | Forks the repo and adapts the architecture for their own product within a sprint |
| Bootcamp | Incorporates PayFlow into curriculum and receives positive student feedback |
| Engineering team | Adds Promptfoo to their CI pipeline using PayFlow as the reference implementation |

---

## 12. Messaging Angles

| Angle | Message |
|---|---|
| For QA engineers | "Test AI systems the same way you test APIs — with structure, assertions, and confidence." |
| For SDETs | "Understand what your AI system is actually doing. Then test it." |
| For instructors | "A complete, teachable AI system. One component at a time." |
| For tech leads | "A clean reference architecture for multi-agent AI. Fork it. Adapt it. Ship it." |
| For bootcamps | "Give your students a real AI system to test, not a toy." |
| For Promptfoo learners | "A working demo app built specifically for Promptfoo evaluation." |
| General | "Stop guessing. Start testing. PayFlow shows you exactly how an AI system makes decisions." |
