"""Template context processors for injecting global data into templates."""

from typing import Optional

from fastapi import Cookie, Request
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.database import get_async_session
from app.models.user import User


async def get_current_user_context(
    request: Request,
    access_token: Optional[str] = Cookie(None)
) -> Optional[User]:
    """Get current user for template context.
    
    This function attempts to get the current user from cookies.
    If the user is not authenticated or token is invalid, returns None.
    
    Args:
        request: FastAPI request object
        access_token: JWT token from cookie
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not access_token:
        return None
        
    try:
        # Create a new database session for this context
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.config import settings
        
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        user = await get_current_user_from_cookie(request, access_token, db)
        return user
    except Exception:
        # If any error occurs (invalid token, user not found, etc.)
        # we return None to indicate no authenticated user
        return None
    finally:
        # Always close the database session
        if 'db' in locals():
            db.close()