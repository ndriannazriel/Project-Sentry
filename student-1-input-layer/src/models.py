"""
SQLAlchemy ORM Models for Student 1
These map directly to the PostgreSQL schema
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, UUID, Boolean, Float, Text, ForeignKey, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Asset(Base):
    """Asset inventory - devices, servers, workstations"""
    __tablename__ = "assets"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    ip_address = Column(INET, nullable=True, index=True)
    hostname = Column(String(255), nullable=True, index=True)
    os_type = Column(String(100), nullable=True)
    asset_type = Column(String(50), default="generic")
    asset_criticality = Column(Integer, default=5, nullable=False)
    owner_team = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scanned = Column(DateTime, nullable=True)

    # Relationships
    events = relationship("Event", back_populates="asset", cascade="all, delete-orphan")
    sbom_records = relationship("SBOMRecord", back_populates="asset", cascade="all, delete-orphan")
    golden_baseline = relationship("GoldenBaseline", back_populates="asset", uselist=False, cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("asset_criticality >= 1 AND asset_criticality <= 10", name="check_criticality_range"),
    )

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, ip={self.ip_address})>"


class Event(Base):
    """Security events - Auth, Access, Admin, System"""
    __tablename__ = "events"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # Auth, Access, Admin, System
    source_ip = Column(INET, nullable=True)
    user_id = Column(String(255), nullable=True, index=True)
    action = Column(String(255), nullable=False)
    status = Column(String(50), default="success")  # success, failure
    severity = Column(Integer, default=5, nullable=False)  # 1-10
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    raw_data = Column(JSONB, nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="events")

    # Constraints
    __table_args__ = (
        CheckConstraint("event_type IN ('Auth', 'Access', 'Admin', 'System')", name="check_event_type"),
        CheckConstraint("status IN ('success', 'failure')", name="check_event_status"),
        CheckConstraint("severity >= 1 AND severity <= 10", name="check_event_severity"),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, action={self.action})>"


class SBOMRecord(Base):
    """Software Bill of Materials - Components and vulnerabilities"""
    __tablename__ = "sbom_records"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    component_name = Column(String(255), nullable=False)
    version = Column(String(100), nullable=False)
    component_type = Column(String(50), nullable=True)  # library, framework, os_package, etc
    vulnerability_count = Column(Integer, default=0)
    high_criticality_vulns = Column(Integer, default=0)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    asset = relationship("Asset", back_populates="sbom_records")

    def __repr__(self):
        return f"<SBOM(id={self.id}, component={self.component_name}, vulns={self.vulnerability_count})>"


class GoldenBaseline(Base):
    """Golden image baseline - Known-good configurations"""
    __tablename__ = "golden_baseline"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    file_hash = Column(String(512), nullable=True)
    config_hash = Column(String(512), nullable=True)
    baseline_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="golden_baseline")

    def __repr__(self):
        return f"<GoldenBaseline(asset_id={self.asset_id}, created_at={self.baseline_time})>"
