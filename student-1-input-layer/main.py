"""
Student 1: Input Layer - Raw Visibility & Event Ingestion
Primary responsibility: Capture raw security events and asset data
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database
from src.database import init_db, SessionLocal
from src.models import Asset, Event

# Import routers
from src.event_collector import router as events_router
from src.discovery import router as discovery_router
from src.sbom_generator import router as sbom_router
from src.drift_detection import router as drift_router

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Student 1: Input Layer starting...")
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    logger.info("Initializing event collector, discovery engine, SBOM generator, and drift detection...")
    yield
    # Shutdown
    logger.info("🛑 Student 1: Input Layer shutting down...")

# Create app
app = FastAPI(
    title="Sentinel - Student 1: Input Layer",
    description="Raw visibility & event ingestion service",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(discovery_router.router, prefix="/api/v1/discovery", tags=["Discovery"])
app.include_router(sbom_router.router, prefix="/api/v1/sbom", tags=["SBOM"])
app.include_router(drift_router.router, prefix="/api/v1/drift", tags=["Drift Detection"])

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Student 1 - Input Layer",
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Project Sentinel - Student 1 (Input Layer)",
        "endpoints": {
            "health": "/health",
            "events": "/api/v1/events",
            "discovery": "/api/v1/discovery",
            "sbom": "/api/v1/sbom",
            "drift": "/api/v1/drift"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
