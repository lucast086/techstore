"""FastAPI dependency injection for TechStore SaaS."""

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Common database dependency
DatabaseDep = Depends(get_db)
