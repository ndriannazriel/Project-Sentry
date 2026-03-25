"""Event Collector Module - FastAPI based event ingestion"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from uuid import UUID
import logging

from ..database import get_db
from ..models import Event, Asset
from ..schemas import EventCreate, EventResponse, EventListResponse, EventFilterParams

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "module": "event-collector", "timestamp": datetime.utcnow().isoformat()}


@router.post("/ingest", response_model=EventResponse, status_code=201)
async def ingest_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Ingest a security event
    
    Event types: Auth (logins), Access (file/DB access), Admin (privilege changes), System (process starts)
    
    **Example:**
    ```json
    {
      "asset_id": "550e8400-e29b-41d4-a716-446655440000",
      "event_type": "Auth",
      "source_ip": "203.0.113.5",
      "user_id": "john.doe",
      "action": "login",
      "status": "success",
      "severity": 5
    }
    ```
    """
    try:
        # Verify asset exists if asset_id provided
        if event.asset_id:
            asset = db.query(Asset).filter(Asset.id == event.asset_id).first()
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset {event.asset_id} not found")
        
        # Create event
        db_event = Event(
            asset_id=event.asset_id,
            event_type=event.event_type,
            source_ip=event.source_ip,
            user_id=event.user_id,
            action=event.action,
            status=event.status,
            severity=event.severity,
            raw_data=event.raw_data
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"✅ Event ingested: {db_event.id} ({event.event_type})")
        return db_event
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to ingest event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=EventListResponse)
async def list_events(
    event_type: str = Query(None, description="Filter by event type"),
    asset_id: UUID = Query(None, description="Filter by asset ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    status: str = Query(None, description="Filter by status"),
    severity_min: int = Query(None, ge=1, le=10),
    severity_max: int = Query(None, ge=1, le=10),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all ingested events with optional filtering
    
    Returns paginated results, newest first
    """
    try:
        query = db.query(Event)
        
        # Apply filters
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if asset_id:
            query = query.filter(Event.asset_id == asset_id)
        if user_id:
            query = query.filter(Event.user_id == user_id)
        if status:
            query = query.filter(Event.status == status)
        if severity_min:
            query = query.filter(Event.severity >= severity_min)
        if severity_max:
            query = query.filter(Event.severity <= severity_max)
        
        # Count total
        total = query.count()
        
        # Order by created_at desc and paginate
        events = query.order_by(desc(Event.created_at)).offset(offset).limit(limit).all()
        
        return EventListResponse(total=total, events=events)
        
    except Exception as e:
        logger.error(f"❌ Failed to list events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get details of a specific event"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asset/{asset_id}/events", response_model=EventListResponse)
async def get_asset_events(
    asset_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all events for a specific asset"""
    try:
        # Verify asset exists
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        query = db.query(Event).filter(Event.asset_id == asset_id)
        total = query.count()
        events = query.order_by(desc(Event.created_at)).offset(offset).limit(limit).all()
        
        return EventListResponse(total=total, events=events)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get asset events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

