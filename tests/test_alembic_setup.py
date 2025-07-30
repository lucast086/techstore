"""
Tests for Alembic migration setup
Following TDD - these tests should fail initially
"""
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from alembic import command
from alembic.config import Config


class TestAlembicConfiguration:
    """Test Alembic migration configuration"""

    def test_alembic_ini_exists(self):
        """Test that alembic.ini file exists"""
        alembic_ini_path = Path("/workspace/alembic.ini")
        assert alembic_ini_path.exists(), "alembic.ini file not found"

    def test_alembic_directory_structure(self):
        """Test that alembic directory structure is correct"""
        alembic_dir = Path("/workspace/alembic")
        assert alembic_dir.exists(), "alembic directory not found"
        assert (alembic_dir / "env.py").exists(), "alembic/env.py not found"
        assert (
            alembic_dir / "versions"
        ).exists(), "alembic/versions directory not found"

    def test_alembic_env_imports_models(self):
        """Test that alembic env.py imports all models"""
        env_path = Path("/workspace/alembic/env.py")
        assert env_path.exists()

        with open(env_path) as f:
            content = f.read()
            # Should import models to ensure they're in metadata
            assert "import app.models" in content
            assert "from app.database import Base" in content

    def test_can_generate_migration(self, tmp_path):
        """Test that we can generate a migration"""
        from app.config import settings

        # Create a test database for migrations
        test_db_url = str(settings.TEST_DATABASE_URL)

        # Configure Alembic
        alembic_cfg = Config("/workspace/alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # Try to create a migration (this will fail if not properly configured)
        try:
            command.revision(alembic_cfg, autogenerate=True, message="test_migration")

            # Check if migration was created
            versions_dir = Path("/workspace/alembic/versions")
            migrations = list(versions_dir.glob("*_test_migration.py"))
            assert len(migrations) > 0, "Migration file was not created"

            # Clean up test migration
            for migration in migrations:
                migration.unlink()

        except Exception as e:
            pytest.fail(f"Failed to generate migration: {e}")

    def test_can_run_migrations(self):
        """Test that migrations can be run"""
        from app.config import settings

        test_db_url = str(settings.TEST_DATABASE_URL)

        # Configure Alembic
        alembic_cfg = Config("/workspace/alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        try:
            # Run migrations
            command.upgrade(alembic_cfg, "head")

            # Verify database has alembic_version table
            engine = create_engine(test_db_url)
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            assert "alembic_version" in tables, "alembic_version table not created"

        except Exception as e:
            pytest.fail(f"Failed to run migrations: {e}")

    def test_can_rollback_migrations(self):
        """Test that migrations can be rolled back"""
        from app.config import settings

        test_db_url = str(settings.TEST_DATABASE_URL)

        # Configure Alembic
        alembic_cfg = Config("/workspace/alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        try:
            # First upgrade
            command.upgrade(alembic_cfg, "head")

            # Then downgrade
            command.downgrade(alembic_cfg, "-1")

            # Should not raise an exception
            assert True

        except Exception as e:
            pytest.fail(f"Failed to rollback migrations: {e}")
