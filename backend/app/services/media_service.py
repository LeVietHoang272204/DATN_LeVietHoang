import os
import shutil
import uuid
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.media import MediaFile
from app.ai.ingestion import process_document
from app.ai.legal_classifier import is_meaningless_title, auto_generate_title
from app.config import settings

logger = logging.getLogger(__name__)

MEDIA_DIR = "uploads/media"
os.makedirs(MEDIA_DIR, exist_ok=True)


def upload_media(db: Session, file: UploadFile, owner_id: int) -> MediaFile:
    """Upload a personal file, save it, and index for personal RAG."""
    ext = os.path.splitext(file.filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, safe_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)

    media = MediaFile(
        owner_id=owner_id,
        filename=safe_name,
        original_filename=file.filename,
        file_type=ext.lstrip("."),
        file_size=file_size,
        processing_status="processing",
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    # Process and index into personal collection
    if ext in (".pdf", ".docx"):
        collection = f"user_{owner_id}"
        metadata = {
            "media_id": media.id,
            "document_title": file.filename,
            "owner_id": owner_id,
        }
        result = process_document(file_path, metadata=metadata, collection_name=collection)
        media.processing_status = result["status"]
        media.is_indexed = result["status"] == "done"
        media.extracted_text = result.get("text", "")[:5000]

        # Tự đặt tên nếu tên file gốc vô nghĩa
        raw_text = result.get("text", "")
        if raw_text and is_meaningless_title(file.filename or ""):
            better_name = auto_generate_title(
                text=raw_text,
                filename=file.filename or safe_name,
                google_api_key=settings.GOOGLE_API_KEY,
                gemini_model=settings.GEMINI_MODEL,
            )
            if better_name:
                media.original_filename = better_name
    else:
        media.processing_status = "done"

    db.commit()
    db.refresh(media)
    return media


def get_user_media(db: Session, owner_id: int) -> List[MediaFile]:
    return (
        db.query(MediaFile)
        .filter(MediaFile.owner_id == owner_id)
        .order_by(MediaFile.created_at.desc())
        .all()
    )


def rename_media(db: Session, media_id: int, owner_id: int, new_name: str) -> Optional[MediaFile]:
    media = db.query(MediaFile).filter(
        MediaFile.id == media_id, MediaFile.owner_id == owner_id
    ).first()
    if not media:
        return None
    media.original_filename = new_name
    db.commit()
    db.refresh(media)
    return media


def delete_media(db: Session, media_id: int, owner_id: int) -> bool:
    media = db.query(MediaFile).filter(
        MediaFile.id == media_id, MediaFile.owner_id == owner_id
    ).first()
    if not media:
        return False
    file_path = os.path.join(MEDIA_DIR, media.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(media)
    db.commit()
    return True
