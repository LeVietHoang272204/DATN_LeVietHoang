from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# --- Event ---
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    legal_field: Optional[str] = None
    start_time: datetime
    end_time: datetime
    max_questions: int = 10


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    legal_field: Optional[str]
    start_time: datetime
    end_time: datetime
    is_active: bool
    max_questions: int
    question_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Question ---
class QuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 10


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    options: List[str]
    points: int

    model_config = {"from_attributes": True}


# --- Submission ---
class AnswerSubmission(BaseModel):
    answers: dict  # {question_id: "user_answer"}


class ScoreResponse(BaseModel):
    id: int
    event_id: int
    score: int
    total_questions: int
    correct_answers: int
    completed_at: datetime

    model_config = {"from_attributes": True}


class ScoreHistory(BaseModel):
    scores: List[ScoreResponse]
    total_accumulated: int
