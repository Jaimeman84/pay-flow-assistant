"""
Request schema for the POST /chat endpoint.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Incoming user message for the PayFlow GenAI assistant."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The user's natural language question about PayFlow.",
        examples=["What Jira bugs are blocking the payment release?"],
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for request tracing.",
        examples=["demo-session-001"],
    )
    user_role: str = Field(
        default="student",
        description="User role — used for logging and future role-based routing.",
        examples=["student", "instructor", "developer"],
    )
