"""
Orchestrator — keyword-based routing and task description builder.

Replaces both the original LLM-based orchestrator AND the App Specialist
(see implementation-decisions.md §2 Issues 1 & 2).

What this module does:
  1. Scans the user message for specialist signal words
     → decides which specialist agents to invoke
  2. Detects the PayFlow feature area from the message
     → narrows specialist retrieval to the right feature
  3. Extracts keywords for specialist scoring
  4. Assigns a named orchestrator_decision string
  5. Builds a human-readable task description

Everything here is deterministic — same input always produces same output.
This makes routing fully testable with Promptfoo assertions.

Teaching note: Students can inspect SPECIALIST_SIGNALS and FEATURE_AREA_SIGNALS
to understand exactly what words trigger which routing paths.
"""
import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

# ── Specialist signal words ─────────────────────────────────────────────────
# If any of these appear in the message, the corresponding specialist is selected.
SPECIALIST_SIGNALS: dict[str, list[str]] = {
    "jira": [
        "jira",
        "ticket",
        "tickets",
        "bug",
        "bugs",
        "issue",
        "issues",
        "sprint",
        "blocker",
        "blockers",
        "blocking",
        "blocked",
        "story",
        "epic",
        "defect",
        "open ticket",
        "open bug",
        "assigned to",
        "in progress",
        "closed ticket",
        "resolved",
    ],
    "confluence": [
        "confluence",
        "documentation",
        "docs",
        "doc",
        "requirements",
        "requirement",
        "release note",
        "release notes",
        "changelog",
        "process flow",
        "specification",
        "spec",
        "wiki",
        "what does confluence",
        "what changed",
        "what did",
        "what was",
        "policy",
        "procedure",
        "flow",
    ],
    "figma": [
        "figma",
        "screen",
        "screens",
        "design",
        "component",
        "components",
        "wireframe",
        "mockup",
        "ui",
        "ux",
        "interface",
        "toggle",
        "which screen",
        "what screen",
        "design note",
        "annotation",
        "layout",
        "prototype",
    ],
}

# ── Feature area signal words ───────────────────────────────────────────────
# Used to narrow specialist retrieval to a specific PayFlow feature.
FEATURE_AREA_SIGNALS: dict[str, list[str]] = {
    "login": [
        "login",
        "log in",
        "sign in",
        "signin",
        "authentication",
        "auth",
        "otp",
        "password",
        "biometric",
        "face id",
        "touch id",
        "fingerprint",
        "forgot password",
        "session",
        "token",
    ],
    "payments": [
        "payment",
        "payments",
        "pay",
        "transfer",
        "send money",
        "payment confirmation",
        "confirm payment",
        "payment release",
        "payment history",
        "payment flow",
        "fee",
        "transaction fee",
        "idempotency",
    ],
    "cards": [
        "card",
        "cards",
        "freeze card",
        "freeze",
        "frozen",
        "unfreeze",
        "report lost",
        "lost card",
        "virtual card",
        "card management",
        "debit card",
        "credit card",
    ],
    "dashboard": [
        "dashboard",
        "home screen",
        "home page",
        "overview",
        "balance widget",
        "quick actions",
        "balance",
        "notification badge",
    ],
    "transactions": [
        "transaction",
        "transactions",
        "transaction history",
        "history",
        "statement",
        "receipt",
        "export",
        "pdf export",
        "csv export",
        "date filter",
        "filter",
    ],
}

# ── Stop words for keyword extraction ───────────────────────────────────────
_STOP_WORDS = {
    "what", "which", "where", "when", "how", "why", "who",
    "is", "are", "was", "were", "will", "would", "should", "could",
    "the", "a", "an", "and", "or", "but", "for", "in", "on",
    "at", "to", "of", "does", "do", "can", "tell", "me", "about",
    "show", "find", "give", "list", "there", "any", "some",
    "this", "that", "these", "those", "with", "from", "has",
    "have", "had", "been", "being", "its", "not", "related",
    "please", "thanks", "help", "need",
}


@dataclass
class RoutingDecision:
    """
    Result of the orchestrator's routing analysis.

    Contains everything the pipeline needs to dispatch to specialists
    and build the response metadata.
    """

    selected_specialists: List[str]
    """Which specialist agents to invoke."""

    orchestrator_decision: str
    """Named routing decision for the response and Promptfoo assertions."""

    feature_area: Optional[str]
    """Detected PayFlow feature area, or None if not detected."""

    keywords: List[str]
    """Key terms extracted from the message for specialist scoring."""

    task_description: str
    """Human-readable task description passed to specialists and included in debug output."""


def route(message: str) -> RoutingDecision:
    """
    Analyse the user message and return a RoutingDecision.

    Steps:
      1. Detect specialist signals → selected_specialists
      2. Detect feature area       → feature_area
      3. Extract keywords          → keywords
      4. Assign decision name      → orchestrator_decision
      5. Build task description    → task_description
    """
    message_lower = message.lower()

    # ── Step 1: Detect specialists ──────────────────────────────────────────
    selected: List[str] = []
    for specialist, signals in SPECIALIST_SIGNALS.items():
        for signal in signals:
            if signal in message_lower:
                if specialist not in selected:
                    selected.append(specialist)
                break  # One signal match is enough to select this specialist

    # Fallback: if nothing matched, route to basic knowledge
    if not selected:
        selected = ["basic"]

    # ── Step 2: Detect feature area ─────────────────────────────────────────
    feature_area: Optional[str] = None
    for area, signals in FEATURE_AREA_SIGNALS.items():
        for signal in signals:
            if signal in message_lower:
                feature_area = area
                break
        if feature_area:
            break

    # ── Step 3: Extract keywords ─────────────────────────────────────────────
    words = re.findall(r"\b[a-z]+\b", message_lower)
    keywords = [w for w in words if len(w) > 3 and w not in _STOP_WORDS]

    # ── Step 4: Assign decision name ─────────────────────────────────────────
    decision = _determine_decision(selected, message_lower, feature_area)

    # ── Step 5: Build task description ──────────────────────────────────────
    task_description = _build_task_description(message, selected, feature_area)

    logger.debug(
        "Orchestrator: decision=%s specialists=%s feature=%s keywords=%s",
        decision,
        selected,
        feature_area,
        keywords[:5],
    )

    return RoutingDecision(
        selected_specialists=selected,
        orchestrator_decision=decision,
        feature_area=feature_area,
        keywords=keywords,
        task_description=task_description,
    )


def _determine_decision(
    specialists: List[str],
    message_lower: str,
    feature_area: Optional[str],
) -> str:
    """Map the selected specialists and message context to a named decision string."""

    # Cross-source: more than one specialist selected
    if len(specialists) > 1:
        return "cross_source_comparison"

    # Single specialist decisions
    if specialists == ["jira"]:
        blocker_words = ("block", "blocked", "blocker", "blocking", "release")
        if any(w in message_lower for w in blocker_words):
            return "jira_blocker_query"
        return "jira_ticket_query"

    if specialists == ["confluence"]:
        release_words = ("release note", "release notes", "what changed", "changelog")
        if any(w in message_lower for w in release_words):
            return "confluence_release_notes_query"
        return "confluence_docs_query"

    if specialists == ["figma"]:
        component_words = ("component", "toggle", "button", "element", "icon")
        if any(w in message_lower for w in component_words):
            return "figma_component_query"
        return "figma_screen_query"

    if specialists == ["basic"]:
        # Check if any specialist signal was detected but fell through to basic
        has_jira_signal = any(s in message_lower for s in SPECIALIST_SIGNALS["jira"])
        has_confluence_signal = any(
            s in message_lower for s in SPECIALIST_SIGNALS["confluence"]
        )
        has_figma_signal = any(s in message_lower for s in SPECIALIST_SIGNALS["figma"])
        if not (has_jira_signal or has_confluence_signal or has_figma_signal):
            return "unknown_topic_fallback"
        return "basic_knowledge_query"

    return "basic_knowledge_query"


def _build_task_description(
    message: str,
    specialists: List[str],
    feature_area: Optional[str],
) -> str:
    """Build a human-readable task description for the debug output."""
    feature_str = f" related to {feature_area}" if feature_area else ""
    specialist_str = " and ".join(s.capitalize() for s in specialists)
    return f"Find information{feature_str} from {specialist_str}: {message[:120]}"
