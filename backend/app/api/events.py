from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.event import (
    EventCreate, EventResponse, QuestionCreate, QuestionResponse,
    AnswerSubmission, ScoreResponse, ScoreHistory,
)
from app.services import event_service
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.ai.quiz_generator import generate_quiz_from_field
from app.ai.legal_classifier import FIELD_LABELS
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/events", tags=["Events"])


class QuizGenerateRequest(BaseModel):
    legal_field: str = "khac"
    count: int = 5
    difficulty: str = "trung-bình"  # dễ | trung-bình | khó


# --- Public ---
@router.get("/", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)):
    return event_service.get_events(db)


@router.get("/{event_id}/questions", response_model=list[QuestionResponse])
def get_questions(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return event_service.get_event_questions(db, event_id)


@router.post("/{event_id}/submit", response_model=ScoreResponse)
def submit_answers(
    event_id: int,
    submission: AnswerSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return event_service.submit_answers(
        db, current_user.id, event_id, submission.answers
    )


@router.get("/scores/me", response_model=ScoreHistory)
def my_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return event_service.get_user_scores(db, current_user.id)


# --- Admin ---
@router.post("/", response_model=EventResponse)
def create_event(
    data: EventCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return event_service.create_event(
        db, admin.id,
        title=data.title,
        description=data.description,
        legal_field=data.legal_field,
        start_time=data.start_time,
        end_time=data.end_time,
        max_questions=data.max_questions,
    )


@router.post("/{event_id}/ai-generate", response_model=list[QuestionResponse])
def ai_generate_questions(
    event_id: int,
    req: QuizGenerateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """AI tự sinh câu hỏi quiz từ các tài liệu pháp luật trong collection.

    Admin chỉ cần chọn lĩnh vực + số câu + mức độ, hệ thống tự sinh và lưu vào event.
    """
    event = event_service.get_event_detail(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Không tìm thấy sự kiện")

    questions = generate_quiz_from_field(
        legal_field=req.legal_field,
        count=req.count,
        difficulty=req.difficulty,
    )

    if not questions:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Không có tài liệu '{FIELD_LABELS.get(req.legal_field, req.legal_field)}' "
                "trong cơ sở dữ liệu. Hãy upload văn bản pháp luật trước."
            ),
        )

    saved = []
    for q in questions:
        opts = q.get("options", [])
        if isinstance(opts, dict):
            opts = [f"{k}. {v}" for k, v in opts.items()]
        saved.append(
            event_service.add_question(
                db, event_id,
                question_text=q["question_text"],
                options=opts,
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation", ""),
                points=q.get("points", 10),
            )
        )
    return saved


@router.post("/{event_id}/questions", response_model=QuestionResponse)
def add_question(
    event_id: int,
    data: QuestionCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return event_service.add_question(
        db, event_id,
        question_text=data.question_text,
        options=data.options,
        correct_answer=data.correct_answer,
        explanation=data.explanation,
        points=data.points,
    )


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not event_service.delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    return {"detail": "Đã xóa sự kiện"}
