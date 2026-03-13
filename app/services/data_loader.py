"""
Data loader service — loads and caches all sample JSON data files at startup.

All specialist agents read from this shared in-memory store.
Data is loaded once when the module is first imported and reused across all requests.

Teaching note: This pattern separates data loading from retrieval logic.
To swap JSON files for a live API or database, only this file needs to change.
"""
import json
import os
import logging
from typing import List

logger = logging.getLogger(__name__)

# Path to the data directory relative to this file
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename: str) -> dict:
    """Load a JSON file from the data directory."""
    path = os.path.normpath(os.path.join(_DATA_DIR, filename))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class DataStore:
    """
    In-memory store of all PayFlow sample data.

    Attributes:
        jira:       List of Jira ticket dicts from jira.json
        confluence: List of Confluence page dicts from confluence.json
        figma:      List of Figma screen dicts from figma.json
        basic:      List of knowledge entry dicts from basic_knowledge.json
    """

    def __init__(self) -> None:
        logger.info("Loading PayFlow sample data files...")
        self.jira: List[dict] = _load_json("jira.json")["tickets"]
        self.confluence: List[dict] = _load_json("confluence.json")["pages"]
        self.figma: List[dict] = _load_json("figma.json")["screens"]
        self.basic: List[dict] = _load_json("basic_knowledge.json")["entries"]
        logger.info(
            "Data loaded — Jira: %d | Confluence: %d | Figma: %d | Basic: %d",
            len(self.jira),
            len(self.confluence),
            len(self.figma),
            len(self.basic),
        )


# Module-level singleton — loaded once, shared across all requests
_store: DataStore | None = None


def get_store() -> DataStore:
    """Return the shared DataStore instance, initialising it on first call."""
    global _store
    if _store is None:
        _store = DataStore()
    return _store
