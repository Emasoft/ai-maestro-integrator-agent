# Documentation Analysis: Common Issues

## Table of Contents

- [Common Issues to Look For](#common-issues-to-look-for)
  - [Missing Docstrings](#missing-docstrings)
  - [Poor Documentation Quality](#poor-documentation-quality)
  - [Missing Examples](#missing-examples)
  - [Poor README](#poor-readme)
  - [Missing Error Documentation](#missing-error-documentation)
  - [Unhelpful Comments](#unhelpful-comments)

This document covers common documentation issues to look for during code review, with examples.

**Parent document**: [documentation-analysis.md](./documentation-analysis.md)

---

## Common Issues to Look For

### Missing Docstrings

**Undocumented public function**
```python
# WRONG: No docstring
def calculate_discount(price, customer_type, quantity):
    if customer_type == 'premium':
        return price * 0.9 * quantity
    return price * quantity

# CORRECT: Complete docstring
def calculate_discount(price: float, customer_type: str, quantity: int) -> float:
    """Calculate total price with applicable discount.

    Applies a 10% discount for premium customers. Regular customers
    pay full price.

    Args:
        price: Unit price of the item in dollars
        customer_type: Customer category ('premium' or 'regular')
        quantity: Number of items to purchase

    Returns:
        Total price after discount in dollars

    Raises:
        ValueError: If price is negative or quantity is not positive

    Examples:
        >>> calculate_discount(100.0, 'premium', 2)
        180.0
        >>> calculate_discount(100.0, 'regular', 2)
        200.0
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    if customer_type == 'premium':
        return price * 0.9 * quantity
    return price * quantity
```

**Undocumented class**
```python
# WRONG: No class documentation
class UserManager:
    def __init__(self, db):
        self.db = db

    def create_user(self, name, email):
        pass

# CORRECT: Documented class
class UserManager:
    """Manages user operations including creation, retrieval, and updates.

    This class provides a high-level interface for user management,
    handling validation, database operations, and error handling.

    Attributes:
        db: Database connection for user operations

    Examples:
        >>> manager = UserManager(database)
        >>> user = manager.create_user("Alice", "alice@example.com")
        >>> print(user.name)
        Alice
    """

    def __init__(self, db: Database):
        """Initialize UserManager with database connection.

        Args:
            db: Active database connection
        """
        self.db = db

    def create_user(self, name: str, email: str) -> User:
        """Create a new user with given name and email.

        Args:
            name: User's full name
            email: User's email address (must be unique)

        Returns:
            Created User object

        Raises:
            ValueError: If email is invalid or already exists
        """
        pass
```

### Poor Documentation Quality

**Redundant docstring**
```python
# WRONG: States the obvious
def add(a, b):
    """Add two numbers together."""
    return a + b

# CORRECT: Adds value (if needed at all for simple case)
def add(a: Number, b: Number) -> Number:
    """Add two numbers with overflow protection.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b

    Note:
        For very large integers, this may raise OverflowError
        on systems with limited integer size.
    """
    return a + b
```

**Outdated documentation**
```python
# WRONG: Documentation doesn't match implementation
def process_order(order_id, user_id):
    """Process an order and send confirmation email.

    Args:
        order_id: ID of the order to process
    """
    # Code no longer sends email, and user_id param not documented
    order = Order.get(order_id)
    order.process()
    return order

# CORRECT: Updated documentation
def process_order(order_id: int, user_id: int) -> Order:
    """Process an order for a specific user.

    Args:
        order_id: ID of the order to process
        user_id: ID of the user who owns the order

    Returns:
        Processed Order object

    Raises:
        OrderNotFoundError: If order doesn't exist
        UnauthorizedError: If user doesn't own the order
    """
    order = Order.get(order_id)
    if order.user_id != user_id:
        raise UnauthorizedError("User doesn't own this order")
    order.process()
    return order
```

**Vague parameter descriptions**
```python
# WRONG: Vague descriptions
def send_notification(user, message, level):
    """Send a notification.

    Args:
        user: The user
        message: The message
        level: The level
    """
    pass

# CORRECT: Clear descriptions
def send_notification(
    user: User,
    message: str,
    level: NotificationLevel
) -> bool:
    """Send a notification to a user through their preferred channel.

    Args:
        user: User object containing notification preferences
        message: Notification message text (max 500 characters)
        level: Urgency level (INFO, WARNING, ERROR, CRITICAL)

    Returns:
        True if notification sent successfully, False otherwise

    Raises:
        ValueError: If message exceeds 500 characters
    """
    pass
```

### Missing Examples

**Complex function without examples**
```python
# WRONG: Complex function, no examples
def parse_date_range(date_string, format_string=None, timezone=None):
    """Parse a date range string into start and end dates."""
    pass

# CORRECT: Examples provided
def parse_date_range(
    date_string: str,
    format_string: Optional[str] = None,
    timezone: Optional[str] = None
) -> Tuple[datetime, datetime]:
    """Parse a date range string into start and end dates.

    Supports various formats including ISO 8601, relative dates,
    and natural language ranges.

    Args:
        date_string: Date range string to parse
        format_string: Optional custom format (uses ISO 8601 if None)
        timezone: Timezone name (uses UTC if None)

    Returns:
        Tuple of (start_date, end_date) as datetime objects

    Examples:
        >>> start, end = parse_date_range("2024-01-01 to 2024-01-31")
        >>> print(start.date())
        2024-01-01

        >>> start, end = parse_date_range("last week")
        >>> print((end - start).days)
        7

        >>> start, end = parse_date_range(
        ...     "01/01/2024 - 01/31/2024",
        ...     format_string="%m/%d/%Y"
        ... )
    """
    pass
```

### Poor README

**Incomplete README**
```markdown
<!-- WRONG: Minimal README -->
# MyProject

A project that does stuff.

## Installation
```
pip install myproject
```

<!-- CORRECT: Comprehensive README -->
# MyProject

A high-performance data processing library for analyzing large datasets
with built-in caching and parallel processing support.

[![Build Status](https://img.shields.io/travis/user/myproject.svg)](https://travis-ci.org/user/myproject)
[![Coverage](https://img.shields.io/codecov/c/github/user/myproject.svg)](https://codecov.io/github/user/myproject)
[![PyPI version](https://img.shields.io/pypi/v/myproject.svg)](https://pypi.org/project/myproject/)

## Features

- Fast parallel data processing
- Automatic caching for repeated operations
- Support for multiple data formats (CSV, JSON, Parquet)
- Memory-efficient streaming for large files
- Built-in data validation

## Installation

### Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- Linux, macOS, or Windows

### Install via pip
```bash
pip install myproject
```

### Install from source
```bash
git clone https://github.com/user/myproject.git
cd myproject
pip install -e .
```

## Quick Start

```python
from myproject import DataProcessor

# Create processor
processor = DataProcessor()

# Load and process data
result = processor.process('data.csv', workers=4)

# Access results
print(f"Processed {result.rows} rows in {result.duration}s")
```

## Configuration

Create a `config.yaml` file:

```yaml
processing:
  workers: 4
  chunk_size: 1000
  cache_enabled: true
cache:
  directory: .cache
  max_size_mb: 1000
```

## Documentation

Full documentation is available at https://myproject.readthedocs.io

## Contributing

See [CONTRIBUTING.md]\(CONTRIBUTING.md\) for guidelines.

## License

MIT License - see [LICENSE]\(LICENSE\) for details.
```

### Missing Error Documentation

**Undocumented exceptions**
```python
# WRONG: No exception documentation
def get_user(user_id):
    """Get a user by ID."""
    if user_id < 0:
        raise ValueError("Invalid ID")
    user = db.get(user_id)
    if not user:
        raise UserNotFoundError()
    return user

# CORRECT: Exceptions documented
def get_user(user_id: int) -> User:
    """Get a user by ID.

    Args:
        user_id: Unique user identifier (must be positive)

    Returns:
        User object with the specified ID

    Raises:
        ValueError: If user_id is negative
        UserNotFoundError: If no user exists with the given ID
        DatabaseError: If database connection fails

    Examples:
        >>> user = get_user(123)
        >>> print(user.name)
        Alice

        >>> get_user(-1)
        ValueError: Invalid ID

        >>> get_user(999)
        UserNotFoundError: User 999 not found
    """
    if user_id < 0:
        raise ValueError(f"Invalid ID: {user_id}")
    user = db.get(user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

### Unhelpful Comments

**Obvious comments**
```python
# WRONG: Comment states the obvious
# Increment counter
counter = counter + 1

# Loop through users
for user in users:
    # Print user name
    print(user.name)

# CORRECT: Self-documenting code, comments only where needed
counter += 1

for user in users:
    print(user.name)

# Non-obvious case that needs comment
# Convert to UTC before comparison to handle DST correctly
utc_time = local_time.astimezone(timezone.utc)
```

**Why vs what comments**
```python
# WRONG: Comment explains what
# Set timeout to 30 seconds
timeout = 30

# CORRECT: Comment explains why
# 30 second timeout to prevent hanging on slow networks
# while allowing large file uploads to complete
timeout = 30
```
