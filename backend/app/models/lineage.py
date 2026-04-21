from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.database import Base
import uuid
from datetime import datetime, timezone


class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    target_asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    edge_type = Column(String(32), nullable=False)
    connector_id = Column(String(36), nullable=True)
    sql_fragment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )