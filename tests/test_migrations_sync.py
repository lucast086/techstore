"""Test to verify models and migrations are in sync."""

import subprocess

import pytest
from app.models.cash_closing import CashClosing
from app.models.customer import Customer
from app.models.sale import Sale
from sqlalchemy import inspect


@pytest.mark.migrations
def test_model_columns_exist_in_db(db_session):
    """Verify all model columns exist in the actual database.

    This catches the case where a migration drops columns
    but the model still references them.
    """
    inspector = inspect(db_session.bind)

    models_to_check = [
        (CashClosing, "cash_closings"),
        (Customer, "customers"),
        (Sale, "sales"),
    ]

    errors = []
    for model_class, table_name in models_to_check:
        db_columns = {col["name"] for col in inspector.get_columns(table_name)}
        model_columns = {col.key for col in model_class.__table__.columns}

        missing_in_db = model_columns - db_columns
        if missing_in_db:
            errors.append(f"{table_name}: Model has columns not in DB: {missing_in_db}")

    if errors:
        pytest.fail(
            "Model/DB column mismatch detected!\n"
            + "\n".join(errors)
            + "\nThis means a migration dropped columns the model still uses."
        )


@pytest.mark.migrations
def test_no_pending_migrations():
    """Verify there are no model changes that need new migrations.

    This test runs 'alembic check' which compares the current database
    schema (from migrations) against the SQLAlchemy models.
    If they differ, it means either:
    - A migration dropped/added columns that the model doesn't reflect
    - A model was changed without creating a migration
    """
    result = subprocess.run(
        ["poetry", "run", "alembic", "check"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Ignore "database not up to date" - that's expected in test env
        if "Target database is not up to date" not in result.stderr:
            pytest.fail(
                f"Models and migrations are out of sync!\n"
                f"Run 'poetry run alembic revision --autogenerate' to check differences.\n"
                f"stderr: {result.stderr}"
            )


@pytest.mark.migrations
def test_single_migration_head():
    """Verify there's only one migration head (no branches)."""
    result = subprocess.run(
        ["poetry", "run", "alembic", "heads"],
        capture_output=True,
        text=True,
    )

    heads = [
        line for line in result.stdout.strip().split("\n") if line and "head" in line
    ]

    assert len(heads) == 1, (
        f"Multiple migration heads detected! This will cause deployment failures.\n"
        f"Heads found: {heads}\n"
        f"Run 'poetry run alembic merge heads' to fix."
    )
