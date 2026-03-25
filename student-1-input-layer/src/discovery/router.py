"""Discovery Module - Asset management and network scanning"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from uuid import UUID
import logging

from ..database import get_db
from ..models import Asset
from ..schemas import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "module": "discovery", "timestamp": datetime.utcnow().isoformat()}


@router.post("/assets", response_model=AssetResponse, status_code=201)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """
    Create a new asset in inventory
    
    **Example:**
    ```json
    {
      "name": "web-server-01",
      "ip_address": "192.168.1.100",
      "hostname": "web-server-01.local",
      "os_type": "Ubuntu Linux 22.04",
      "asset_type": "server",
      "asset_criticality": 8,
      "owner_team": "Platform Team"
    }
    ```
    """
    try:
        db_asset = Asset(
            name=asset.name,
            ip_address=asset.ip_address,
            hostname=asset.hostname,
            os_type=asset.os_type,
            asset_type=asset.asset_type,
            asset_criticality=asset.asset_criticality,
            owner_team=asset.owner_team
        )
        
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        
        logger.info(f"✅ Asset created: {db_asset.id} ({db_asset.name})")
        return db_asset
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to create asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    asset_type: str = Query(None, description="Filter by asset type"),
    criticality_min: int = Query(None, ge=1, le=10),
    criticality_max: int = Query(None, ge=1, le=10),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all discovered assets with optional filtering
    
    Returns paginated results, newest first
    """
    try:
        query = db.query(Asset)
        
        # Apply filters
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        if criticality_min:
            query = query.filter(Asset.asset_criticality >= criticality_min)
        if criticality_max:
            query = query.filter(Asset.asset_criticality <= criticality_max)
        
        # Count total
        total = query.count()
        
        # Order by created_at desc and paginate
        assets = query.order_by(desc(Asset.created_at)).offset(offset).limit(limit).all()
        
        return AssetListResponse(total=total, assets=assets)
        
    except Exception as e:
        logger.error(f"❌ Failed to list assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    """Get details of a specific asset"""
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: UUID, asset_update: AssetUpdate, db: Session = Depends(get_db)):
    """Update an existing asset"""
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        # Update fields that are provided
        update_data = asset_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(asset, key, value)
        
        asset.updated_at = datetime.utcnow()
        
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        logger.info(f"✅ Asset updated: {asset.id}")
        return asset
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to update asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset(asset_id: UUID, db: Session = Depends(get_db)):
    """Delete an asset"""
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        db.delete(asset)
        db.commit()
        
        logger.info(f"✅ Asset deleted: {asset_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to delete asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan")
async def start_scan(network: str):
    """
    Start a hybrid network discovery scan
    
    Active: Nmap scan | Passive: PCAP sniffing
    
    **Note:** This is currently a stub. Real implementation requires Nmap integration.
    """
    return {"status": "scan_started", "network": network, "scan_id": "scan_123"}


@router.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan results"""
    return {"scan_id": scan_id, "status": "in_progress", "assets": []}

