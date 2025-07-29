"""
Tests for database setup and configuration
Following TDD - these tests should fail initially
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestDatabaseConfiguration:
    """Test database configuration and connection"""

    def test_config_loads_from_env(self):
        """Test that configuration loads from environment variables"""
        from app.config import settings

        # Should load from .env or environment
        assert settings.DATABASE_URL is not None
        assert "postgresql://" in settings.DATABASE_URL

    def test_database_url_construction(self):
        """Test that database URL is properly constructed"""
        from app.config import settings

        expected_url = "postgresql://postgres:postgres@db:5432/techstore_db"
        assert str(settings.DATABASE_URL) == expected_url

    def test_database_url_format(self):
        """Test that database URL has proper format"""
        from app.config import settings

        # Should be a valid PostgreSQL URL
        assert settings.DATABASE_URL.startswith("postgresql://")
        assert "@" in settings.DATABASE_URL  # has host
        assert "/" in settings.DATABASE_URL.split("@")[1]  # has database name


class TestDatabaseConnection:
    """Test database connection functionality"""

    def test_database_connection(self):
        """Test that we can connect to the database"""
        from app.database import engine

        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_session_creation(self):
        """Test that we can create a database session"""
        from app.database import SessionLocal

        session = SessionLocal()
        assert isinstance(session, Session)

        # Test query execution
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1

        session.close()

    def test_get_db_dependency(self):
        """Test the get_db dependency function"""
        from app.database import get_db

        # Should yield a session
        db_gen = get_db()
        db = next(db_gen)

        assert isinstance(db, Session)

        # Cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass

    def test_database_health_check(self):
        """Test database health check function"""
        from app.database import check_db_connection

        # Should return True when database is accessible
        assert check_db_connection() is True

    def test_connection_pool_configuration(self):
        """Test that connection pool is properly configured"""
        from app.database import engine

        # Just verify engine has a pool configured
        assert hasattr(engine, "pool")
        assert engine.pool is not None


class TestBaseModel:
    """Test base model functionality"""

    def test_base_model_has_common_fields(self):
        """Test that BaseModel has id, created_at, updated_at, is_active"""
        from app.models import BaseModel
        from sqlalchemy import inspect

        # Create a test model
        class TestModel(BaseModel):
            __tablename__ = "test_model"

        # Inspect columns
        mapper = inspect(TestModel)
        column_names = [c.key for c in mapper.columns]

        assert "id" in column_names
        assert "created_at" in column_names
        assert "updated_at" in column_names
        assert "is_active" in column_names

    def test_base_model_timestamps(self):
        """Test that timestamps are automatically set"""
        from datetime import datetime

        from app.database import Base, engine
        from app.models import BaseModel
        from sqlalchemy.orm import Session

        class TestTimestampModel(BaseModel):
            __tablename__ = "test_timestamp_model"

        # Create the table for this test
        Base.metadata.create_all(bind=engine, tables=[TestTimestampModel.__table__])

        try:
            # Test timestamp handling
            with Session(engine) as session:
                test_obj = TestTimestampModel()
                session.add(test_obj)
                session.commit()
                session.refresh(test_obj)

                assert test_obj.created_at is not None
                assert test_obj.updated_at is not None
                assert isinstance(test_obj.created_at, datetime)
                assert isinstance(test_obj.updated_at, datetime)
                assert test_obj.is_active is True
                assert test_obj.id is not None
        finally:
            # Clean up the test table
            TestTimestampModel.__table__.drop(bind=engine, checkfirst=True)
