from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class TemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]
    fields: List[Any]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    fields: List[dict]
    content_template: str


class TemplateGenerate(BaseModel):
    template_id: int
    field_values: dict  # {"field_name": "value"}
    output_format: str = "docx"  # "docx" or "pdf"
