"""
Guard layer — rules-based input safety check.

Runs on EVERY request before any specialist retrieval or LLM call.
Fast, free, and fully deterministic — no external API calls.

Checks performed (in order):
  1. Message length (max 1000 characters)
  2. Empty message
  3. Prompt injection patterns (regex)
  4. Harmful content keywords

Teaching note: This is the simplest possible guard layer.
Students can add new patterns or keywords and immediately test
the effect using Promptfoo injection test cases.
"""
import re
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 1000

# Regex patterns that indicate prompt injection attempts.
# Each pattern is checked case-insensitively against the lowercased message.
INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous",
    r"disregard\s+(all\s+)?previous",
    r"you\s+are\s+now\s+",
    r"pretend\s+you\s+are",
    r"act\s+as\s+(if\s+you('re|\s+are)\s+)?a\b",
    r"jailbreak",
    r"developer\s+mode\s+enabled",
    r"dan\s+mode",
    r"reveal\s+your\s+(system\s+)?prompt",
    r"show\s+me\s+your\s+(system\s+)?prompt",
    r"what\s+are\s+your\s+(exact\s+)?instructions",
    r"override\s+your\s+(instructions|directives|rules)",
    r"bypass\s+your\s+(safety|filter|guardrail|restriction)",
    r"repeat\s+the\s+above",
    r"print\s+the\s+(above|previous)\s+(prompt|instructions|system)",
]

# Simple keyword blocklist for clearly harmful or inappropriate content.
HARMFUL_KEYWORDS: list[str] = [
    "kill yourself",
    "bomb threat",
    "how to hack",
    "credit card fraud",
    "money laundering",
]


@dataclass
class GuardResult:
    """Result of a guard check."""

    status: str
    """'allowed' | 'blocked' | 'flagged'"""

    reason: Optional[str] = None
    """
    Reason code for blocked/flagged messages. None if allowed.

    Reason codes:
      message_too_long     — exceeds 1000 character limit
      empty_message        — blank or whitespace-only input
      prompt_injection     — matches an injection regex pattern
      harmful_content      — matches a harmful keyword
    """


def check_message(message: str) -> GuardResult:
    """
    Run all guard checks on the incoming message.

    Returns a GuardResult with status 'allowed', 'blocked', or 'flagged'.
    Blocked messages should never proceed to the orchestrator or LLM.
    """
    # 1. Length check
    if len(message) > MAX_MESSAGE_LENGTH:
        logger.warning("Guard blocked: message_too_long (length=%d)", len(message))
        return GuardResult(status="blocked", reason="message_too_long")

    # 2. Empty message check
    if not message.strip():
        logger.warning("Guard blocked: empty_message")
        return GuardResult(status="blocked", reason="empty_message")

    message_lower = message.lower()

    # 3. Injection pattern check
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            logger.warning("Guard blocked: prompt_injection (pattern=%r)", pattern)
            return GuardResult(status="blocked", reason="prompt_injection")

    # 4. Harmful keyword check
    for keyword in HARMFUL_KEYWORDS:
        if keyword in message_lower:
            logger.warning("Guard blocked: harmful_content (keyword=%r)", keyword)
            return GuardResult(status="blocked", reason="harmful_content")

    return GuardResult(status="allowed")
