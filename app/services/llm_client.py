"""
LLM client service — thin wrapper around the configured LLM API.

All LLM calls in the system go through this module.
This makes it easy to swap providers (Anthropic → OpenAI → Ollama) by changing one file.

Configuration via environment variables:
    LLM_PROVIDER  — "anthropic" (default) or "openai"
    LLM_MODEL     — model identifier (default: claude-3-5-haiku-20241022)
    LLM_API_KEY   — API key (optional — app works without it using template synthesis)

Teaching note: The app is fully functional without an API key.
Without a key, synthesis falls back to structured template formatting.
With a key, synthesis uses the LLM to generate natural language answers.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def is_available() -> bool:
    """Return True if an LLM API key is configured."""
    return bool(os.getenv("LLM_API_KEY", "").strip())


def complete(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1024,
) -> Optional[str]:
    """
    Call the configured LLM API and return the response text.

    Returns None if:
    - No API key is configured
    - The API call fails (timeout, rate limit, error)
    - An unsupported provider is configured

    Supports:
    - "anthropic" (default): uses the Anthropic Messages API
    - "openai": uses the OpenAI Chat Completions API
    """
    if not is_available():
        logger.debug("LLM_API_KEY not set — skipping LLM call")
        return None

    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    model = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
    api_key = os.getenv("LLM_API_KEY")

    try:
        if provider == "anthropic":
            return _call_anthropic(api_key, model, system_prompt, user_message, max_tokens)
        elif provider == "openai":
            return _call_openai(api_key, model, system_prompt, user_message, max_tokens)
        else:
            logger.warning("Unknown LLM_PROVIDER: %s — skipping LLM call", provider)
            return None

    except Exception as e:
        logger.error("LLM call failed (%s / %s): %s: %s", provider, model, type(e).__name__, e)
        return None


def _call_anthropic(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int,
) -> str:
    """Call the Anthropic Messages API."""
    try:
        import anthropic
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        raise

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _call_openai(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int,
) -> str:
    """Call the OpenAI Chat Completions API."""
    try:
        import openai
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai")
        raise

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
