from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MediaFileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: Optional[str]
    file_size: int
    cloudinary_url: Optional[str]
    processing_status: str
    is_indexed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MediaFileRename(BaseModel):
    new_filename: str
