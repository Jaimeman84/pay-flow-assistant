"""
Base specialist interface — shared contract for all specialist agents.

Every specialist agent:
  - Receives a RetrievalTask (what to look for)
  - Accesses only its designated data source
  - Returns a list of RetrievedItem objects
  - Uses deterministic keyword/field filtering — no LLM calls

Teaching note: The abstract base class enforces a consistent interface.
All specialists are interchangeable from the pipeline's perspective.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RetrievalTask:
    """
    Describes what the specialist should look for.

    Produced by the orchestrator and passed to each selected specialist.
    """

    message: str
    """The original user message — used for keyword extraction and context."""

    feature_area: Optional[str] = None
    """
    Detected PayFlow feature area.
    One of: login | payments | cards | dashboard | transactions | None
    """

    keywords: List[str] = field(default_factory=list)
    """
    Key terms extracted from the user message (stop words removed).
    Used by specialists to score record relevance.
    """


@dataclass
class RetrievedItem:
    """
    A single piece of data retrieved from a knowledge source.

    Every field here has a direct mapping to the API response:
    - source, id, title → Citation object
    - content → used in synthesis to ground the answer
    """

    source: str
    """Which knowledge source this came from: jira | confluence | figma | basic"""

    id: str
    """The unique record identifier, e.g. PF-104, CF-005, FG-006, BK-001"""

    title: str
    """Human-readable title of the record."""

    content: str
    """Summary content passed to the synthesis layer for grounding."""


class BaseSpecialist(ABC):
    """
    Abstract base class for all specialist agents.

    Subclasses implement retrieve() for their specific data source.
    """

    source_name: str = ""

    @abstractmethod
    def retrieve(self, task: RetrievalTask) -> List[RetrievedItem]:
        """
        Query the knowledge source and return matching records.

        Args:
            task: RetrievalTask containing message, feature_area, and keywords.

        Returns:
            List of RetrievedItem objects. Empty list if no matches found.
        """
        ...
