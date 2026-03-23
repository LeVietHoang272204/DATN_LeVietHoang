from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # "user" | "admin"
    is_active = Column(Boolean, default=True)
    theme = Column(String(10), default="light")  # "light" | "dark"
    font_size = Column(Integer, default=16)
    total_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete")
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete"
    )
    event_scores = relationship(
        "EventScore", back_populates="user", cascade="all, delete"
    )
    media_files = relationship(
        "MediaFile", back_populates="owner", cascade="all, delete"
    )
