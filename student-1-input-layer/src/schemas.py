"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# ASSET SCHEMAS
# ============================================================================

class AssetCreate(BaseModel):
    """Create a new asset"""
    name: str = Field(..., min_length=1, max_length=255, description="Asset name")
    ip_address: Optional[str] = Field(None, description="IPv4 or IPv6 address")
    hostname: Optional[str] = Field(None, max_length=255)
    os_type: Optional[str] = Field(None, max_length=100, description="e.g., Ubuntu Linux, Windows 10, macOS")
    asset_type: str = Field("generic", description="e.g., server, workstation, network_device")
    asset_criticality: int = Field(5, ge=1, le=10, description="Criticality score 1-10")
    owner_team: Optional[str] = Field(None, max_length=255)

    class Config:
        schema_extra = {
            "example": {
                "name": "web-server-01",
                "ip_address": "192.168.1.100",
                "hostname": "web-server-01.local",
                "os_type": "Ubuntu Linux 22.04",
                "asset_type": "server",
                "asset_criticality": 8,
                "owner_team": "Platform Team"
            }
        }


class AssetUpdate(BaseModel):
    """Update an asset"""
    name: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    os_type: Optional[str] = None
    asset_type: Optional[str] = None
    asset_criticality: Optional[int] = Field(None, ge=1, le=10)
    owner_team: Optional[str] = None


class AssetResponse(BaseModel):
    """Asset response"""
    id: UUID
    name: str
    ip_address: Optional[str]
    hostname: Optional[str]
    os_type: Optional[str]
    asset_type: str
    asset_criticality: int
    owner_team: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_scanned: Optional[datetime]

    class Config:
        from_attributes = True  # Pydantic v2


class AssetListResponse(BaseModel):
    """List of assets"""
    total: int
    assets: List[AssetResponse]


# ============================================================================
# EVENT SCHEMAS
# ============================================================================

class EventCreate(BaseModel):
    """Create a new event"""
    asset_id: Optional[UUID] = Field(None, description="Asset UUID")
    event_type: str = Field(..., description="Auth, Access, Admin, or System")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    user_id: Optional[str] = Field(None, max_length=255)
    action: str = Field(..., min_length=1, max_length=255)
    status: str = Field("success", description="success or failure")
    severity: Optional[int] = Field(5, ge=1, le=10, description="Event severity 1-10")
    raw_data: Optional[dict] = Field(None, description="Additional event metadata")

    @validator("event_type")
    def validate_event_type(cls, v):
        valid_types = {"Auth", "Access", "Admin", "System"}
        if v not in valid_types:
            raise ValueError(f"event_type must be one of {valid_types}")
        return v

    @validator("status")
    def validate_status(cls, v):
        valid_statuses = {"success", "failure"}
        if v not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "asset_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "Auth",
                "source_ip": "203.0.113.5",
                "user_id": "john.doe",
                "action": "login",
                "status": "success",
                "severity": 5,
                "raw_data": {"mfa": "enabled", "duration_ms": 1234}
            }
        }


class EventResponse(BaseModel):
    """Event response"""
    id: UUID
    asset_id: Optional[UUID]
    event_type: str
    source_ip: Optional[str]
    user_id: Optional[str]
    action: str
    status: str
    severity: int
    created_at: datetime
    raw_data: Optional[dict]

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """List of events"""
    total: int
    events: List[EventResponse]


class EventFilterParams(BaseModel):
    """Query parameters for filtering events"""
    event_type: Optional[str] = None
    asset_id: Optional[UUID] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    severity_min: Optional[int] = Field(None, ge=1, le=10)
    severity_max: Optional[int] = Field(None, ge=1, le=10)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ============================================================================
# SBOM SCHEMAS
# ============================================================================

class SBOMRecordCreate(BaseModel):
    """Create SBOM record"""
    asset_id: UUID
    component_name: str
    version: str
    component_type: Optional[str] = None
    vulnerability_count: int = 0
    high_criticality_vulns: int = 0


class SBOMRecordResponse(BaseModel):
    """SBOM record response"""
    id: UUID
    asset_id: UUID
    component_name: str
    version: str
    component_type: Optional[str]
    vulnerability_count: int
    high_criticality_vulns: int
    generated_at: datetime

    class Config:
        from_attributes = True


class SBOMResponse(BaseModel):
    """Complete SBOM for an asset"""
    asset_id: UUID
    components: List[SBOMRecordResponse]
    total_components: int
    total_vulnerabilities: int
    high_criticality_vulns: int
    generated_at: datetime


# ============================================================================
# GOLDEN BASELINE SCHEMAS
# ============================================================================

class GoldenBaselineCreate(BaseModel):
    """Create golden baseline"""
    asset_id: UUID
    file_hash: Optional[str] = None
    config_hash: Optional[str] = None
    created_by: Optional[str] = None


class GoldenBaselineResponse(BaseModel):
    """Golden baseline response"""
    id: UUID
    asset_id: UUID
    file_hash: Optional[str]
    config_hash: Optional[str]
    baseline_time: datetime
    created_by: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class DriftCheckRequest(BaseModel):
    """Check drift against baseline"""
    asset_id: UUID
    current_file_hash: Optional[str] = None
    current_config_hash: Optional[str] = None


class DriftCheckResponse(BaseModel):
    """Drift check result"""
    asset_id: UUID
    drift_detected: bool
    file_hash_match: Optional[bool] = None
    config_hash_match: Optional[bool] = None
    baseline_time: Optional[datetime]
    check_time: datetime


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    database: str = "unknown"
    timestamp: datetime
