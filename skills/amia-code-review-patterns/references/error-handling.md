---
name: "Error Handling in Code Reviews"
description: "Common error patterns, anti-patterns, and best practices for reviewing error handling code"
---

# Error Handling in Code Reviews

## Table of Contents

- [Core Principles](#core-principles)
- [Common Error Handling Patterns](#common-error-handling-patterns)
  - [1. Try-Catch-Finally (Exception-Based)](#1-try-catch-finally-exception-based)
  - [2. Context Managers (Resource Management)](#2-context-managers-resource-management)
  - [3. Result Types (Functional Approach)](#3-result-types-functional-approach)
  - [4. Error Codes (Legacy/C-Style)](#4-error-codes-legacyc-style)
- [Anti-Patterns to Flag](#anti-patterns-to-flag)
- [Language-Specific Patterns](#language-specific-patterns)
  - [Python](#python)
  - [JavaScript/TypeScript](#javascripttypescript)
  - [Go](#go)
- [Review Checklist](#review-checklist)
  - [Error Detection](#error-detection)
  - [Error Handling](#error-handling)
  - [Resource Management](#resource-management)
  - [Error Communication](#error-communication)
  - [Security](#security)
- [Common Scenarios](#common-scenarios)
  - [Scenario 1: Database Operations](#scenario-1-database-operations)
  - [Scenario 2: External API Calls](#scenario-2-external-api-calls)
  - [Scenario 3: File Operations](#scenario-3-file-operations)
  - [Scenario 4: User Input Validation](#scenario-4-user-input-validation)
- [Error Logging Best Practices](#error-logging-best-practices)
  - [What to Log](#what-to-log)
  - [What NOT to Log](#what-not-to-log)
- [Testing Error Handling](#testing-error-handling)
  - [Reviewers Should Verify Tests Exist](#reviewers-should-verify-tests-exist)
- [Summary](#summary)

Proper error handling is critical for robust, maintainable software. This guide helps reviewers identify error handling issues and suggest improvements.

## Core Principles

1. **Fail Fast**: Detect errors early and fail loudly
2. **Be Specific**: Provide actionable error messages
3. **Clean Up**: Always release resources, even on error
4. **Don't Hide**: Never silently swallow errors
5. **Context Matters**: Include enough context to debug

---

## Common Error Handling Patterns

### 1. Try-Catch-Finally (Exception-Based)

**Python example:**
```python
def read_config(file_path: str) -> dict:
    """Read configuration from file."""
    file_handle = None
    try:
        file_handle = open(file_path, 'r')
        config = json.load(file_handle)
        validate_config(config)
        return config
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {file_path}: {e}")
    except ValidationError as e:
        raise ConfigError(f"Invalid config: {e}")
    finally:
        if file_handle:
            file_handle.close()
```

**Review checklist:**
- [ ] Specific exception types are caught (not bare `except`)
- [ ] Resources are cleaned up in `finally` block
- [ ] Errors are re-raised with context
- [ ] Original error is not lost (use `raise from` in Python)

### 2. Context Managers (Resource Management)

**Better approach using context manager:**
```python
def read_config(file_path: str) -> dict:
    """Read configuration from file."""
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        validate_config(config)
        return config
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {file_path}: {e}")
    except ValidationError as e:
        raise ConfigError(f"Invalid config: {e}")
```

**Review checklist:**
- [ ] Context managers used for file/network/database resources
- [ ] No manual cleanup needed
- [ ] Errors still propagate correctly

### 3. Result Types (Functional Approach)

**Example (Rust-style Result in Python):**
```python
from typing import Union
from dataclasses import dataclass

@dataclass
class Ok:
    value: Any

@dataclass
class Err:
    error: str

Result = Union[Ok, Err]

def divide(a: float, b: float) -> Result:
    """Divide a by b, returning Result."""
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# Usage
result = divide(10, 2)
if isinstance(result, Ok):
    print(f"Result: {result.value}")
else:
    print(f"Error: {result.error}")
```

**Review checklist:**
- [ ] Errors are explicit in return type
- [ ] Caller is forced to handle error case
- [ ] No exceptions can be silently ignored

### 4. Error Codes (Legacy/C-Style)

**Example:**
```python
def save_user(user: User) -> tuple[bool, str]:
    """Save user to database.

    Returns:
        (success: bool, message: str)
    """
    if not user.email:
        return False, "Email is required"

    if db.exists(user.email):
        return False, "Email already exists"

    try:
        db.save(user)
        return True, "User saved successfully"
    except DatabaseError as e:
        return False, f"Database error: {e}"
```

**Review checklist:**
- [ ] Return value convention is documented
- [ ] Caller checks return code before using value
- [ ] Error messages are informative

---

## Anti-Patterns to Flag

### ❌ 1. Silent Failures

**Bad:**
```python
try:
    result = risky_operation()
except Exception:
    pass  # Silent failure!
```

**Why it's bad:**
- Errors are hidden
- Debugging becomes impossible
- Failures cascade silently

**Fix:**
```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"risky_operation failed: {e}")
    raise  # Re-raise or handle appropriately
```

### ❌ 2. Catching Too Broadly

**Bad:**
```python
try:
    config = load_config()
    process_data(config)
    send_email()
except Exception as e:
    print(f"Something went wrong: {e}")
```

**Why it's bad:**
- Catches unintended exceptions (KeyboardInterrupt, MemoryError, etc.)
- Loses information about which operation failed
- Makes debugging difficult

**Fix:**
```python
try:
    config = load_config()
except ConfigError as e:
    logger.error(f"Config loading failed: {e}")
    raise

try:
    process_data(config)
except ProcessingError as e:
    logger.error(f"Data processing failed: {e}")
    raise

try:
    send_email()
except EmailError as e:
    logger.warning(f"Email send failed: {e}")
    # Maybe don't raise - email is non-critical
```

### ❌ 3. Losing Error Context

**Bad:**
```python
try:
    user = get_user(user_id)
except UserNotFound:
    raise ValueError("Invalid user")  # Lost which user_id!
```

**Why it's bad:**
- Debugging requires guessing which user_id failed
- Original error details are lost

**Fix:**
```python
try:
    user = get_user(user_id)
except UserNotFound as e:
    raise ValueError(f"Invalid user_id {user_id}") from e
```

### ❌ 4. Generic Error Messages

**Bad:**
```python
if not user:
    raise ValueError("Invalid input")
```

**Why it's bad:**
- Doesn't tell user what's wrong
- Doesn't tell developer what to fix
- Multiple validation errors have same message

**Fix:**
```python
if not user:
    raise ValueError("User object cannot be None")

if not user.email:
    raise ValueError(f"User {user.id} missing required field: email")
```

### ❌ 5. Ignoring Resource Cleanup

**Bad:**
```python
def process_file(path):
    f = open(path)
    data = f.read()
    result = process(data)  # If this raises, file never closes!
    f.close()
    return result
```

**Why it's bad:**
- File descriptors leak
- Database connections leak
- Can cause "too many open files" errors

**Fix:**
```python
def process_file(path):
    with open(path) as f:
        data = f.read()
        return process(data)
```

### ❌ 6. Returning None on Error

**Bad:**
```python
def get_user_age(user_id: int) -> int | None:
    try:
        user = db.get_user(user_id)
        return user.age
    except UserNotFound:
        return None  # Ambiguous! Is None a valid age?
```

**Why it's bad:**
- Caller can't distinguish "user not found" from "age is None"
- Forces None-checking everywhere
- Errors are hidden in data flow

**Fix (Option 1 - Explicit exception):**
```python
def get_user_age(user_id: int) -> int:
    """Get user age. Raises UserNotFound if user doesn't exist."""
    user = db.get_user(user_id)  # Let exception propagate
    if user.age is None:
        raise ValueError(f"User {user_id} has no age set")
    return user.age
```

**Fix (Option 2 - Optional with specific meaning):**
```python
def get_user_age(user_id: int) -> int | None:
    """Get user age. Returns None if age not set.

    Raises:
        UserNotFound: If user_id doesn't exist
    """
    user = db.get_user(user_id)  # Raises UserNotFound
    return user.age  # None means "age not set", not "error"
```

### ❌ 7. Creating "God" Error Handlers

**Bad:**
```python
def handle_all_errors(error):
    """Central error handler for everything."""
    if isinstance(error, DatabaseError):
        # handle database error
    elif isinstance(error, NetworkError):
        # handle network error
    elif isinstance(error, ValidationError):
        # handle validation error
    # ... 50 more cases
```

**Why it's bad:**
- Centralizes error handling logic
- Makes errors hard to trace
- Violates single responsibility

**Fix:**
Handle errors close to where they occur:
```python
# In database layer
try:
    db.execute(query)
except DatabaseError as e:
    logger.error(f"Query failed: {query}, error: {e}")
    raise

# In network layer
try:
    response = requests.get(url)
except RequestException as e:
    logger.error(f"HTTP request failed: {url}, error: {e}")
    raise NetworkError(f"Failed to fetch {url}") from e
```

---

## Language-Specific Patterns

### Python

**Custom exceptions:**
```python
class ApplicationError(Exception):
    """Base exception for application."""
    pass

class ConfigError(ApplicationError):
    """Configuration-related errors."""
    pass

class ValidationError(ApplicationError):
    """Validation errors."""
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}: {message}")
```

**Chaining exceptions:**
```python
try:
    config = parse_config(raw_data)
except json.JSONDecodeError as e:
    raise ConfigError("Invalid JSON config") from e
    # `from e` preserves original traceback
```

### JavaScript/TypeScript

**Async error handling:**
```typescript
// Bad
async function fetchUser(id: number) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();  // What if fetch fails?
}

// Good
async function fetchUser(id: number): Promise<User> {
    try {
        const response = await fetch(`/api/users/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        throw new UserFetchError(`Failed to fetch user ${id}`, { cause: error });
    }
}
```

**Promise rejection:**
```typescript
// Bad
someAsyncOperation()
    .then(result => process(result))
    .catch(err => console.log(err));  // Silent failure!

// Good
someAsyncOperation()
    .then(result => process(result))
    .catch(err => {
        logger.error('Operation failed', err);
        throw err;  // Re-throw or handle appropriately
    });
```

### Go

**Error wrapping:**
```go
// Bad
func GetUser(id int) (*User, error) {
    user, err := db.Query(id)
    if err != nil {
        return nil, err  // Lost context!
    }
    return user, nil
}

// Good
func GetUser(id int) (*User, error) {
    user, err := db.Query(id)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}
```

---

## Review Checklist

### Error Detection

- [ ] All error conditions are identified
- [ ] Edge cases are handled (null, empty, out-of-range)
- [ ] External dependencies failures are handled (network, DB, file I/O)
- [ ] Invalid user input is validated

### Error Handling

- [ ] Errors are caught at appropriate level
- [ ] Specific exception types are used (not generic)
- [ ] Error messages are clear and actionable
- [ ] Context is preserved (don't lose original error)
- [ ] Errors are logged with sufficient detail

### Resource Management

- [ ] Resources are always cleaned up (files, connections, locks)
- [ ] Context managers or RAII used where appropriate
- [ ] No resource leaks on error paths
- [ ] Cleanup happens even if error occurs

### Error Communication

- [ ] API documentation specifies possible errors
- [ ] Error types are part of function signature (where applicable)
- [ ] Caller has enough information to handle error
- [ ] Errors include actionable information (what failed, why, how to fix)

### Security

- [ ] Errors don't leak sensitive information
- [ ] Stack traces not exposed to end users
- [ ] Error messages don't reveal system internals
- [ ] Logging doesn't include secrets/passwords

---

## Common Scenarios

### Scenario 1: Database Operations

**Review question:** "Does this handle database failures?"

```python
# Minimal handling
def get_user(user_id: int) -> User:
    """Get user by ID."""
    try:
        return db.query("SELECT * FROM users WHERE id = ?", (user_id,))
    except DatabaseError as e:
        logger.error(f"Database query failed for user_id={user_id}: {e}")
        raise UserNotFoundError(f"User {user_id} not found") from e
```

**What to check:**
- [ ] Database connection errors are handled
- [ ] Query errors are logged
- [ ] Transactions are rolled back on error
- [ ] Original exception is preserved (`from e`)

### Scenario 2: External API Calls

**Review question:** "What if the API is down?"

```python
def fetch_weather(city: str) -> dict:
    """Fetch weather data for city."""
    try:
        response = requests.get(
            f"{API_BASE}/weather",
            params={"city": city},
            timeout=5  # Always set timeout!
        )
        response.raise_for_status()  # Raises for 4xx/5xx
        return response.json()
    except requests.Timeout:
        raise WeatherServiceError(f"Timeout fetching weather for {city}")
    except requests.RequestException as e:
        raise WeatherServiceError(f"Failed to fetch weather: {e}") from e
```

**What to check:**
- [ ] Timeout is set (prevents hanging forever)
- [ ] HTTP errors are checked (4xx, 5xx)
- [ ] Network errors are caught
- [ ] Retries with backoff (if appropriate)
- [ ] Fallback/cache considered (if appropriate)

### Scenario 3: File Operations

**Review question:** "What if the file doesn't exist or is corrupted?"

```python
def load_config(path: str) -> dict:
    """Load JSON config from file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}")
    except PermissionError:
        raise ConfigError(f"Permission denied reading {path}")
```

**What to check:**
- [ ] File not found is handled
- [ ] Invalid format is handled
- [ ] Permission errors are handled
- [ ] File is closed (context manager ensures this)

### Scenario 4: User Input Validation

**Review question:** "What if the user provides invalid data?"

```python
def create_user(data: dict) -> User:
    """Create user from input data."""
    errors = []

    email = data.get('email', '').strip()
    if not email:
        errors.append("Email is required")
    elif not is_valid_email(email):
        errors.append(f"Invalid email format: {email}")

    age = data.get('age')
    if age is None:
        errors.append("Age is required")
    elif not isinstance(age, int) or age < 0 or age > 150:
        errors.append(f"Invalid age: {age}")

    if errors:
        raise ValidationError("Invalid user data", errors=errors)

    return User(email=email, age=age)
```

**What to check:**
- [ ] All required fields are validated
- [ ] Type checking is performed
- [ ] Range/format validation is done
- [ ] Multiple errors are collected (not just first one)
- [ ] Clear error messages for each validation

---

## Error Logging Best Practices

### What to Log

**Always log:**
- Exception type and message
- Context (user_id, request_id, etc.)
- Timestamp
- Stack trace (for unexpected errors)

**Example:**
```python
logger.error(
    "Payment processing failed",
    extra={
        "user_id": user.id,
        "order_id": order.id,
        "amount": order.total,
        "error": str(e)
    },
    exc_info=True  # Include stack trace
)
```

### What NOT to Log

**Never log:**
- Passwords or API keys
- Credit card numbers
- Personally identifiable information (PII) without necessity
- Full request bodies with sensitive data

**Bad:**
```python
logger.error(f"Login failed for {username} with password {password}")
```

**Good:**
```python
logger.error(f"Login failed for user {user_id}")
```

---

## Testing Error Handling

### Reviewers Should Verify Tests Exist

**Questions to ask:**
- Does the test suite cover error paths?
- Are edge cases tested?
- Are resource leaks tested?

**Example test:**
```python
def test_get_user_not_found():
    """Test get_user raises UserNotFound when user doesn't exist."""
    with pytest.raises(UserNotFoundError) as exc_info:
        get_user(99999)

    assert "User 99999 not found" in str(exc_info.value)

def test_config_invalid_json():
    """Test load_config raises ConfigError for invalid JSON."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("{invalid json}")
        f.flush()

        with pytest.raises(ConfigError) as exc_info:
            load_config(f.name)

        assert "Invalid JSON" in str(exc_info.value)
```

---

## Summary

When reviewing error handling:

1. **Verify all error paths are handled**
2. **Check resources are cleaned up**
3. **Ensure error messages are clear**
4. **Confirm context is preserved**
5. **Validate logging is appropriate**
6. **Check tests cover error cases**

**Red flags:**
- Silent failures (`except: pass`)
- Broad exception catches (`except Exception`)
- Missing resource cleanup
- Generic error messages
- Lost error context
- Sensitive data in logs
