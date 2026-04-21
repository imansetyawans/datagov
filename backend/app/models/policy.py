from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey
from app.database import Base
import uuid
from datetime import datetime, timezone


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(256), nullable=False)
    policy_type = Column(String(32), nullable=False)
    rules = Column(JSON, default=list)
    applies_to = Column(String(32), default="column")
    enabled = Column(Boolean, default=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )