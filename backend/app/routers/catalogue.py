from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.database import get_db
from app.models import Asset, AssetColumn
from app.services import catalogue_service
from app.middleware.auth import get_current_user, require_admin, require_editor
from app.models import User


router = APIRouter(prefix="/assets", tags=["Catalogue"])


class AssetResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    description: Optional[str] = None
    dq_score: Optional[float] = None
    row_count: Optional[int] = None
    last_scanned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    data: List[AssetResponse]
    meta: dict


@router.get("", response_model=AssetListResponse)
def list_assets(
    q: Optional[str] = Query(None, description="Search query"),
    type: Optional[str] = Query(None, alias="type"),
    source: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    dq_min: Optional[float] = Query(None),
    dq_max: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user()),
):
    filters = {}
    if type:
        filters["type"] = type
    if source:
        filters["connector_id"] = source
    if dq_min is not None:
        filters["dq_min"] = dq_min
    if dq_max is not None:
        filters["dq_max"] = dq_max
    
    if q:
        assets = catalogue_service.search_assets(q, limit)
        return AssetListResponse(
            data=[AssetResponse.model_validate(a) for a in assets],
            meta={"page": 1, "limit": limit, "total": len(assets)}
        )
    
    result = catalogue_service.get_assets(filters, page, limit)
    return AssetListResponse(
        data=[AssetResponse.model_validate(a) for a in result["data"]],
        meta=result["meta"]
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user()),
):
    asset = catalogue_service.get_asset_detail(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}/columns")
def get_asset_columns(
    asset_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1),
    current_user: User = Depends(get_current_user()),
):
    asset = catalogue_service.get_asset_detail(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    columns = asset.columns
    return {
        "data": [
            {
                "id": c.id,
                "column_name": c.column_name,
                "data_type": c.data_type,
                "is_nullable": c.is_nullable,
                "ordinal_position": c.ordinal_position,
                "dq_completeness": c.dq_completeness,
                "dq_uniqueness": c.dq_uniqueness,
                "dq_consistency": c.dq_consistency,
                "dq_accuracy": c.dq_accuracy,
            }
            for c in columns
        ],
        "meta": {"page": page, "limit": limit, "total": len(columns)}
    }


@router.patch("/{asset_id}")
def update_asset(
    asset_id: str,
    description: Optional[str] = None,
    owner_id: Optional[str] = None,
    tags: Optional[list] = None,
    current_user: User = Depends(require_editor()),
):
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if description is not None:
            asset.description = description
        if owner_id is not None:
            asset.owner_id = owner_id
        if tags is not None:
            asset.tags = tags
        
        db.commit()
        db.refresh(asset)
        return {"data": AssetResponse.model_validate(asset)}
    finally:
        db.close()


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user()),
):
    assets = catalogue_service.search_assets(q, limit)
    return {
        "data": [
            {
                "id": a.id,
                "name": a.name,
                "asset_type": a.asset_type,
                "dq_score": a.dq_score,
            }
            for a in assets
        ],
        "meta": {"limit": limit, "total": len(assets)}
    }