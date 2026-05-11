import os
import shutil
import uuid
import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.document import Document
from app.ai.ingestion import process_document
from app.ai.rag_pipeline import summarize_text, query_legal
from app.ai.legal_classifier import is_meaningless_title, auto_generate_title
from app.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_and_process(
    db: Session,
    file: UploadFile,
    title: str,
    owner_id: Optional[int] = None,
    is_public: bool = True,
    document_number: Optional[str] = None,
    document_type: Optional[str] = None,
    legal_field: Optional[str] = None,
    issuing_body: Optional[str] = None,
    effective_date=None,
    expired_date=None,
) -> Document:
    """Upload a document, process through ingestion pipeline, and save to DB."""
    # Save file to disk
    ext = os.path.splitext(file.filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)

    # Create DB record
    doc = Document(
        title=title,
        document_number=document_number,
        document_type=document_type,
        legal_field=legal_field,
        issuing_body=issuing_body,
        effective_date=effective_date,
        expired_date=expired_date,
        file_path=file_path,
        file_type=ext.lstrip("."),
        owner_id=owner_id,
        is_public=is_public,
        processing_status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Determine collection: public or personal
    collection = None
    if not is_public and owner_id:
        collection = f"user_{owner_id}"

    # Process through ingestion pipeline
    metadata = {
        "document_id": doc.id,
        "document_title": title,
        "document_number": document_number or "",
        "legal_field": legal_field or "",
        "document_type": document_type or "",
    }

    result = process_document(file_path, metadata=metadata, collection_name=collection)

    doc.processing_status = result["status"]
    doc.is_scanned = result.get("is_scanned", False)
    doc.total_pages = result.get("total_pages", 0)
    doc.chunk_count = result.get("chunks", 0)
    doc.raw_text = result.get("text", "")
    doc.processing_error = result.get("error")

    # Ghi lại lĩnh vực pháp luật tự phân loại nếu người dùng không chỉ định
    if not doc.legal_field and result.get("auto_legal_field"):
        doc.legal_field = result["auto_legal_field"]

    # Tự động đặt tên nếu tên hiện tại vô nghĩa (chỉ số, UUID, ...)
    raw_text = result.get("text", "")
    if raw_text and is_meaningless_title(doc.title):
        better_title = auto_generate_title(
            text=raw_text,
            filename=file.filename or title,
            google_api_key=settings.GOOGLE_API_KEY,
            gemini_model=settings.GEMINI_MODEL,
        )
        if better_title and better_title != doc.title:
            doc.title = better_title
            logger.info(f"Document {doc.id} renamed: '{title}' -> '{better_title}'")

    db.commit()
    db.refresh(doc)
    return doc


def get_documents(
    db: Session,
    owner_id: Optional[int] = None,
    legal_field: Optional[str] = None,
    public_only: bool = False,
):
    query = db.query(Document)
    if public_only:
        query = query.filter(Document.is_public == True)
    if owner_id:
        query = query.filter(Document.owner_id == owner_id)
    if legal_field:
        query = query.filter(Document.legal_field == legal_field)
    return query.order_by(Document.created_at.desc()).all()


def get_document_by_id(db: Session, doc_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == doc_id).first()


def summarize_document(db: Session, doc_id: int, length: str = "trung bình") -> str:
    doc = get_document_by_id(db, doc_id)
    if not doc or not doc.raw_text:
        return "Không thể tóm tắt: tài liệu chưa được xử lý."
    summary = summarize_text(doc.raw_text, summary_length=length)
    doc.summary = summary
    db.commit()
    return summary


def ask_question(
    question: str,
    legal_field: Optional[str] = None,
    collection_name: Optional[str] = None,
    chat_history: Optional[list] = None,
) -> dict:
    return query_legal(
        question=question,
        collection_name=collection_name,
        legal_field=legal_field,
        chat_history=chat_history,
    )


def delete_document(db: Session, doc_id: int, owner_id: int) -> bool:
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.owner_id == owner_id
    ).first()
    if not doc:
        return False
    # Remove file
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()
    return True
