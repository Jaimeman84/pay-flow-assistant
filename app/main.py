"""
FastAPI application entry point for the PayFlow GenAI Demo.

Start the server with:
    uvicorn app.main:app --reload --port 8000

Teaching note: This file is intentionally minimal.
It sets up the app, middleware, and router registration.
All logic lives in the core/, specialists/, and services/ layers.
"""
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(override=True)
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.services.data_loader import get_store

# ── Logging configuration ────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Application lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load all data files at startup so the first request is fast."""
    logger.info("PayFlow GenAI Demo starting up...")
    get_store()  # Loads and caches all JSON data files
    # Log LLM status so it's visible on startup
    api_key = os.getenv("LLM_API_KEY", "")
    if api_key.strip():
        provider = os.getenv("LLM_PROVIDER", "anthropic")
        model = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
        logger.info("LLM synthesis ENABLED — provider=%s model=%s key=...%s", provider, model, api_key[-6:])
    else:
        logger.warning("LLM synthesis DISABLED — LLM_API_KEY not set, using template fallback")
    logger.info("PayFlow GenAI Demo ready.")
    yield
    logger.info("PayFlow GenAI Demo shutting down.")


# ── FastAPI application ───────────────────────────────────────────────────────
app = FastAPI(
    title="PayFlow GenAI Demo",
    description=(
        "An educational demonstration of specialist agents in a GenAI-based system. "
        "Ask questions about the fictional PayFlow fintech application across "
        "Jira tickets, Confluence docs, Figma screens, and general knowledge."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow all origins for local demo use ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
