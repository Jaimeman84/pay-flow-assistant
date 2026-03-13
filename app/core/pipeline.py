"""
Pipeline — coordinates the full request processing flow.

This is the single entry point that the API layer calls.
It chains together all system components in order:

  Guard → Orchestrator → Specialists → Synthesis → Response

Each step appends to the debug.steps list so the full processing
trace is visible in every API response.

Teaching note: Read this file alongside workflow.md to see how
the documented workflow maps directly to the code.
"""
import logging

from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse, RouteInfo, DebugInfo, Citation
from app.core import guard, orchestrator, synthesizer
from app.specialists.base import RetrievalTask, RetrievedItem
from app.specialists.jira_specialist import JiraSpecialist
from app.specialists.confluence_specialist import ConfluenceSpecialist
from app.specialists.figma_specialist import FigmaSpecialist
from app.specialists.basic_specialist import BasicSpecialist

logger = logging.getLogger(__name__)

# Safe refusal message returned for all blocked requests
_BLOCKED_ANSWER = (
    "I'm unable to process that request. "
    "Please ask a question about the PayFlow application."
)

# Instantiate all specialist agents once at module load
_SPECIALISTS = {
    "jira": JiraSpecialist(),
    "confluence": ConfluenceSpecialist(),
    "figma": FigmaSpecialist(),
    "basic": BasicSpecialist(),
}


def process(request: ChatRequest) -> ChatResponse:
    """
    Process a ChatRequest through the full pipeline and return a ChatResponse.

    Always returns a structured ChatResponse — never raises an exception.
    Errors are caught and surfaced as safe error messages in the response.
    """
    steps: list[str] = []
    session = request.session_id or "no-session"

    try:
        return _run_pipeline(request, steps, session)
    except Exception as e:
        logger.error("[%s] Unhandled pipeline error: %s", session, e, exc_info=True)
        steps.append(f"Unhandled error: {type(e).__name__}")
        return _error_response(steps)


def _run_pipeline(
    request: ChatRequest,
    steps: list[str],
    session: str,
) -> ChatResponse:
    """Internal pipeline execution — may raise; caller handles exceptions."""

    # ── Step 1: Guard check ──────────────────────────────────────────────────
    guard_result = guard.check_message(request.message)

    step_label = f"Guard check: {guard_result.status}"
    if guard_result.reason:
        step_label += f" ({guard_result.reason})"
    steps.append(step_label)
    logger.info("[%s] %s", session, step_label)

    if guard_result.status == "blocked":
        return ChatResponse(
            answer=_BLOCKED_ANSWER,
            route=RouteInfo(
                guard_status="blocked",
                guard_reason=guard_result.reason,
                selected_specialists=[],
                orchestrator_decision=None,
            ),
            citations=[],
            debug=DebugInfo(app_specialist_task=None, steps=steps),
        )

    # ── Step 2: Orchestrator — routing and task building ─────────────────────
    routing = orchestrator.route(request.message)

    steps.append(f"Orchestrator decision: {routing.orchestrator_decision}")
    steps.append(f"Routing to specialists: {', '.join(routing.selected_specialists)}")
    if routing.feature_area:
        steps.append(f"Feature area detected: {routing.feature_area}")

    logger.info(
        "[%s] %s → %s (feature: %s)",
        session,
        routing.orchestrator_decision,
        routing.selected_specialists,
        routing.feature_area,
    )

    # ── Step 3: Specialist retrieval ─────────────────────────────────────────
    task = RetrievalTask(
        message=request.message,
        feature_area=routing.feature_area,
        keywords=routing.keywords,
    )

    all_results: list[RetrievedItem] = []

    for name in routing.selected_specialists:
        specialist = _SPECIALISTS.get(name)
        if specialist is None:
            steps.append(f"{name.capitalize()} specialist: unknown — skipped")
            continue

        try:
            results = specialist.retrieve(task)
            all_results.extend(results)
            steps.append(
                f"{name.capitalize()} specialist: {len(results)} result(s) retrieved"
            )
            logger.debug("[%s] %s specialist: %d results", session, name, len(results))
        except Exception as e:
            logger.error("[%s] %s specialist failed: %s", session, name, e)
            steps.append(f"{name.capitalize()} specialist: error — skipped")

    # ── Step 4: Synthesis ────────────────────────────────────────────────────
    answer = synthesizer.synthesize(request.message, routing.task_description, all_results)
    steps.append("Answer synthesized")

    # ── Step 5: Build response ───────────────────────────────────────────────
    citations = [
        Citation(source=r.source, id=r.id, title=r.title)
        for r in all_results
    ]
    steps.append(f"Response assembled with {len(citations)} citation(s)")

    logger.info("[%s] Response ready — %d citation(s)", session, len(citations))

    return ChatResponse(
        answer=answer,
        route=RouteInfo(
            guard_status=guard_result.status,
            guard_reason=guard_result.reason,
            selected_specialists=routing.selected_specialists,
            orchestrator_decision=routing.orchestrator_decision,
        ),
        citations=citations,
        debug=DebugInfo(
            app_specialist_task=routing.task_description,
            steps=steps,
        ),
    )


def _error_response(steps: list[str]) -> ChatResponse:
    """Safe error response returned when an unhandled exception occurs."""
    return ChatResponse(
        answer=(
            "An error occurred while processing your request. "
            "Please try again or contact support."
        ),
        route=RouteInfo(
            guard_status="allowed",
            guard_reason=None,
            selected_specialists=[],
            orchestrator_decision=None,
        ),
        citations=[],
        debug=DebugInfo(app_specialist_task=None, steps=steps),
    )
