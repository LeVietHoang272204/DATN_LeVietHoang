from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[int] = None  # None = create new session
    use_personal_docs: bool = False  # Use personal document RAG


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    confidence_score: Optional[float]
    sources: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ChatSessionDetail(BaseModel):
    id: int
    title: str
    messages: List[ChatMessageResponse]
    created_at: datetime

    model_config = {"from_attributes": True}
