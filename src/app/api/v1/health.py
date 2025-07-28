"""Health check endpoints for TechStore SaaS."""


from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import check_db_connection, get_db, get_db_version

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "TechStore API", "version": "1.0.0"}


@router.get("/health/db")
async def database_health(db: Session = Depends(get_db)) -> dict:
    """Database connectivity check."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_version = get_db_version()

        return {
            "status": "healthy",
            "database": "connected",
            "postgres_version": db_version,
            "pool_size": settings.DB_POOL_SIZE,
            "database_name": settings.POSTGRES_DB,
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)) -> dict:
    """Readiness check for Kubernetes/Docker."""
    db_connected = check_db_connection()

    if not db_connected:
        return {"status": "not_ready", "checks": {"database": "failed"}}

    return {"status": "ready", "checks": {"database": "passed"}}
