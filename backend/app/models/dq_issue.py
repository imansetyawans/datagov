from sqlalchemy import Column, String, Float, DateTime, Text
from app.database import Base
import uuid
from datetime import datetime, timezone


class DQIssue(Base):
    __tablename__ = "dq_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), nullable=False, index=True)
    column_id = Column(String(36), nullable=True)
    metric = Column(String(32), nullable=False)
    severity = Column(String(16), nullable=False)
    status = Column(String(16), nullable=False, default="open")
    previous_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    delta = Column(Float, nullable=True)
    resolution_note = Column(Text, nullable=True)
    resolved_by = Column(String(36), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))