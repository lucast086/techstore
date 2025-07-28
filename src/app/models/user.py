"""User model for authentication and authorization."""


from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for storing user authentication data.

    Attributes:
        email: Unique email address for login.
        password_hash: Bcrypt hashed password.
        full_name: User's full name for display.
        role: User role (admin or technician).
        is_active: Whether the user can login.
        last_login: Timestamp of last successful login.
        created_by: ID of user who created this user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, technician
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    creator = relationship("User", remote_side="User.id", backref="created_users")

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.email}>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"

    @property
    def is_technician(self) -> bool:
        """Check if user has technician role."""
        return self.role == "technician"
