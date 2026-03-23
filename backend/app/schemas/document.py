from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class DocumentUpload(BaseModel):
    title: str
    document_number: Optional[str] = None
    document_type: Optional[str] = None
    legal_field: Optional[str] = None
    issuing_body: Optional[str] = None
    effective_date: Optional[date] = None
    expired_date: Optional[date] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    document_number: Optional[str]
    document_type: Optional[str]
    legal_field: Optional[str]
    issuing_body: Optional[str]
    effective_date: Optional[date]
    expired_date: Optional[date]
    status: str
    is_scanned: bool
    total_pages: int
    processing_status: str
    chunk_count: int
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentSummary(BaseModel):
    document_id: int
    title: str
    summary: str


class SourceReference(BaseModel):
    document_title: str
    document_number: Optional[str]
    chunk_text: str
    relevance_score: float


class QuestionRequest(BaseModel):
    question: str
    legal_field: Optional[str] = None  # Filter by field
    active_only: bool = True  # Only search active documents


class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceReference]
    warning: Optional[str] = None  # Low confidence warning
