from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Connector
from app.middleware.auth import get_current_user, require_admin
from app.models import User
from app.services import catalogue_service
from app.connectors.sqlite_connector import SQLiteConnector
from app.connectors.postgres_connector import PostgreSQLConnector


router = APIRouter(prefix="/connectors", tags=["Connectors"])


class ConnectorCreate(BaseModel):
    name: str
    connector_type: str
    config: dict


class ConnectorResponse(BaseModel):
    id: str
    name: str
    connector_type: str
    status: str
    last_tested_at: str = None

    class Config:
        from_attributes = True


CONNECTOR_TYPES = {
    "sqlite": SQLiteConnector,
    "postgres": PostgreSQLConnector,
}


@router.get("")
def list_connectors(current_user: User = Depends(require_admin())):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        connectors = db.query(Connector).all()
        return {
            "data": [
                {
                    "id": c.id,
                    "name": c.name,
                    "connector_type": c.connector_type,
                    "status": c.status,
                    "last_tested_at": c.last_tested_at.isoformat() if c.last_tested_at else None,
                }
                for c in connectors
            ]
        }
    finally:
        db.close()


@router.post("")
def create_connector(
    data: ConnectorCreate,
    current_user: User = Depends(require_admin()),
):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        connector = Connector(
            name=data.name,
            connector_type=data.connector_type,
            config_encrypted=data.config,
            status="disconnected",
        )
        db.add(connector)
        db.commit()
        db.refresh(connector)
        
        return {"data": {"id": connector.id, "name": connector.name}}
    finally:
        db.close()


@router.post("/{connector_id}/test")
def test_connector(
    connector_id: str,
    current_user: User = Depends(require_admin()),
):
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")
        
        connector_class = CONNECTOR_TYPES.get(connector.connector_type)
        if not connector_class:
            raise HTTPException(status_code=400, detail="Unsupported connector type")
        
        config = connector.config_encrypted or {}
        conn = connector_class(config)
        result = conn.test_connection()
        
        connector.last_tested_at = datetime.now(timezone.utc)
        connector.status = "connected" if result.success else "failed"
        
        db.commit()
        
        return {
            "success": result.success,
            "latency_ms": result.latency_ms,
            "error": result.error
        }
    finally:
        db.close()


@router.delete("/{connector_id}")
def delete_connector(
    connector_id: str,
    current_user: User = Depends(require_admin()),
):
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")
        
        db.delete(connector)
        db.commit()
        
        return {"data": {"deleted": True}}
    finally:
        db.close()