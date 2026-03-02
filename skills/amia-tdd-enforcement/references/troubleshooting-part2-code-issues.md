# TDD Troubleshooting - Part 2: Code Issues

## Table of Contents
- [Code Passes But Seems Wrong](#code-passes-but-seems-wrong)
  - [Symptoms](#symptoms)
  - [Root Cause](#root-cause)
  - [Solution](#solution)
  - [Prevention](#prevention)
- [Refactoring Takes Too Long](#refactoring-takes-too-long)
  - [Symptoms](#symptoms-1)
  - [Root Cause](#root-cause-1)
  - [Solution](#solution-1)
  - [Prevention](#prevention-1)

---

## Code Passes But Seems Wrong

### Symptoms
- Test passes
- All assertions succeed
- But code seems incorrect/incomplete/buggy

### Root Cause
The test does not fully specify the intended behavior.

### Solution

**Step 1: Do NOT modify the implementation**

The code passes the test = it meets the specification = it is correct.

**Step 2: Write a NEW test that catches the issue**

**Example:**

Current test:
```python
def test_user_can_login():
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True
```

Current code:
```python
def login(self, email, password):
    # BUG: Always returns True (but test passes!)
    return LoginResult(authenticated=True)
```

Issue: Login accepts ANY password, but test only checks the happy path.

**Step 3: New test (RED phase)**

```python
def test_user_cannot_login_with_wrong_password():
    """Login fails when password is incorrect"""
    service = UserService()
    service.register("alice@example.com", "correct_password")
    result = service.login("alice@example.com", "wrong_password")
    assert result.authenticated == False  # This will FAIL
```

**Step 4: Run new test to verify it fails**
```bash
pytest tests/test_user_service.py::test_user_cannot_login_with_wrong_password
# FAIL: Expected False, got True
```

**Step 5: Modify implementation to pass BOTH tests (GREEN phase)**

```python
def login(self, email, password):
    if email in self.users and self.users[email] == password:
        return LoginResult(authenticated=True)
    return LoginResult(authenticated=False)
```

**Step 6: Run all tests**
```bash
pytest tests/
# All tests: PASS
```

### Prevention
- Think about what could go wrong
- Write tests for negative cases
- Write tests for edge cases
- One test per behavior (including failure cases)

---

## Refactoring Takes Too Long

### Symptoms
- Spent 30+ minutes refactoring
- Still not satisfied with code
- Many changes made
- Afraid to commit

### Root Cause
Trying to refactor too much code at once.

### Solution

**Step 1: Commit current refactored state (if tests pass)**

```bash
pytest tests/
# All tests: PASS

git add .
git commit -m "REFACTOR: improved method names and extracted helper"
```

**Step 2: Move to next feature (new RED phase)**

Don't try to perfect the code now. Build more features.

**Step 3: Return to refactor this code in a future cycle if needed**

After implementing more features, patterns will emerge.

**Step 4: Make smaller refactoring changes**

Instead of:
- "Refactor entire UserService class"

Do:
- "Extract email validation method" (5 min)
- "Rename _hash_password to _hash_password_bcrypt" (2 min)
- "Extract User class" (10 min)

### Prevention
- Set a 10-15 minute timer for REFACTOR phase
- When timer expires, commit and move on
- Small, frequent refactorings > large, rare ones
- Perfect is the enemy of good
