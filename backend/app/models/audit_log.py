from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base
from datetime import datetime, timezone
import uuid


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    event_type = Column(String(128), nullable=False, index=True)
    resource_type = Column(String(64), nullable=True)
    resource_id = Column(String(256), nullable=True, index=True)
    ip_address = Column(String(64), nullable=True)
    result = Column(String(16), nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)