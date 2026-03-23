from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.media import MediaFileResponse, MediaFileRename
from app.services import media_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/media", tags=["Media Library"])


@router.post("/upload", response_model=MediaFileResponse)
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = (".pdf", ".docx", ".png", ".jpg", ".jpeg")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ hỗ trợ các định dạng: {', '.join(allowed)}",
        )
    return media_service.upload_media(db, file, current_user.id)


@router.get("/", response_model=list[MediaFileResponse])
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return media_service.get_user_media(db, current_user.id)


@router.put("/{media_id}/rename", response_model=MediaFileResponse)
def rename_file(
    media_id: int,
    data: MediaFileRename,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    media = media_service.rename_media(db, media_id, current_user.id, data.new_filename)
    if not media:
        raise HTTPException(status_code=404, detail="File không tồn tại")
    return media


@router.delete("/{media_id}")
def delete_file(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not media_service.delete_media(db, media_id, current_user.id):
        raise HTTPException(status_code=404, detail="File không tồn tại")
    return {"detail": "Đã xóa file"}
