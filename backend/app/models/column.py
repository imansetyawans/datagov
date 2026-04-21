from sqlalchemy import Column, String, Text, Float, DateTime, JSON, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime, timezone


class AssetColumn(Base):
    __tablename__ = "asset_columns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    column_name = Column(String(256), nullable=False, index=True)
    data_type = Column(String(64), nullable=False)
    is_nullable = Column(Boolean, default=True)
    ordinal_position = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    classifications = Column(JSON, default=list)
    dq_completeness = Column(Float, nullable=True)
    dq_uniqueness = Column(Float, nullable=True)
    dq_consistency = Column(Float, nullable=True)
    dq_accuracy = Column(Float, nullable=True)
    accuracy_rule = Column(JSON, nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    asset = relationship("Asset", back_populates="columns")