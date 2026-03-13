"""
Synthesis service — generates a grounded natural language answer from retrieved data.

Two modes:
  1. LLM synthesis (when LLM_API_KEY is configured)
     → Sends retrieved records as context to the LLM
     → LLM is instructed to answer using ONLY the provided data
     → Falls back to template if LLM call fails

  2. Template synthesis (fallback, no API key required)
     → Formats retrieved records into a readable structured answer
     → Fully deterministic — identical results every time
     → Good enough for demos and teaching retrieval/routing

The app is 100% functional in template mode.
LLM synthesis improves answer fluency and readability.

Teaching note: Grounding means the LLM cannot add information
that wasn't retrieved. Test this by asking about a topic with no
data — the system should say "I don't have information" not fabricate.
"""
import logging
from typing import List, Optional

from app.specialists.base import RetrievedItem
from app.services import llm_client

logger = logging.getLogger(__name__)

# Human-readable labels for each source
_SOURCE_LABELS: dict[str, str] = {
    "jira": "Jira Tickets",
    "confluence": "Confluence Documentation",
    "figma": "Figma Design Screens",
    "basic": "PayFlow Knowledge Base",
}

# Polite no-data message shown when no specialist found matching records
NO_DATA_ANSWER = (
    "I don't have information about that in the PayFlow knowledge base. "
    "I can help with questions about PayFlow's Jira tickets, Confluence documentation, "
    "Figma design screens, or general product knowledge. "
    "Try asking about login, payments, cards, dashboard, or transaction history."
)

# System prompt for LLM synthesis — strict grounding instructions
_SYNTHESIS_SYSTEM_PROMPT = """You are a helpful assistant for the PayFlow fintech application.

Your task is to answer the user's question using ONLY the retrieved data provided below.
Rules:
- Do NOT add information that is not present in the retrieved data.
- Reference specific IDs (like PF-104, CF-005, FG-006) where relevant.
- Be concise and factual.
- If the retrieved data is insufficient to fully answer the question, say so clearly and describe what was found.
- Do not speculate or make up details."""


def synthesize(
    message: str,
    task_description: str,
    results: List[RetrievedItem],
) -> str:
    """
    Generate a grounded answer from the retrieved specialist results.

    Args:
        message:          The original user question.
        task_description: Task context from the orchestrator.
        results:          All items retrieved by the selected specialists.

    Returns:
        A grounded natural language answer string.
    """
    if not results:
        return NO_DATA_ANSWER

    # Try LLM synthesis if configured
    if llm_client.is_available():
        logger.info("LLM synthesis: attempting LLM call...")
        answer = _llm_synthesize(message, task_description, results)
        if answer:
            logger.info("LLM synthesis: success")
            return answer
        logger.warning("LLM synthesis failed — falling back to template")
    else:
        logger.info("LLM synthesis: skipped (no API key), using template")

    return _template_synthesize(results)


def _llm_synthesize(
    message: str,
    task_description: str,
    results: List[RetrievedItem],
) -> Optional[str]:
    """Call the LLM to generate a grounded answer from the retrieved data."""
    # Build the context block from retrieved records
    context_parts: List[str] = []
    for r in results:
        label = _SOURCE_LABELS.get(r.source, r.source)
        context_parts.append(
            f"[{label} — {r.id}]\nTitle: {r.title}\n{r.content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    user_message = (
        f"Retrieved Data:\n{context}\n\n"
        f"User Question: {message}\n"
        f"Task: {task_description}\n\n"
        "Please answer the question using only the retrieved data above."
    )

    return llm_client.complete(_SYNTHESIS_SYSTEM_PROMPT, user_message)


def _template_synthesize(results: List[RetrievedItem]) -> str:
    """
    Format retrieved records into a structured readable answer without an LLM.

    Deterministic — identical results for identical inputs.
    Used when no LLM API key is configured.
    Outputs Markdown so the UI can render it with proper formatting.
    """
    # Group results by source
    by_source: dict[str, list[RetrievedItem]] = {}
    for r in results:
        by_source.setdefault(r.source, []).append(r)

    sections: List[str] = []

    for source, items in by_source.items():
        label = _SOURCE_LABELS.get(source, source)
        block: List[str] = [f"### {label}"]
        for item in items:
            block.append(f"\n**{item.id}** — {item.title}")
            # Jira content uses | as field separator — convert to bullet list
            if source == "jira":
                fields = [f.strip() for f in item.content.split("|") if f.strip()]
                block.append("\n".join(f"- {f}" for f in fields))
            else:
                block.append(f"> {item.content}")
        sections.append("\n".join(block))

    sections.append(
        "\n---\n*Tip: Set `LLM_API_KEY` in your `.env` file for natural language answers.*"
    )

    return "\n\n".join(sections)
