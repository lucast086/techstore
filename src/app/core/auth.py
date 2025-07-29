"""Authentication logic and user management."""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate


class AuthService:
    """Service for authentication operations.

    This service handles user authentication, token generation,
    and user management operations.
    """

    def __init__(self, db: Session):
        """Initialize auth service with database session.

        Args:
            db: Database session.
        """
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.

        Args:
            email: User's email address.
            password: User's plain text password.

        Returns:
            User object if authentication succeeds, None otherwise.
        """
        print(f"[AUTH DEBUG] Attempting login for email: {email}")

        # Get user by email
        result = self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"[AUTH DEBUG] User not found: {email}")
            return None

        print(f"[AUTH DEBUG] User found: {user.email}, active: {user.is_active}")

        # Check if user is active
        if not user.is_active:
            print("[AUTH DEBUG] User is not active")
            return None

        # Verify password
        print("[AUTH DEBUG] Verifying password...")
        password_valid = verify_password(password, user.password_hash)
        print(f"[AUTH DEBUG] Password valid: {password_valid}")

        if not password_valid:
            print(f"[AUTH DEBUG] Password hash in DB: {user.password_hash[:20]}...")
            return None

        # Update last login
        user.last_login = datetime.now(UTC)
        self.db.commit()

        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for a user.

        Args:
            user: The authenticated user.

        Returns:
            TokenResponse with access and refresh tokens.
        """
        # Token payload
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}

        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=8 * 3600,  # 8 hours in seconds
        )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's ID.

        Returns:
            User object if found, None otherwise.
        """
        result = self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: The user's email address.

        Returns:
            User object if found, None otherwise.
        """
        result = self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def create_user(
        self, user_data: UserCreate, created_by: Optional[int] = None
    ) -> User:
        """Create a new user.

        Args:
            user_data: User creation data.
            created_by: ID of the user creating this user.

        Returns:
            The created user.

        Raises:
            ValueError: If user with email already exists.
        """
        # Check if user exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        password_hash = get_password_hash(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
            role=user_data.role,
            created_by=created_by,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:
        """Change a user's password.

        Args:
            user: The user whose password to change.
            current_password: The user's current password.
            new_password: The new password.

        Returns:
            True if password was changed, False if current password is wrong.
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return False

        # Update password
        user.password_hash = get_password_hash(new_password)
        self.db.commit()

        return True

    def deactivate_user(self, user: User) -> None:
        """Deactivate a user account.

        Args:
            user: The user to deactivate.
        """
        user.is_active = False
        self.db.commit()

    def activate_user(self, user: User) -> None:
        """Activate a user account.

        Args:
            user: The user to activate.
        """
        user.is_active = True
        self.db.commit()
