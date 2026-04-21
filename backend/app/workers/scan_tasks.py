from datetime import datetime, timezone
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models import Scan, Connector
from app.services import catalogue_service


@celery_app.task(bind=True)
def run_scan(self, scan_id: str):
    db = SessionLocal()
    
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return {"error": "Scan not found"}
        
        scan.status = "running"
        scan.started_at = datetime.now(timezone.utc)
        db.commit()
        
        results = {
            "assets_discovered": 0,
            "columns_discovered": 0,
            "connectors_processed": 0,
            "errors": []
        }
        
        connector_ids = scan.connector_ids or []
        
        for connector_id in connector_ids:
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
        
        return results
    
    except Exception as e:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = "failed"
            scan.finished_at = datetime.now(timezone.utc)
            scan.errors = [{"error": str(e)}]
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()