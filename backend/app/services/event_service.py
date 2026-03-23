from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.event import Event, EventQuestion, EventScore
from app.models.user import User


def create_event(db: Session, admin_id: int, **kwargs) -> Event:
    event = Event(created_by=admin_id, **kwargs)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events(db: Session, active_only: bool = True) -> List[Event]:
    query = db.query(Event)
    if active_only:
        query = query.filter(Event.is_active == True)
    events = query.order_by(Event.start_time.desc()).all()
    for e in events:
        e.question_count = len(e.questions)
    return events


def get_event_detail(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()


def add_question(db: Session, event_id: int, **kwargs) -> EventQuestion:
    question = EventQuestion(event_id=event_id, **kwargs)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_event_questions(db: Session, event_id: int) -> List[EventQuestion]:
    return db.query(EventQuestion).filter(EventQuestion.event_id == event_id).all()


def submit_answers(
    db: Session, user_id: int, event_id: int, answers: dict
) -> EventScore:
    """Grade user's answers and save score."""
    questions = get_event_questions(db, event_id)
    if not questions:
        raise HTTPException(status_code=404, detail="Sự kiện không có câu hỏi")

    # Check if already submitted
    existing = db.query(EventScore).filter(
        EventScore.user_id == user_id, EventScore.event_id == event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bạn đã tham gia sự kiện này rồi")

    correct = 0
    total = len(questions)
    total_score = 0
    detail = {}

    for q in questions:
        user_answer = answers.get(str(q.id), "")
        is_correct = user_answer == q.correct_answer
        if is_correct:
            correct += 1
            total_score += q.points
        detail[str(q.id)] = {
            "user_answer": user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "points": q.points if is_correct else 0,
        }

    score = EventScore(
        user_id=user_id,
        event_id=event_id,
        score=total_score,
        total_questions=total,
        correct_answers=correct,
        answers_detail=detail,
    )
    db.add(score)

    # Update user total score
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.total_score = (user.total_score or 0) + total_score

    db.commit()
    db.refresh(score)
    return score


def get_user_scores(db: Session, user_id: int) -> dict:
    scores = (
        db.query(EventScore)
        .filter(EventScore.user_id == user_id)
        .order_by(EventScore.completed_at.desc())
        .all()
    )
    total = sum(s.score for s in scores)
    return {"scores": scores, "total_accumulated": total}


def delete_event(db: Session, event_id: int) -> bool:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return False
    db.delete(event)
    db.commit()
    return True
