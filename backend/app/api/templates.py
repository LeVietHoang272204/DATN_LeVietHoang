from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.template import TemplateResponse, TemplateCreate, TemplateGenerate
from app.services import template_service
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.get("/", response_model=list[TemplateResponse])
def list_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return template_service.get_templates(db, category)


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    tpl = template_service.get_template_by_id(db, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template không tồn tại")
    return tpl


@router.post("/generate")
def generate_document(
    data: TemplateGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return template_service.generate_document(
        db, data.template_id, data.field_values, data.output_format
    )


# --- Admin ---
@router.post("/", response_model=TemplateResponse)
def create_template(
    data: TemplateCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return template_service.create_template(
        db,
        name=data.name,
        category=data.category,
        description=data.description,
        fields=data.fields,
        content_template=data.content_template,
    )
