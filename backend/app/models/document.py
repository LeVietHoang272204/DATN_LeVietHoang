from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Document(Base):
    """Legal documents with versioning metadata."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    document_number = Column(String(100), index=True)  # e.g. "45/2013/QH13"
    document_type = Column(String(100))  # Luật, Nghị định, Thông tư, etc.
    legal_field = Column(String(100), index=True)  # Đất đai, Lao động, Dân sự
    issuing_body = Column(String(255))  # Quốc hội, Chính phủ, etc.

    # -- Versioning (improvement) --
    effective_date = Column(Date, nullable=True)
    expired_date = Column(Date, nullable=True)
    status = Column(String(50), default="active")  # active, expired, replaced
    replaces_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # -- Processing info --
    file_path = Column(String(500))
    file_type = Column(String(10))  # pdf, docx
    is_scanned = Column(Boolean, default=False)
    total_pages = Column(Integer, default=0)
    processing_status = Column(String(20), default="pending")  # pending, processing, done, error
    processing_error = Column(Text, nullable=True)

    # -- Content --
    raw_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_public = Column(Boolean, default=True)  # Public legal docs vs personal docs
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="documents")
    replaced_by = relationship("Document", remote_side="Document.id")
