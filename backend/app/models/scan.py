from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base
import uuid
from datetime import datetime, timezone


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connector_ids = Column(JSON, default=list)
    scan_type = Column(String(32), nullable=False, default="full")
    status = Column(String(32), nullable=False, default="queued")
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    assets_scanned = Column(JSON, default=list)
    errors = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
