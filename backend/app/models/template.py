from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from datetime import datetime, timezone
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # hợp đồng, đơn từ, biên bản
    description = Column(Text, nullable=True)
    fields = Column(JSON, nullable=False)  # [{"name": "...", "label": "...", "type": "text"}]
    content_template = Column(Text, nullable=False)  # Template with {{field}} placeholders
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
