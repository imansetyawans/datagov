from sqlalchemy import Column, String, Text, DateTime, JSON
from app.database import Base
import uuid
from datetime import datetime, timezone


class GlossaryTerm(Base):
    __tablename__ = "glossary_terms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    term = Column(String(256), nullable=False, index=True)
    definition = Column(Text, nullable=True)
    synonyms = Column(JSON, default=list)
    status = Column(String(16), default="draft")
    steward_id = Column(String(36), nullable=True)
    linked_assets = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )