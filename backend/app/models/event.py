from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    legal_field = Column(String(100))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    max_questions = Column(Integer, default=10)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questions = relationship(
        "EventQuestion", back_populates="event", cascade="all, delete"
    )
    scores = relationship("EventScore", back_populates="event", cascade="all, delete")


class EventQuestion(Base):
    __tablename__ = "event_questions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # ["A", "B", "C", "D"]
    correct_answer = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=10)

    event = relationship("Event", back_populates="questions")


class EventScore(Base):
    __tablename__ = "event_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    answers_detail = Column(JSON, nullable=True)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="event_scores")
    event = relationship("Event", back_populates="scores")
