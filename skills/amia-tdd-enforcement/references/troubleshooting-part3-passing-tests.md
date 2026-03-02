# TDD Troubleshooting - Part 3: Passing Tests

## Table of Contents
- [Test Passes But Code Incomplete](#test-passes-but-code-incomplete)
  - [Symptoms](#symptoms)
  - [Root Cause](#root-cause)
  - [Solution](#solution)
  - [Prevention](#prevention)
- [Test Passes on First Run](#test-passes-on-first-run)
  - [Symptoms](#symptoms-1)
  - [Root Cause](#root-cause-1)
  - [Solution](#solution-1)
  - [Prevention](#prevention-1)

---

## Test Passes But Code Incomplete

### Symptoms
- Test passes
- Code works
- But feels like it's not doing enough

### Root Cause
The test only covers one aspect of the behavior. This is **correct**.

### Solution

**This is not a problem. This is TDD working correctly.**

**Step 1: Accept that implementation is intentionally minimal**

TDD builds features incrementally, not monolithically.

**Step 2: Write another test for the next aspect**

```python
# Current test (passes)
def test_user_can_register():
    service = UserService()
    result = service.register("alice@example.com", "password")
    assert result.success == True

# Next test (new RED phase)
def test_user_cannot_register_with_invalid_email():
    """User registration fails when email is malformed"""
    service = UserService()
    result = service.register("not-an-email", "password")
    assert result.success == False
    assert result.error == "Invalid email format"
```

**Step 3: Return to RED phase for the next behavior**

**Step 4: Build incrementally**

Feature completion might take 10-20 RED-GREEN-REFACTOR cycles. That's normal.

### Prevention
- Embrace incremental development
- One test = one behavior
- Build features piece by piece
- Trust the process

---

## Test Passes on First Run

### Symptoms
- Wrote a new test
- Ran it for the first time
- Test passes immediately (no failure)

### Root Cause

**Either:**
- Code already implements this behavior (good)
- Test is broken and doesn't actually test anything (bad)

### Solution

**Step 1: Verify test is actually testing something**

```python
# Original test
def test_user_can_login():
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True
```

**Step 2: Temporarily break the code**

```python
def login(self, email, password):
    return LoginResult(authenticated=False)  # Intentionally wrong
```

**Step 3: Run test again**

```bash
pytest tests/test_user_service.py::test_user_can_login
# Expected: FAIL
# If still passes: Test is broken!
```

**Step 4: If test fails (good):**

```bash
# Revert the intentional break
git checkout src/user_service.py

# Test now passes again
pytest tests/test_user_service.py::test_user_can_login
# PASS
```

This means code already implements the behavior. Don't rewrite it. Move to next behavior.

**Step 5: If test still passes (bad):**

Test is broken. Fix it.

```python
# Broken test (always passes)
def test_user_can_login():
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")
    # Missing assertion! Test always passes!

# Fixed test
def test_user_can_login():
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True  # Now it actually tests
```

### Prevention
- Always run test before implementing
- Confirm test fails
- If test passes, investigate immediately
- Verify test has assertions
