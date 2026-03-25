from typing import List, Optional

from pydantic import BaseModel
from typing_extensions import Literal


class ChatMessageIn(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str
    sender: Optional[str] = None
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None


class ChatRequest(BaseModel):
    mode: Literal["single", "multi"]
    messages: List[ChatMessageIn]
    max_turns: int = 6


class ChatMessageOut(BaseModel):
    role: Literal["assistant", "tool"]
    content: str
    sender: Optional[str] = None
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None


class ChatResponse(BaseModel):
    activeAgent: str
    messages: List[ChatMessageOut]
