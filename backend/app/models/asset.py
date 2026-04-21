from sqlalchemy import Column, String, Text, Float, BigInteger, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime, timezone


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connector_id = Column(String(36), nullable=True)
    external_id = Column(String(512), nullable=False, index=True)
    asset_type = Column(String(32), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), nullable=True)
    dq_score = Column(Float, nullable=True)
    schema_hash = Column(String(64), nullable=True)
    row_count = Column(BigInteger, nullable=True)
    tags = Column(JSON, default=list)
    classifications = Column(JSON, default=list)
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    columns = relationship("AssetColumn", back_populates="asset", cascade="all, delete-orphan")