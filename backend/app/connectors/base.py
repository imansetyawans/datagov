from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Optional, Any
from datetime import datetime


@dataclass
class AssetMetadata:
    external_id: str
    name: str
    asset_type: str  # table, view
    schema_name: str
    description: Optional[str] = None
    row_count: Optional[int] = None


@dataclass
class ColumnMetadata:
    column_name: str
    data_type: str
    is_nullable: bool
    ordinal_position: int
    description: Optional[str] = None


@dataclass
class LineageEdge:
    source_external_id: str
    target_external_id: str
    edge_type: str
    sql_fragment: Optional[str] = None


@dataclass
class ConnectionStatus:
    success: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class BaseConnector(ABC):
    def __init__(self, config: dict):
        self.config = config
        self._connection = None

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> ConnectionStatus:
        pass

    @abstractmethod
    def list_assets(self, since: Optional[datetime] = None) -> Iterator[AssetMetadata]:
        pass

    @abstractmethod
    def get_schema(self, asset_external_id: str) -> list[ColumnMetadata]:
        pass

    def get_sample_rows(self, asset_external_id: str, limit: int = 10) -> list[dict]:
        return []

    def extract_lineage(self, since: Optional[datetime] = None) -> Iterator[LineageEdge]:
        return iter([])

    def close(self) -> None:
        if self._connection:
            self._connection = None