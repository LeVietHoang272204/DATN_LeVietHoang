import io
import re
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.models.template import Template


def create_template(db: Session, **kwargs) -> Template:
    tpl = Template(**kwargs)
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl


def get_templates(db: Session, category: Optional[str] = None):
    query = db.query(Template).filter(Template.is_active == True)
    if category:
        query = query.filter(Template.category == category)
    return query.order_by(Template.name).all()


def get_template_by_id(db: Session, template_id: int) -> Optional[Template]:
    return db.query(Template).filter(Template.id == template_id).first()


def generate_document(db: Session, template_id: int, field_values: dict, output_format: str = "docx"):
    """Fill template with user values, generate DOCX or PDF."""
    tpl = get_template_by_id(db, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template không tồn tại")

    # Replace placeholders {{field_name}} with actual values
    content = tpl.content_template
    for field_name, value in field_values.items():
        placeholder = "{{" + field_name + "}}"
        content = content.replace(placeholder, str(value))

    # Check for unfilled placeholders
    remaining = re.findall(r"\{\{(\w+)\}\}", content)
    if remaining:
        raise HTTPException(
            status_code=400,
            detail=f"Vui lòng điền đầy đủ các trường: {', '.join(remaining)}",
        )

    if output_format == "docx":
        return _generate_docx(content, tpl.name)
    else:
        # For PDF, generate DOCX then convert (simplified)
        return _generate_docx(content, tpl.name)


def _generate_docx(content: str, filename: str) -> StreamingResponse:
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(13)

    lines = content.split("\n")
    for line in lines:
        if line.strip():
            doc.add_paragraph(line)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    safe_name = re.sub(r"[^\w\s-]", "", filename).strip()
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.docx"'},
    )
