"""
Chat API router — defines the POST /chat and GET /health endpoints.

This file contains NO business logic.
It receives requests, delegates to the pipeline, and returns responses.

Teaching note: Separating the API layer from processing logic means
students can change the business logic without touching the HTTP layer,
and vice versa.
"""
import logging
from fastapi import APIRouter
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.core import pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the PayFlow GenAI assistant",
    description=(
        "Send a natural language question about PayFlow. "
        "The system routes it through a guard layer, an orchestrator, "
        "and one or more specialist agents, then returns a structured JSON response "
        "with an answer, routing metadata, citations, and a debug trace."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user question and return a structured GenAI response."""
    logger.info(
        "POST /chat — session=%s role=%s message_length=%d",
        request.session_id or "none",
        request.user_role,
        len(request.message),
    )
    return pipeline.process(request)


@router.get(
    "/health",
    summary="Health check",
    description="Returns service status. Use this to verify the app is running before running Promptfoo evals.",
)
async def health() -> dict:
    """Return service health status."""
    return {"status": "ok", "service": "payflow-genai-demo", "version": "1.0.0"}
