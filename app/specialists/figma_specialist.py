"""
Figma specialist agent — retrieves Figma screen data from figma.json.

Scoring logic (deterministic, no LLM):
  +5  Feature area exact match
  +4  Keyword match in screen_name
  +3  Keyword match in components list
  +2  Keyword match in design_notes

Top 3 results by score are returned.
"""
from typing import List

from app.specialists.base import BaseSpecialist, RetrievalTask, RetrievedItem
from app.services.data_loader import get_store

# Max characters to include from design_notes in synthesis context
_MAX_NOTES_CHARS = 300


class FigmaSpecialist(BaseSpecialist):
    """Retrieves Figma-style screen and component data matching the user's task."""

    source_name = "figma"

    def retrieve(self, task: RetrievalTask) -> List[RetrievedItem]:
        screens = get_store().figma

        scored: list[tuple[int, dict]] = []
        for screen in screens:
            score = self._score(screen, task)
            if score > 0:
                scored.append((score, screen))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            RetrievedItem(
                source="figma",
                id=s["id"],
                title=s["screen_name"],
                content=self._format_content(s),
            )
            for _, s in scored[:3]
        ]

    def _score(self, screen: dict, task: RetrievalTask) -> int:
        score = 0

        # Feature area match
        if task.feature_area and screen.get("feature_area") == task.feature_area:
            score += 5

        screen_name_lower = screen.get("screen_name", "").lower()
        # Join component names into a searchable string
        components_str = " ".join(screen.get("components", [])).lower()
        design_notes_lower = screen.get("design_notes", "").lower()

        for kw in task.keywords:
            if len(kw) > 3:
                if kw in screen_name_lower:
                    score += 4
                if kw in components_str:
                    score += 3
                if kw in design_notes_lower:
                    score += 2

        return score

    def _format_content(self, screen: dict) -> str:
        """Format screen data into a content string for synthesis."""
        components = ", ".join(screen.get("components", []))
        notes = screen.get("design_notes", "")
        truncated_notes = (
            notes[:_MAX_NOTES_CHARS] + "..." if len(notes) > _MAX_NOTES_CHARS else notes
        )
        return f"Components: {components} | Design Notes: {truncated_notes}"
