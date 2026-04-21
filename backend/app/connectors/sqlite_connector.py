import sqlite3
import time
from typing import Iterator, Optional
from datetime import datetime

from app.connectors.base import BaseConnector, AssetMetadata, ColumnMetadata, ConnectionStatus


class SQLiteConnector(BaseConnector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.db_path = config.get("db_path") or config.get("path") or ":memory:"
    
    def connect(self) -> None:
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
    
    def test_connection(self) -> ConnectionStatus:
        start = time.time()
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT 1")
            conn.close()
            latency_ms = (time.time() - start) * 1000
            return ConnectionStatus(success=True, latency_ms=latency_ms)
        except Exception as e:
            return ConnectionStatus(success=False, error=str(e))
    
    def list_assets(self, since: Optional[datetime] = None) -> Iterator[AssetMetadata]:
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT name, type 
            FROM sqlite_master 
            WHERE type IN ('table', 'view') 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        for row in cursor.fetchall():
            table_name = row[0]
            asset_type = row[1]
            
            count_cursor = self._connection.cursor()
            count_cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
            row_count = count_cursor.fetchone()[0]
            
            yield AssetMetadata(
                external_id=f"{self.db_path}.{table_name}",
                name=table_name,
                asset_type=asset_type,
                schema_name="main",
                row_count=row_count
            )
    
    def get_schema(self, asset_external_id: str) -> list[ColumnMetadata]:
        if not self._connection:
            self.connect()
        
        table_name = asset_external_id.split(".")[-1]
        
        cursor = self._connection.cursor()
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        
        columns = []
        for i, row in enumerate(cursor.fetchall()):
            columns.append(ColumnMetadata(
                column_name=row[1],
                data_type=row[2],
                is_nullable=not bool(row[3]),
                ordinal_position=i + 1
            ))
        
        return columns
    
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None