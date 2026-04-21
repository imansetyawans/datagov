import hashlib
from typing import Optional
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Asset, AssetColumn, Connector
from app.connectors.sqlite_connector import SQLiteConnector
from app.connectors.postgres_connector import PostgreSQLConnector
from app.connectors.base import BaseConnector


CONNECTOR_CLASSES = {
    "sqlite": SQLiteConnector,
    "postgres": PostgreSQLConnector,
}


def get_connector(connector: Connector) -> Optional[BaseConnector]:
    config = connector.config_encrypted or {}
    connector_type = connector.connector_type
    
    if connector_type not in CONNECTOR_CLASSES:
        return None
    
    return CONNECTOR_CLASSES[connector_type](config)


def compute_schema_hash(columns: list) -> str:
    column_str = "".join([f"{c.column_name}:{c.data_type}" for c in columns])
    return hashlib.sha256(column_str.encode()).hexdigest()[:64]


def run_discovery(connector_id: str) -> dict:
    db = SessionLocal()
    
    try:
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            return {"error": "Connector not found"}
        
        connector_obj = get_connector(connector)
        if not connector_obj:
            return {"error": f"Unsupported connector type: {connector.connector_type}"}
        
        connector_obj.connect()
        
        assets_discovered = 0
        columns_discovered = 0
        
        for asset_meta in connector_obj.list_assets():
            existing = db.query(Asset).filter(
                Asset.external_id == asset_meta.external_id
            ).first()
            
            columns = list(connector_obj.get_schema(asset_meta.external_id))
            schema_hash = compute_schema_hash(columns)
            
            if existing:
                if existing.schema_hash != schema_hash:
                    existing.schema_hash = schema_hash
                    existing.last_scanned_at = datetime.now(timezone.utc)
                    
                    for col in existing.columns:
                        db.delete(col)
                    
                    for col_meta in columns:
                        new_col = AssetColumn(
                            asset_id=existing.id,
                            column_name=col_meta.column_name,
                            data_type=col_meta.data_type,
                            is_nullable=col_meta.is_nullable,
                            ordinal_position=col_meta.ordinal_position,
                        )
                        db.add(new_col)
                        columns_discovered += 1
            else:
                new_asset = Asset(
                    connector_id=connector_id,
                    external_id=asset_meta.external_id,
                    name=asset_meta.name,
                    asset_type=asset_meta.asset_type,
                    row_count=asset_meta.row_count,
                    schema_hash=schema_hash,
                    last_scanned_at=datetime.now(timezone.utc),
                )
                db.add(new_asset)
                db.flush()
                
                for col_meta in columns:
                    new_col = AssetColumn(
                        asset_id=new_asset.id,
                        column_name=col_meta.column_name,
                        data_type=col_meta.data_type,
                        is_nullable=col_meta.is_nullable,
                        ordinal_position=col_meta.ordinal_position,
                    )
                    db.add(new_col)
                    columns_discovered += 1
                
                assets_discovered += 1
        
        connector_obj.close()
        
        connector.last_tested_at = datetime.now(timezone.utc)
        connector.status = "connected"
        
        db.commit()
        
        return {
            "assets_discovered": assets_discovered,
            "columns_discovered": columns_discovered,
            "connector_status": "connected"
        }
    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def search_assets(query: str, limit: int = 50) -> list:
    db = SessionLocal()
    try:
        q = f"%{query}%"
        assets = db.query(Asset).filter(
            Asset.deleted_at == None,
            (Asset.name.like(q) | Asset.description.like(q))
        ).limit(limit).all()
        return assets
    finally:
        db.close()


def get_assets(filters: dict = None, page: int = 1, limit: int = 50) -> dict:
    db = SessionLocal()
    try:
        query = db.query(Asset).filter(Asset.deleted_at == None)
        
        if filters:
            if filters.get("type"):
                query = query.filter(Asset.asset_type == filters["type"])
            if filters.get("connector_id"):
                query = query.filter(Asset.connector_id == filters["connector_id"])
            if filters.get("dq_min"):
                query = query.filter(Asset.dq_score >= filters["dq_min"])
            if filters.get("dq_max"):
                query = query.filter(Asset.dq_score <= filters["dq_max"])
        
        total = db.query(Asset).filter(Asset.deleted_at == None).count()
        
        assets = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            "data": assets,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total
            }
        }
    finally:
        db.close()


from sqlalchemy.orm import joinedload

def get_asset_detail(asset_id: str) -> Optional[Asset]:
    db = SessionLocal()
    try:
        return db.query(Asset).options(
            joinedload(Asset.columns)
        ).filter(Asset.id == asset_id, Asset.deleted_at == None).first()
    finally:
        db.close()