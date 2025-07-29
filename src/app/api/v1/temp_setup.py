"""Temporary setup endpoint - DELETE AFTER USE."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.dependencies import get_db
from app.models.user import User

router = APIRouter()


@router.post("/setup/create-admin")
def create_admin_user(db: Session = Depends(get_db)):
    """Create admin user - NO AUTH REQUIRED - DELETE AFTER USE."""
    admin_email = "admin@techstore.com"
    admin_password = "Admin123!"

    # Check if admin exists
    existing = db.execute(
        select(User).where(User.email == admin_email)
    ).scalar_one_or_none()

    if existing:
        return {
            "status": "exists",
            "message": f"Admin user already exists: {admin_email}",
        }

    # Create admin user
    admin = User(
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        full_name="System Administrator",
        role="admin",
        is_active=True,
    )

    db.add(admin)
    db.commit()

    return {
        "status": "created",
        "message": "Admin user created successfully",
        "credentials": {"email": admin_email, "password": admin_password},
        "warning": "DELETE THIS ENDPOINT AFTER USE!",
    }
