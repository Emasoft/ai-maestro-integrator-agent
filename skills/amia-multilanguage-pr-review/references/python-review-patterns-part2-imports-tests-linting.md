# Python Review Patterns - Part 2: Imports, Tests, and Linting

## Table of Contents

- 2.4 Import organization and dependency management
  - 2.4.1 Import grouping order (stdlib, third-party, local)
  - 2.4.2 Import style rules table
  - 2.4.3 Circular import prevention strategies
  - 2.4.4 Dependency management with pyproject.toml
- 2.5 Test framework patterns with pytest
  - 2.5.1 pytest project structure
  - 2.5.2 Essential pytest patterns (fixtures, conftest)
  - 2.5.3 pytest configuration in pyproject.toml
  - 2.5.4 Test review checklist
- 2.6 Linting with ruff, mypy, and bandit
  - 2.6.1 ruff configuration
  - 2.6.2 Running linters (ruff, mypy, bandit commands)
  - 2.6.3 bandit configuration
  - 2.6.4 Common security issues bandit detects
  - 2.6.5 Linting review checklist

---

## 2.4 Import Organization and Dependency Management

### Import Organization Rules

Imports should be grouped in this order, separated by blank lines:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# 1. Standard library
import json
import os
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TypeVar

# 2. Third-party
import httpx
import pydantic
from fastapi import FastAPI, HTTPException

# 3. Local application
from myapp.config import Settings
from myapp.models import User, UserCreate
from myapp.utils import format_date, parse_input
```

### Import Style Rules

| Style | When to Use |
|-------|-------------|
| `import module` | Accessing many items from module |
| `from module import item` | Using specific items frequently |
| `from module import item as alias` | Name conflicts or long names |
| `import module as alias` | Standard abbreviations (np, pd) |

### Circular Import Prevention

Circular imports cause `ImportError`. Prevention strategies:

```python
# Strategy 1: Import inside function
def process_user(user_id: int) -> "User":
    from myapp.models import User  # Delayed import
    return User.get(user_id)

# Strategy 2: TYPE_CHECKING guard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.models import User  # Only for type hints

def process_user(user_id: int) -> "User":
    ...

# Strategy 3: Restructure modules
# Move shared code to a base module imported by both
```

### Dependency Management with pyproject.toml

```toml
[project]
name = "myproject"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]
```

---

## 2.5 Test Framework Patterns with pytest

### pytest Project Structure

```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── models.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_models.py
│   └── test_utils.py
└── pyproject.toml
```

### Essential pytest Patterns

```python
# tests/conftest.py
import pytest
from mypackage.models import Database

@pytest.fixture
def db() -> Database:
    """Provide a clean database for each test."""
    database = Database(":memory:")
    database.initialize()
    yield database
    database.close()

@pytest.fixture
def sample_user(db: Database) -> dict:
    """Create a sample user in the database."""
    user_data = {"name": "Test User", "email": "test@example.com"}
    db.users.insert(user_data)
    return user_data
```

```python
# tests/test_models.py
import pytest
from mypackage.models import User, ValidationError

class TestUser:
    """Test cases for User model."""

    def test_user_creation_with_valid_data(self, db):
        """User should be created with valid data."""
        user = User.create(name="Alice", email="alice@example.com")
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

    def test_user_creation_rejects_invalid_email(self, db):
        """User creation should reject invalid email format."""
        with pytest.raises(ValidationError, match="Invalid email"):
            User.create(name="Bob", email="not-an-email")

    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("user@sub.example.com", True),
        ("invalid", False),
        ("@example.com", False),
    ])
    def test_email_validation(self, email: str, expected: bool):
        """Email validation should correctly identify valid/invalid emails."""
        assert User.is_valid_email(email) == expected
```

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "-p no:cacheprovider",
]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:third_party.*",
]
```

### Test Review Checklist

- [ ] Tests use descriptive names (`test_user_creation_rejects_invalid_email`)
- [ ] Tests have docstrings explaining what they verify
- [ ] Each test verifies one behavior
- [ ] Tests use fixtures for setup/teardown
- [ ] Parametrized tests cover edge cases
- [ ] No sleep() calls (use mocking/fakes)
- [ ] Tests clean up resources (use fixtures or context managers)
- [ ] Integration tests are marked and can be skipped

---

## 2.6 Linting with ruff, mypy, and bandit

### ruff Configuration

ruff is a fast Python linter that replaces flake8, isort, and more.

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "ARG",  # flake8-unused-arguments
    "SIM",  # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "B008",   # function call in default argument
]

[tool.ruff.isort]
known-first-party = ["mypackage"]
force-single-line = true

[tool.ruff.per-file-ignores]
"tests/**" = ["ARG001"]  # Unused arguments OK in tests (fixtures)
```

### Running Linters

```bash
# ruff - lint and format
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix issues
ruff format .                   # Format code

# mypy - type checking
mypy src/                       # Check types in src/
mypy --strict src/              # Strict mode

# bandit - security
bandit -r src/                  # Security scan
bandit -r src/ -ll              # Only medium+ severity
```

### bandit Configuration

```toml
# pyproject.toml
[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # Skip assert warnings (OK in tests)

# Or use .bandit file for more control
```

### Common Security Issues bandit Detects

| Code | Issue | Risk |
|------|-------|------|
| B101 | Assert used | Assertions disabled in optimization |
| B102 | exec() used | Code injection risk |
| B103 | set bad file permissions | Security misconfiguration |
| B104 | Binding to all interfaces | Network exposure |
| B105 | Hardcoded password | Credential exposure |
| B106 | Hardcoded password in function arg | Credential exposure |
| B301 | Pickle usage | Deserialization attack |
| B303 | MD5/SHA1 for security | Weak cryptography |
| B307 | eval() used | Code injection risk |
| B324 | Insecure hash function | Weak cryptography |
| B501 | Request with verify=False | SSL bypass |
| B506 | Unsafe YAML load | Deserialization attack |

### Linting Review Checklist

- [ ] ruff check passes with no errors
- [ ] mypy passes in strict mode (or project mode)
- [ ] bandit reports no high-severity issues
- [ ] No `# noqa` without explanation comment
- [ ] No `# type: ignore` without explanation comment
- [ ] All warnings are addressed or explicitly ignored with reason
