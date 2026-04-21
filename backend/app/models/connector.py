from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base
import uuid
from datetime import datetime, timezone


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(256), nullable=False)
    connector_type = Column(String(64), nullable=False)
    config_encrypted = Column(JSON, nullable=True)
    status = Column(String(32), default="disconnected")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_tested_at = Column(DateTime(timezone=True), nullable=True)