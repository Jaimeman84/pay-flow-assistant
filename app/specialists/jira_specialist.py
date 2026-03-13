"""
Jira specialist agent — retrieves Jira ticket data from jira.json.

Scoring logic (deterministic, no LLM):
  +5  Feature area exact match
  +4  Ticket is 'blocked' and message asks about blockers/release
  +3  Priority is 'critical'
  +2  Priority is 'high' | keyword found in ticket title
  +1  Ticket status is active (open, blocked, in-progress) | keyword in summary

Top 5 results by score are returned.
"""
from typing import List

from app.specialists.base import BaseSpecialist, RetrievalTask, RetrievedItem
from app.services.data_loader import get_store

# Statuses that indicate an active / relevant ticket
_ACTIVE_STATUSES = {"open", "blocked", "in-progress"}

# Priority score weights
_PRIORITY_SCORES = {"critical": 3, "high": 2, "medium": 1, "low": 0}


class JiraSpecialist(BaseSpecialist):
    """Retrieves Jira-style ticket data matching the user's task."""

    source_name = "jira"

    def retrieve(self, task: RetrievalTask) -> List[RetrievedItem]:
        tickets = get_store().jira
        message_lower = task.message.lower()

        # Detect whether user is asking about release blockers
        wants_blockers = any(
            w in message_lower
            for w in ("block", "blocked", "blocker", "blocking", "release")
        )

        scored: list[tuple[int, dict]] = []
        for ticket in tickets:
            score = self._score(ticket, task, wants_blockers)
            if score > 0:
                scored.append((score, ticket))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            RetrievedItem(
                source="jira",
                id=t["id"],
                title=t["title"],
                content=self._format_content(t),
            )
            for _, t in scored[:5]
        ]

    def _score(self, ticket: dict, task: RetrievalTask, wants_blockers: bool) -> int:
        # Relevance signals — at least one must match for this ticket to qualify
        relevance = 0

        if task.feature_area and ticket.get("feature_area") == task.feature_area:
            relevance += 5

        title = ticket.get("title", "").lower()
        summary = ticket.get("summary", "").lower()
        for kw in task.keywords:
            if len(kw) > 3:
                if kw in title:
                    relevance += 2
                elif kw in summary:
                    relevance += 1

        # No relevance signal — exclude this ticket entirely
        if relevance == 0:
            return 0

        # Quality bonuses applied only when ticket is relevant
        score = relevance
        if wants_blockers and ticket.get("status") == "blocked":
            score += 4
        score += _PRIORITY_SCORES.get(ticket.get("priority", ""), 0)
        if ticket.get("status") in _ACTIVE_STATUSES:
            score += 1

        return score

    def _format_content(self, ticket: dict) -> str:
        """Format ticket fields into a content string for synthesis."""
        blockers = ticket.get("blockers", [])
        blocker_str = f" | Blocked by: {', '.join(blockers)}" if blockers else ""
        return (
            f"Status: {ticket.get('status', 'unknown').upper()} | "
            f"Priority: {ticket.get('priority', 'unknown').upper()} | "
            f"Assignee: {ticket.get('assignee', 'unassigned')} | "
            f"Sprint: {ticket.get('sprint', 'N/A')}{blocker_str} | "
            f"{ticket.get('summary', '')}"
        )
