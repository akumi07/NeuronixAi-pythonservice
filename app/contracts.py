"""Pydantic models matching backend/docs/contracts/ai-service.yaml.

If you change a model here, change the contract YAML in the same PR (and vice versa).
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for every contract model: camelCase JSON, unknown fields rejected."""

    model_config = ConfigDict(
        alias_generator=to_camel,  # python user_id <-> JSON "userId"
        populate_by_name=True,  # also allow ChatTurnRequest(user_id=...) in Python code
        extra="forbid",  # reject any field that is not in the contract
    )


class AgentName(str, Enum):
    PLANNING = "planning"
    CODING = "coding"
    RESEARCH = "research"
    KNOWLEDGE = "knowledge"
    GENERAL = "general"


# ---------- Java -> Python: POST /internal/v1/chat/turn ----------


class HistoryMessage(ApiModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatTurnRequest(ApiModel):
    request_id: str
    user_id: int
    conversation_id: int
    message: str = Field(min_length=1, max_length=8000)
    selected_agent: AgentName | None = None
    document_ids: list[int] = Field(default_factory=list, max_length=100)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=50)


class Citation(ApiModel):
    document_id: int
    page: int = Field(ge=1)
    chunk_id: int
    snippet: str


class ChatTurnResponse(ApiModel):
    answer: str
    agent: AgentName
    route_reason: str
    citations: list[Citation] = Field(default_factory=list)
    thread_id: str
    status: Literal["completed", "interrupted", "failed"]


# ---------- Python -> Java: POST /internal/v1/rag/retrieve ----------


class RetrieveRequest(ApiModel):
    user_id: int
    document_ids: list[int] = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(ApiModel):
    chunk_id: int
    document_id: int
    page: int = Field(ge=1)
    text: str
    score: float


class RetrieveResponse(ApiModel):
    chunks: list[RetrievedChunk]


# ---------- Shared error shape (same as the Java backend) ----------


class ErrorResponse(ApiModel):
    timestamp: datetime
    status: int
    error: str
    message: str
    path: str
    field_errors: dict[str, str] | None = None