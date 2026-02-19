# Testing Guide

## Overview

This project uses a comprehensive testing infrastructure with unit tests, Docker-based testing, pre-commit hooks, and CI/CD automation via GitHub Actions.

## Quick Start

### Run Tests Locally

```bash
# Option 1: Use the provided script
./run-tests.sh

# Option 2: Run pytest directly
PYTHONPATH=./dags pytest tests/ -v

# Option 3: Run with coverage
PYTHONPATH=./dags pytest tests/ --cov=dags --cov-report=html
```

### Run Tests in Docker

```bash
# Option 1: Use the provided script
./run-tests-docker.sh

# Option 2: Run docker compose directly
docker compose --profile test up --build test

# View test logs
docker compose --profile test logs test
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── fixtures/
│   ├── __init__.py
│   └── common_fixtures.py   # Reusable test fixtures
├── unit/
│   ├── __init__.py
│   ├── test_moodle_api_client.py    # API client tests (35 tests)
│   ├── test_configuration.py         # Configuration tests (14 tests)
│   └── test_utility_functions.py     # Utility function tests (13 tests)
└── integration/             # Integration tests (future)
    └── __init__.py
```

## Test Categories

### Unit Tests (58 tests implemented)

Based on `docs/TEST_SCENARIOS.md`:

1. **MoodleAPIClient Tests** (35 tests)
   - Client initialization (6 tests)
   - URL validation (4 tests)
   - HTTPS enforcement (4 tests)
   - URL format tests (6 tests)
   - API call operations (6 tests)
   - Specific API methods (5 tests)

2. **Configuration Management Tests** (14 tests)
   - Comma-separated config parsing (8 tests)
   - Instance configuration retrieval (3 tests)
   - DAG configuration loading (3 tests)

3. **Utility Function Tests** (13 tests)
   - Hash computation (3 tests)
   - Record preparation (2 tests)
   - Schema validation (8 tests)

## Running Specific Tests

### By File

```bash
PYTHONPATH=./dags pytest tests/unit/test_moodle_api_client.py -v
```

### By Class

```bash
PYTHONPATH=./dags pytest tests/unit/test_moodle_api_client.py::TestMoodleAPIClientInitialization -v
```

### By Test Name

```bash
PYTHONPATH=./dags pytest tests/unit/test_moodle_api_client.py::TestMoodleAPIClientInitialization::test_1_1_1_initialize_with_valid_https_url -v
```

### By Marker

```bash
# Run only unit tests
PYTHONPATH=./dags pytest -m unit -v

# Run only integration tests
PYTHONPATH=./dags pytest -m integration -v

# Skip slow tests
PYTHONPATH=./dags pytest -m "not slow" -v
```

## Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit.

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

### What Gets Checked

1. **Code Formatting**
   - Black (Python code formatter)
   - isort (Import sorting)

2. **Linting**
   - Flake8 (Style guide enforcement)
   - Pylint (Code quality)

3. **Type Checking**
   - mypy (Static type checking)

4. **Security**
   - Bandit (Security issue detection)

5. **Testing**
   - pytest (Fast unit tests on staged files)

6. **General**
   - Trailing whitespace
   - End of file fixer
   - YAML validation
   - Large file check
   - Private key detection

### Manual Execution

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run pytest-check

# Skip hooks for a commit (not recommended)
git commit --no-verify
```

### Auto-fix Issues

```bash
# Auto-format code
black dags/ tests/
isort dags/ tests/

