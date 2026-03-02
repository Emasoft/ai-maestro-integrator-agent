# Python Review Patterns - Part 1: Style, Types, and Documentation

## Table of Contents

- 2.1 Python code style and formatting checklist
  - 2.1.1 Essential style rules table (PEP 8)
  - 2.1.2 Formatting checklist (whitespace, blank lines, operators)
  - 2.1.3 Example: Proper Python formatting
- 2.2 Type hints verification and mypy compliance
  - 2.2.1 Type hint syntax for Python 3.10+
  - 2.2.2 mypy configuration in pyproject.toml
  - 2.2.3 Type hint review checklist
  - 2.2.4 Common mypy errors and fixes
- 2.3 Docstring standards (Google, NumPy, Sphinx)
  - 2.3.1 Google style docstrings (recommended)
  - 2.3.2 NumPy style docstrings
  - 2.3.3 Docstring review checklist

---

## 2.1 Python Code Style and Formatting Checklist

Python code should follow PEP 8 with modern tooling enforcement.

### Essential Style Rules

| Rule | Good | Bad |
|------|------|-----|
| Indentation | 4 spaces | Tabs or 2 spaces |
| Line length | Max 88 (Black default) | Lines over 120 chars |
| Naming: variables | `snake_case` | `camelCase`, `PascalCase` |
| Naming: classes | `PascalCase` | `snake_case`, `camelCase` |
| Naming: constants | `SCREAMING_SNAKE_CASE` | `lowercase` |
| Naming: private | `_single_underscore` | `__double_underscore` (unless name mangling needed) |
| String quotes | Consistent (prefer double) | Mixed single/double |
| Trailing commas | Yes, in multiline | No trailing commas |

### Formatting Checklist

- [ ] No trailing whitespace
- [ ] Single blank line between function definitions
- [ ] Two blank lines between top-level definitions
- [ ] No multiple statements on one line
- [ ] Spaces around operators (`a = b + c`, not `a=b+c`)
- [ ] No spaces inside brackets (`func(a, b)`, not `func( a, b )`)
- [ ] Consistent quote style throughout file
- [ ] Line continuations use parentheses, not backslashes

### Example: Proper Formatting

```python
# Good: Clean, readable Python
from collections.abc import Mapping
from typing import Any


CONSTANT_VALUE = 42


class DataProcessor:
    """Process data according to configured rules."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self._config = config
        self._processed_count = 0

    def process_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Process a single item.

        Args:
            item: The item to process.

        Returns:
            The processed item with transformations applied.
        """
        result = {
            "id": item["id"],
            "name": item.get("name", "unnamed"),
            "processed": True,
        }
        self._processed_count += 1
        return result
```

---

## 2.2 Type Hints Verification and mypy Compliance

Modern Python (3.10+) should use type hints extensively.

### Type Hint Syntax

```python
# Variable annotations
name: str = "example"
count: int = 0
items: list[str] = []
mapping: dict[str, int] = {}

# Function signatures
def process(data: list[dict[str, Any]], *, strict: bool = False) -> list[str]:
    ...

# Optional types (use | instead of Optional)
def find_user(user_id: int) -> User | None:
    ...

# Union types
def parse_input(value: str | int | float) -> str:
    ...

# Generic types
from collections.abc import Callable, Iterable, Mapping

def apply_all(funcs: Iterable[Callable[[int], int]], value: int) -> int:
    ...

# Type aliases
UserID = int
UserMap = dict[UserID, "User"]
```

### mypy Configuration

Create `pyproject.toml` with mypy settings:

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true
show_column_numbers = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party.*"
ignore_missing_imports = true
```

### Type Hint Review Checklist

- [ ] All public functions have return type annotations
- [ ] All function parameters have type annotations
- [ ] Class attributes have type annotations
- [ ] No use of `Any` without justification
- [ ] `Optional[X]` replaced with `X | None` (Python 3.10+)
- [ ] Generic types use `collections.abc` not `typing` where possible
- [ ] `TypeVar` used correctly for generic functions
- [ ] `Protocol` used for structural typing
- [ ] No `# type: ignore` without explanation comment

### Common mypy Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing return statement` | Not all paths return | Add return or raise in all branches |
| `Incompatible return type` | Wrong type returned | Fix return type or annotation |
| `has no attribute` | Missing attribute in type | Check type annotation, use Protocol |
| `Argument has incompatible type` | Wrong argument type | Fix caller or widen parameter type |
| `Missing type parameters` | Generic without params | Add `[T]` to generic types |

---

## 2.3 Docstring Standards

Python has three major docstring conventions.

### Google Style (Recommended)

```python
def fetch_data(
    url: str,
    timeout: float = 30.0,
    *,
    retry_count: int = 3,
) -> dict[str, Any]:
    """Fetch data from a remote URL.

    Makes an HTTP GET request to the specified URL and returns the
    parsed JSON response. Implements exponential backoff for retries.

    Args:
        url: The URL to fetch data from. Must be a valid HTTP/HTTPS URL.
        timeout: Request timeout in seconds. Defaults to 30.0.
        retry_count: Number of retry attempts on failure. Defaults to 3.

    Returns:
        A dictionary containing the parsed JSON response.

    Raises:
        ValueError: If the URL is malformed or empty.
        HTTPError: If the request fails after all retries.
        JSONDecodeError: If the response is not valid JSON.

    Example:
        >>> data = fetch_data("https://api.example.com/data")
        >>> print(data["status"])
        'ok'
    """
```

### NumPy Style

```python
def calculate_statistics(values: np.ndarray) -> dict[str, float]:
    """
    Calculate descriptive statistics for an array of values.

    Parameters
    ----------
    values : np.ndarray
        1-D array of numerical values.

    Returns
    -------
    dict[str, float]
        Dictionary containing:
        - 'mean': arithmetic mean
        - 'std': standard deviation
        - 'min': minimum value
        - 'max': maximum value

    Raises
    ------
    ValueError
        If the input array is empty.

    See Also
    --------
    numpy.mean : Calculate arithmetic mean.
    numpy.std : Calculate standard deviation.

    Examples
    --------
    >>> stats = calculate_statistics(np.array([1, 2, 3, 4, 5]))
    >>> stats['mean']
    3.0
    """
```

### Docstring Review Checklist

- [ ] All public modules have module docstrings
- [ ] All public classes have class docstrings
- [ ] All public functions/methods have docstrings
- [ ] Docstrings describe what, not how
- [ ] Args section documents all parameters
- [ ] Returns section describes return value
- [ ] Raises section lists all exceptions
- [ ] Examples are included for complex functions
- [ ] Consistent style throughout project
