from typing import List
from datetime import datetime, timezone
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.database import get_db
from app.models import Scan, Connector
from app.middleware.auth import get_current_user, require_admin, require_editor
from app.models import User
from app.workers.scan_tasks import run_scan


router = APIRouter(prefix="/scans", tags=["Scans"])


class ScanCreate(BaseModel):
    connector_ids: List[str]
    scan_type: str = "full"


class ScanResponse(BaseModel):
    id: str
    connector_ids: List[str]
    scan_type: str
    status: str
    assets_scanned: int = 0
    errors: List[dict] = []
    started_at: str = None
    finished_at: str = None
    created_at: str

    class Config:
        from_attributes = True


@router.post("")
def create_scan(
    data: ScanCreate,
    current_user: User = Depends(require_editor()),
):
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        scan = Scan(
            connector_ids=data.connector_ids,
            scan_type=data.scan_type,
            status="queued",
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        
        try:
            from app.services import catalogue_service
            
            results = {
                "assets_discovered": 0,
                "columns_discovered": 0,
                "connectors_processed": 0,
                "errors": []
            }
            
            scan.status = "running"
            scan.started_at = datetime.now(timezone.utc)
            db.commit()
            
            for connector_id in data.connector_ids:
                try:
                    result = catalogue_service.run_discovery(connector_id)
                    if "error" in result:
                        results["errors"].append({
                            "connector_id": connector_id,
                            "error": result["error"]
                        })
                    else:
                        results["assets_discovered"] += result.get("assets_discovered", 0)
                        results["columns_discovered"] += result.get("columns_discovered", 0)
                        results["connectors_processed"] += 1
                except Exception as e:
                    results["errors"].append({
                        "connector_id": connector_id,
                        "error": str(e)
                    })
            
            scan.status = "completed"
            scan.finished_at = datetime.now(timezone.utc)
            scan.assets_scanned = results.get("assets_discovered", 0)
            scan.errors = results.get("errors", [])
            db.commit()
            
            return {
                "data": {
                    "scan_id": scan.id,
                    "status": scan.status,
                    "results": results
                }
            }
        except Exception as e:
            scan.status = "failed"
            scan.errors = [{"error": str(e)}]
            scan.finished_at = datetime.now(timezone.utc)
            db.commit()
            return {
                "data": {
                    "scan_id": scan.id,
                    "status": "failed",
                    "error": str(e)
                }
            }
    finally:
        db.close()


@router.get("/{scan_id}")
def get_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user()),
):
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return {
            "data": {
                "id": scan.id,
                "connector_ids": scan.connector_ids,
                "scan_type": scan.scan_type,
                "status": scan.status,
                "assets_scanned": scan.assets_scanned or 0,
                "errors": scan.errors or [],
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
                "created_at": scan.created_at.isoformat(),
            }
        }
    finally:
        db.close()


@router.get("/{scan_id}/stream")
def scan_stream(
    scan_id: str,
    current_user: User = Depends(get_current_user()),
):
    from app.database import SessionLocal
    
    async def event_generator():
        import asyncio
        db = SessionLocal()
        
        try:
            while True:
                scan = db.query(Scan).filter(Scan.id == scan_id).first()
                if not scan:
                    yield f"data: {json.dumps({'error': 'Scan not found'})}\n\n"
                    break
                
                data = {
                    "status": scan.status,
                    "assets_scanned": scan.assets_scanned or 0,
                    "errors": scan.errors or [],
                }
                
                if scan.started_at:
                    data["started_at"] = scan.started_at.isoformat()
                if scan.finished_at:
                    data["finished_at"] = scan.finished_at.isoformat()
                
                yield f"data: {json.dumps(data)}\n\n"
                
                if scan.status in ["completed", "failed"]:
                    break
                
                await asyncio.sleep(2)
        finally:
            db.close()
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")