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


@router.get("/setup/check-admin")
def check_admin_user(db: Session = Depends(get_db)):
    """Check admin user details - DELETE AFTER USE."""
    admin_email = "admin@techstore.com"

    # Get admin user
    user = db.execute(
        select(User).where(User.email == admin_email)
    ).scalar_one_or_none()

    if not user:
        return {"status": "not_found", "message": "Admin user not found"}

    return {
        "status": "found",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "password_hash": user.password_hash[:20] + "...",
            "created_at": str(user.created_at) if hasattr(user, "created_at") else None,
        },
    }
