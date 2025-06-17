# Testing Structure

## Overview

This document outlines the testing structure for the TechStore project. We follow a Test-Driven Development (TDD) approach, where tests are written before implementation to guide the development process.

## Directory Structure

The tests are organized in a separate `tests` directory at the root of the backend, mirroring the structure of the actual application:

```
techstore/backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared pytest fixtures
│   ├── tenants/                # Tests for tenants app
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── ...
│   ├── users/                  # Tests for users app
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── ...
│   └── techstore_api/          # Tests for core app
│       ├── __init__.py
│       └── ...
├── tenants/                    # Actual tenants app
├── users/                      # Actual users app
└── techstore_api/              # Actual core app
```

## Test Categories

Our tests are organized into the following categories:

### 1. Unit Tests
- Test individual components in isolation
- Fast execution, high coverage
- Examples: model validation, utility functions, serializers

### 2. Integration Tests
- Test how components work together
- Focus on API interactions and database operations
- Use fixtures to set up test environment

### 3. Tenant-Specific Tests
- Test tenant isolation and schema-specific functionality
- Use `TenantTestCase` for tenant-aware testing

## Running Tests

To run the tests, use the following commands:

```bash
# Run all tests
pytest

# Run tests for a specific app
pytest tests/users/

# Run a specific test file
pytest tests/users/test_models.py

# Run a specific test
pytest tests/users/test_models.py::TestUserModel::test_user_creation
```

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `tenant_test`: Creates a test tenant
- `tenant_client`: Returns a client that sets the tenant context
- `admin_user`: Creates an admin user for testing
- `authenticated_client`: Returns an authenticated client

## Test-Driven Development Workflow

1. Write a failing test for the first step of the feature you want to implement
2. Run the test to verify it fails for the expected reason
3. Implement the minimum code necessary to make the test pass
4. Run the test to verify it passes
5. Refactor the code while ensuring the tests continue to pass

## Continuous Integration

Tests are automatically run on every push to the repository through our CI pipeline, ensuring that all changes are tested before being merged into the main branch. 