# Check what would change
black --check --diff dags/ tests/
```

## GitHub Actions CI/CD

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual workflow dispatch

### Workflow Jobs

1. **Lint and Format** (`lint-and-format`)
   - Runs Black, isort, Flake8
   - Security check with Bandit
   - Uploads security report

2. **Unit Tests** (`test`)
   - Runs on Python 3.11
   - PostgreSQL service for database tests
   - Generates coverage report
   - Uploads test results and coverage

3. **Docker Test** (`docker-test`)
   - Runs tests in Docker Compose
   - Validates containerized environment
   - Clean up after execution

4. **All Checks Passed** (`all-checks-passed`)
   - Ensures all jobs succeeded
   - Blocks PR merge if any test fails

### Viewing Results

1. Go to the "Actions" tab in GitHub
2. Click on the workflow run
3. View job logs and artifacts
4. Download coverage reports

### Status Badges

Add to your PR or README:

```markdown
![Tests](https://github.com/cte-zl-ifrn/integration-moodle_elt/actions/workflows/tests.yml/badge.svg)
```

## Code Coverage

### Generate Coverage Report

```bash
# Terminal report
PYTHONPATH=./dags pytest tests/ --cov=dags --cov-report=term-missing

# HTML report (recommended)
PYTHONPATH=./dags pytest tests/ --cov=dags --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

- **Target**: 80% code coverage
- **Current**: ~38% for moodle_api.py (initial implementation)
- **Priority**: Core utility functions and API client

### Exclude from Coverage

In `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## Writing New Tests

### Test File Naming

- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<feature>_integration.py`
- Test functions: `test_<scenario_description>`

### Test Structure

```python
"""
Module docstring describing what is tested
"""

import pytest
from unittest.mock import Mock, patch


class TestFeatureName:
    """Test class for a specific feature"""
    
    def test_scenario_description(self):
        """Test a specific scenario"""
        # Arrange - Set up test data
        input_data = {"key": "value"}
        
        # Act - Execute the code being tested
        result = function_under_test(input_data)
        
        # Assert - Verify the results
        assert result == expected_value
```

### Using Fixtures

```python
def test_with_fixture(sample_user_data):
    """Use predefined fixtures from fixtures/common_fixtures.py"""
    assert sample_user_data["id"] == 123
```

### Mocking

```python
@patch('module.function')
def test_with_mock(mock_function):
    """Mock external dependencies"""
    mock_function.return_value = {"data": "mocked"}
    result = code_that_calls_function()
    mock_function.assert_called_once()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("https://valid.com", True),
    ("http://invalid.com", False),
])
def test_url_validation(input, expected):
    """Test multiple scenarios"""
    result = validate_url(input)
    assert result == expected
```

## Docker Testing Details

### Test Service Configuration

In `docker-compose.yml`:

```yaml
test:
  image: python:3.11-slim
  working_dir: /app
  volumes:
    - .:/app
  environment:
    - PYTHONPATH=/app/dags
  command: >
    bash -c "
      pip install -r requirements.txt -r requirements-dev.txt &&
      pytest -v --cov=dags
    "
  profiles:
    - test
```

### Running in Docker

```bash
# Run tests
docker compose --profile test up --build test

# Run tests and keep container running for debugging
docker compose --profile test up --build

# Access test container
docker compose --profile test run test bash

# Clean up
docker compose --profile test down -v
```

## Troubleshooting

### Import Errors

Make sure `PYTHONPATH` includes the `dags` directory:

```bash
export PYTHONPATH=./dags
pytest tests/
```

### Module Not Found

Install dependencies:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Pre-commit Hook Fails

Update pre-commit hooks:

```bash
pre-commit autoupdate
pre-commit install --install-hooks
```

### Docker Test Fails

Rebuild the container:

```bash
docker compose --profile test build --no-cache test
docker compose --profile test up test
```

### Coverage Too Low

Focus tests on critical code paths and increase test coverage for:
1. Error handling
2. Edge cases
3. Configuration parsing
4. API operations

## Best Practices

1. **Test Naming**
   - Use descriptive names
   - Follow pattern: `test_<what>_<condition>_<expected_result>`

2. **Test Independence**
   - Each test should be independent
   - Don't rely on test execution order
   - Clean up after tests

3. **Mock External Dependencies**
   - Mock API calls
   - Mock database connections
   - Mock file I/O

4. **Use Fixtures**
   - Create reusable test data
   - Use pytest fixtures
   - Share fixtures via conftest.py

5. **Test Edge Cases**
   - Empty inputs
   - Null values
   - Invalid data
   - Boundary conditions

6. **Keep Tests Fast**
   - Unit tests should run quickly
   - Mark slow tests with `@pytest.mark.slow`
   - Run slow tests separately

## Continuous Improvement

### Adding More Tests

1. Review `docs/TEST_SCENARIOS.md`
2. Identify untested scenarios
3. Write test following the pattern
4. Ensure it passes
5. Update coverage report

### Updating Test Infrastructure

1. Update `requirements-dev.txt` for new tools
2. Update `.pre-commit-config.yaml` for new hooks
3. Update `.github/workflows/tests.yml` for new jobs
4. Update this documentation

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Black Documentation](https://black.readthedocs.io/)
- [Test Scenarios Documentation](docs/TEST_SCENARIOS.md)

## Support

For issues or questions:
1. Check this guide
2. Review test output and logs
3. Check GitHub Actions logs
4. Review `docs/TEST_SCENARIOS.md`
5. Open an issue in the repository
