from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class MediaFile(Base):
    """Personal media library - files uploaded by users for Personal Document RAG."""

    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10))  # pdf, docx, png, jpg
    file_size = Column(Integer, default=0)  # bytes
    cloudinary_url = Column(String(500), nullable=True)
    cloudinary_public_id = Column(String(255), nullable=True)

    # Processing
    processing_status = Column(String(20), default="pending")
    is_indexed = Column(Boolean, default=False)  # Indexed in personal vector store
    extracted_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="media_files")
