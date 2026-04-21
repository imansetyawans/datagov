import time
from typing import Iterator, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from app.connectors.base import BaseConnector, AssetMetadata, ColumnMetadata, ConnectionStatus


class PostgreSQLConnector(BaseConnector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 5432)
        self.database = config.get("database")
        self.user = config.get("user")
        self.password = config.get("password")
    
    def _get_connection_string(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
    
    def connect(self) -> None:
        self._connection = psycopg2.connect(self._get_connection_string())
    
    def test_connection(self) -> ConnectionStatus:
        start = time.time()
        try:
            conn = psycopg2.connect(self._get_connection_string())
            conn.close()
            latency_ms = (time.time() - start) * 1000
            return ConnectionStatus(success=True, latency_ms=latency_ms)
        except Exception as e:
            return ConnectionStatus(success=False, error=str(e))
    
    def list_assets(self, since: Optional[datetime] = None) -> Iterator[AssetMetadata]:
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT table_name, table_type, table_schema
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
        """
        cursor.execute(query)
        
        for row in cursor.fetchall():
            table_name = row["table_name"]
            schema = row["table_schema"]
            
            count_query = f'SELECT COUNT(*) FROM "{schema}"."{table_name}"'
            cursor.execute(count_query)
            row_count = cursor.fetchone()["count"]
            
            yield AssetMetadata(
                external_id=f"{schema}.{table_name}",
                name=table_name,
                asset_type="table" if row["table_type"] == "BASE TABLE" else "view",
                schema_name=schema,
                row_count=row_count
            )
    
    def get_schema(self, asset_external_id: str) -> list[ColumnMetadata]:
        if not self._connection:
            self.connect()
        
        schema, table_name = asset_external_id.split(".")
        
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT column_name, data_type, is_nullable, ordinal_position
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        cursor.execute(query, (schema, table_name))
        
        columns = []
        for i, row in enumerate(cursor.fetchall()):
            columns.append(ColumnMetadata(
                column_name=row["column_name"],
                data_type=row["data_type"],
                is_nullable=row["is_nullable"] == "YES",
                ordinal_position=i + 1
            ))
        
        return columns
    
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None