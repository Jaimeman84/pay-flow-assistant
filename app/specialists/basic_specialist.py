"""
Basic knowledge specialist — retrieves general PayFlow knowledge from basic_knowledge.json.

Used as:
  1. The fallback when no other specialist matches
  2. An explicit route for general PayFlow questions

Scoring logic (deterministic, no LLM):
  +4  Keyword match in topic
  +3  Keyword match in tags list
  +2  Keyword match in content (capped at 4 content matches)

Also scores entries whose tags match the detected feature_area.

Top 3 results by score are returned.
"""
from typing import List

from app.specialists.base import BaseSpecialist, RetrievalTask, RetrievedItem
from app.services.data_loader import get_store

_MAX_CONTENT_CHARS = 350


class BasicSpecialist(BaseSpecialist):
    """Retrieves general PayFlow knowledge matching the user's task."""

    source_name = "basic"

    def retrieve(self, task: RetrievalTask) -> List[RetrievedItem]:
        entries = get_store().basic

        scored: list[tuple[int, dict]] = []
        for entry in entries:
            score = self._score(entry, task)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            RetrievedItem(
                source="basic",
                id=e["id"],
                title=e["topic"],
                content=self._truncate(e.get("content", ""), _MAX_CONTENT_CHARS),
            )
            for _, e in scored[:3]
        ]

    def _score(self, entry: dict, task: RetrievalTask) -> int:
        score = 0

        topic_lower = entry.get("topic", "").lower()
        content_lower = entry.get("content", "").lower()
        tags = [t.lower() for t in entry.get("tags", [])]

        # Feature area match via tags
        if task.feature_area and task.feature_area in tags:
            score += 3

        content_hits = 0
        for kw in task.keywords:
            if len(kw) > 3:
                if kw in topic_lower:
                    score += 4
                if kw in tags:
                    score += 3
                if kw in content_lower and content_hits < 4:
                    score += 2
                    content_hits += 1

        return score

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        truncated = text[:max_chars]
        last_space = truncated.rfind(" ")
        return (truncated[:last_space] if last_space > 0 else truncated) + "..."
