"""FastAPI dependency injection for TechStore SaaS."""

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.search_service import SearchService


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_search_service() -> SearchService:
    """Dependency to get search service instance."""
    return SearchService


# Common database dependency
DatabaseDep = Depends(get_db)

# Search service dependency
SearchServiceDep = Depends(get_search_service)
