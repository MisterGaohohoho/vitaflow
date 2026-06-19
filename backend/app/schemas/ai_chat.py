from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class AiChatSendRequest(BaseModel):
    content: str


class AiChatDecisionRequest(BaseModel):
    action: Literal["apply", "reject"]


class AiChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    suggestions: list[str] = Field(default_factory=list)
    optimized_resume_data: Optional[dict[str, Any]] = None
    action_status: str = "none"
    create_time: datetime

    model_config = {"from_attributes": True}


class AiChatSendResponse(BaseModel):
    messages: list[AiChatMessageOut]
    assistant_message: AiChatMessageOut


class AiChatDecisionResponse(BaseModel):
    assistant_message: AiChatMessageOut
    resume_data: Optional[dict[str, Any]] = None
