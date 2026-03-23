from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.document import (
    DocumentResponse, QuestionRequest, AnswerResponse, DocumentSummary,
)
from app.services import document_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_number: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    legal_field: Optional[str] = Form(None),
    issuing_body: Optional[str] = Form(None),
    is_public: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF và DOCX")
    return document_service.upload_and_process(
        db=db,
        file=file,
        title=title,
        owner_id=current_user.id,
        is_public=is_public,
        document_number=document_number,
        document_type=document_type,
        legal_field=legal_field,
        issuing_body=issuing_body,
    )


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    legal_field: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return document_service.get_documents(
        db, owner_id=current_user.id, legal_field=legal_field
    )


@router.get("/public", response_model=list[DocumentResponse])
def list_public_documents(
    legal_field: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return document_service.get_documents(db, legal_field=legal_field, public_only=True)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Tài liệu không tồn tại")
    return doc


@router.post("/{doc_id}/summarize", response_model=DocumentSummary)
def summarize_document(
    doc_id: int,
    length: str = "trung bình",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    summary = document_service.summarize_document(db, doc_id, length)
    doc = document_service.get_document_by_id(db, doc_id)
    return {"document_id": doc_id, "title": doc.title, "summary": summary}


@router.post("/ask", response_model=AnswerResponse)
def ask_question(
    req: QuestionRequest,
    current_user: User = Depends(get_current_user),
):
    result = document_service.ask_question(
        question=req.question,
        legal_field=req.legal_field,
    )
    return result


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not document_service.delete_document(db, doc_id, current_user.id):
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return {"detail": "Đã xóa tài liệu"}
