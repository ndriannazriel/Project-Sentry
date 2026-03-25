"""SBOM Generator Module - Software Bill of Materials generation"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
import logging

from ..database import get_db
from ..models import Asset, SBOMRecord
from ..schemas import SBOMResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "module": "sbom-generator", "timestamp": datetime.utcnow().isoformat()}

@router.post("/generate")
async def generate_sbom(asset_id: UUID, db: Session = Depends(get_db)):
    """
    Generate a Software Bill of Materials (CycloneDX format)
    
    Currently a stub. Real implementation will:
    - Parse package managers (pip, npm, apt, docker)
    - Create components in CycloneDX format
    - Identify vulnerable dependencies via NVD/CVE
    """
    try:
        # Verify asset exists
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        return {
            "status": "generating",
            "asset_id": str(asset_id),
            "asset_name": asset.name,
            "message": "SBOM generation implemented in phase 2",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate SBOM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/asset/{asset_id}", response_model=SBOMResponse)
async def get_asset_sbom(asset_id: UUID, db: Session = Depends(get_db)):
    """Get SBOM for a specific asset"""
    try:
        # Verify asset exists
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        # Get all SBOM records for asset
        records = db.query(SBOMRecord).filter(SBOMRecord.asset_id == asset_id).all()
        
        total_vulns = sum(r.vulnerability_count for r in records)
        high_crit_vulns = sum(r.high_criticality_vulns for r in records)
        
        return SBOMResponse(
            asset_id=asset_id,
            components=records,
            total_components=len(records),
            total_vulnerabilities=total_vulns,
            high_criticality_vulns=high_crit_vulns,
            generated_at=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get SBOM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/asset/{asset_id}/vulnerabilities")
async def get_vulnerabilities(asset_id: UUID, db: Session = Depends(get_db)):
    """Get detected vulnerabilities for an asset"""
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        records = db.query(SBOMRecord).filter(
            SBOMRecord.asset_id == asset_id,
            SBOMRecord.vulnerability_count > 0
        ).all()
        
        return {
            "asset_id": str(asset_id),
            "vulnerable_components": len(records),
            "total_vulnerabilities": sum(r.vulnerability_count for r in records),
            "high_criticality_vulns": sum(r.high_criticality_vulns for r in records),
            "components": [{"name": r.component_name, "version": r.version} for r in records]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get vulnerabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
