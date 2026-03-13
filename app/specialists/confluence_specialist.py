"""
Confluence specialist agent — retrieves Confluence page data from confluence.json.

Scoring logic (deterministic, no LLM):
  +5  Feature area exact match
  +4  Page type is 'release_notes' and message asks about releases/changes
  +3  Page type is 'requirements' for requirements queries
  +3  Keyword match in page title
  +1  Keyword match in page content (capped at 3 content matches)

Top 3 results by score are returned (pages are longer than tickets).
"""
from typing import List

from app.specialists.base import BaseSpecialist, RetrievalTask, RetrievedItem
from app.services.data_loader import get_store

# Max characters to include from page content in the synthesis context
_MAX_CONTENT_CHARS = 400

# Words that suggest the user wants release notes / changelogs
_RELEASE_NOTES_SIGNALS = {
    "release note", "release notes", "what changed", "changelog",
    "what did", "what was", "v2.", "what's new", "new in",
}


class ConfluenceSpecialist(BaseSpecialist):
    """Retrieves Confluence-style documentation matching the user's task."""

    source_name = "confluence"

    def retrieve(self, task: RetrievalTask) -> List[RetrievedItem]:
        pages = get_store().confluence
        message_lower = task.message.lower()

        wants_release_notes = any(
            signal in message_lower for signal in _RELEASE_NOTES_SIGNALS
        )

        scored: list[tuple[int, dict]] = []
        for page in pages:
            score = self._score(page, task, wants_release_notes)
            if score > 0:
                scored.append((score, page))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            RetrievedItem(
                source="confluence",
                id=p["id"],
                title=p["title"],
                content=self._truncate(p.get("content", ""), _MAX_CONTENT_CHARS),
            )
            for _, p in scored[:3]
        ]

    def _score(
        self, page: dict, task: RetrievalTask, wants_release_notes: bool
    ) -> int:
        # Relevance signals — at least one must match for this page to qualify
        relevance = 0

        if task.feature_area and page.get("feature_area") == task.feature_area:
            relevance += 5

        title_lower = page.get("title", "").lower()
        content_lower = page.get("content", "").lower()
        content_hits = 0
        for kw in task.keywords:
            if len(kw) > 3:
                if kw in title_lower:
                    relevance += 3
                elif kw in content_lower and content_hits < 3:
                    relevance += 1
                    content_hits += 1

        # No relevance signal — exclude this page entirely
        if relevance == 0:
            return 0

        # Quality bonuses applied only when page is relevant
        score = relevance
        page_type = page.get("type", "")
        if wants_release_notes and page_type == "release_notes":
            score += 4
        elif not wants_release_notes and page_type == "requirements":
            score += 2

        return score

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        """Truncate content at a word boundary to keep synthesis context readable."""
        if len(text) <= max_chars:
            return text
        truncated = text[:max_chars]
        last_space = truncated.rfind(" ")
        return (truncated[:last_space] if last_space > 0 else truncated) + "..."
