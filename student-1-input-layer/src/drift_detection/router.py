"""Drift Detection Module - Golden image comparison"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
import logging

from ..database import get_db
from ..models import Asset, GoldenBaseline
from ..schemas import GoldenBaselineCreate, GoldenBaselineResponse, DriftCheckRequest, DriftCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "module": "drift-detection", "timestamp": datetime.utcnow().isoformat()}

@router.post("/baseline/{asset_id}", response_model=GoldenBaselineResponse)
async def create_baseline(asset_id: UUID, baseline: GoldenBaselineCreate, db: Session = Depends(get_db)):
    """
    Create a golden image baseline for an asset
    
    This becomes the known-good state for comparison
    """
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        existing = db.query(GoldenBaseline).filter(GoldenBaseline.asset_id == asset_id).first()
        if existing:
            existing.file_hash = baseline.file_hash
            existing.config_hash = baseline.config_hash
            existing.created_by = baseline.created_by
            existing.updated_at = datetime.utcnow()
            db.add(existing)
        else:
            db_baseline = GoldenBaseline(
                asset_id=asset_id,
                file_hash=baseline.file_hash,
                config_hash=baseline.config_hash,
                created_by=baseline.created_by
            )
            db.add(db_baseline)
        
        db.commit()
        result = db.query(GoldenBaseline).filter(GoldenBaseline.asset_id == asset_id).first()
        logger.info(f"✅ Baseline created/updated: {asset_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to create baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/{asset_id}", response_model=DriftCheckResponse)
async def check_drift(asset_id: UUID, drift_check: DriftCheckRequest, db: Session = Depends(get_db)):
    """Check current state against golden baseline - Returns detected configuration drift"""
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        baseline = db.query(GoldenBaseline).filter(GoldenBaseline.asset_id == asset_id).first()
        if not baseline:
            raise HTTPException(status_code=404, detail=f"No baseline found for asset {asset_id}")
        
        file_match = baseline.file_hash == drift_check.current_file_hash if drift_check.current_file_hash else None
        config_match = baseline.config_hash == drift_check.current_config_hash if drift_check.current_config_hash else None
        drift_detected = (file_match is False or config_match is False)
        
        return DriftCheckResponse(
            asset_id=asset_id,
            drift_detected=drift_detected,
            file_hash_match=file_match,
            config_hash_match=config_match,
            baseline_time=baseline.baseline_time,
            check_time=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to check drift: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/baseline/{asset_id}", response_model=GoldenBaselineResponse)
async def get_baseline(asset_id: UUID, db: Session = Depends(get_db)):
    """Get existing baseline for an asset"""
    try:
        baseline = db.query(GoldenBaseline).filter(GoldenBaseline.asset_id == asset_id).first()
        if not baseline:
            raise HTTPException(status_code=404, detail=f"No baseline found for asset {asset_id}")
        return baseline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{asset_id}")
async def get_drift_report(asset_id: UUID, db: Session = Depends(get_db)):
    """Get detailed drift report"""
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        baseline = db.query(GoldenBaseline).filter(GoldenBaseline.asset_id == asset_id).first()
        
        return {
            "asset_id": str(asset_id),
            "asset_name": asset.name,
            "baseline_exists": baseline is not None,
            "baseline_time": baseline.baseline_time if baseline else None,
            "status": "drift_detection_ready" if baseline else "no_baseline",
            "report_generated": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate drift report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
