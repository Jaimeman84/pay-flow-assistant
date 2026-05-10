"""
Request schema for the POST /chat endpoint.
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Union


class Message(BaseModel):
    """A single turn in a multi-turn conversation."""

    role: str = Field(..., examples=["user", "assistant", "system"])
    content: str = Field(default="")


class ChatRequest(BaseModel):
    """Incoming user message for the PayFlow GenAI assistant.

    Accepts three equivalent forms:
      - message: str              — single-turn string
      - message: List[Message]    — multi-turn array in the message field (promptfoo body-template behaviour)
      - messages: List[Message]   — multi-turn array in a dedicated field
    In all multi-turn cases the pipeline extracts the last user turn as the effective message.
    """

    message: Optional[Union[str, List[Message]]] = Field(
        default=None,
        description="Single-turn string question, or a multi-turn messages array.",
        examples=["What Jira bugs are blocking the payment release?"],
    )
    messages: Optional[List[Message]] = Field(
        default=None,
        description="Full conversation history for multi-turn requests. "
                    "The pipeline uses the last user turn as the effective message.",
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

    @model_validator(mode="after")
    def require_message_or_messages(self) -> "ChatRequest":
        if not self.message and not self.messages:
            raise ValueError("Provide either 'message' (string) or 'messages' (list).")
        return self
