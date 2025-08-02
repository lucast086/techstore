"""Test configuration for TechStore SaaS."""

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

# Set test environment variables
os.environ["LOGIN_RATE_LIMIT_PER_MINUTE"] = "0"  # Disable rate limiting for tests
os.environ["LOGIN_RATE_LIMIT_PER_HOUR"] = "0"

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create test database session."""
    # Clear all tables before each test
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)

    # Create a new session for the test
    session = TestingSessionLocal()

    yield session

    session.close()
    # Clear all data after test
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)


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


@pytest.fixture
def test_customer(db_session):
    """Create a test customer."""
    from app.models.customer import Customer

    customer = Customer(
        name="Test Customer",
        email="customer@example.com",
        phone="1234567890",
        address="123 Test St",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_repair(db_session, test_customer):
    """Create a test repair."""
    from app.models.repair import Repair

    repair = Repair(
        repair_number="REP-2024-00001",
        customer_id=test_customer.id,
        device_type="Phone",
        device_brand="Samsung",
        device_model="Galaxy S21",
        problem_description="Screen broken",
        status="delivered",
        received_by=1,
        delivered_by=1,
        warranty_days=30,
    )
    db_session.add(repair)
    db_session.commit()
    db_session.refresh(repair)
    return repair


@pytest.fixture
def test_warranty(db_session, test_repair):
    """Create a test warranty."""
    from datetime import date, timedelta

    from app.models.warranty import CoverageType, Warranty, WarrantyStatus

    warranty = Warranty(
        repair_id=test_repair.id,
        warranty_number="WRN-2024-00001",
        coverage_type=CoverageType.FULL,
        parts_warranty_days=90,
        labor_warranty_days=30,
        start_date=date.today(),
        parts_expiry_date=date.today() + timedelta(days=90),
        labor_expiry_date=date.today() + timedelta(days=30),
        status=WarrantyStatus.ACTIVE,
    )
    db_session.add(warranty)
    db_session.commit()
    db_session.refresh(warranty)
    return warranty
