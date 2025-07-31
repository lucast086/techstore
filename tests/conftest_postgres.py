"""Test configuration for TechStore SaaS using PostgreSQL."""

import os

import pytest
from app.database import Base, get_db
from app.main import app

# Import all models to ensure they're registered
from app.models import *  # noqa: F401, F403
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Set test environment variables
os.environ["LOGIN_RATE_LIMIT_PER_MINUTE"] = "0"  # Disable rate limiting for tests
os.environ["LOGIN_RATE_LIMIT_PER_HOUR"] = "0"

# Use PostgreSQL for testing (same as production)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_techstore"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for tests
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    # Drop and recreate all tables for the test session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session override."""

    # Create a factory that returns the same session
    def get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = get_test_db

    # Clear login attempts to avoid rate limiting in tests
    from app.api.v1.auth import login_attempts

    login_attempts.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user for tests that need authentication."""
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        password_hash=get_password_hash("test_password"),
        full_name="Test User",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
