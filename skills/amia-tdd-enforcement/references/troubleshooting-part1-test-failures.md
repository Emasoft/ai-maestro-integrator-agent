# TDD Troubleshooting - Part 1: Test Failures

## Table of Contents
- [Test Fails During Refactoring](#test-fails-during-refactoring)
  - [Symptoms](#symptoms)
  - [Root Cause](#root-cause)
  - [Solution](#solution)
  - [Prevention](#prevention)
- [Cannot Write a Failing Test](#cannot-write-a-failing-test)
  - [Symptoms](#symptoms-1)
  - [Root Cause](#root-cause-1)
  - [Solution](#solution-1)
  - [Prevention](#prevention-1)

---

## Test Fails During Refactoring

### Symptoms
- Test passed before refactoring
- Made a refactoring change
- Test now fails
- All other tests still pass

### Root Cause
Refactoring changed behavior instead of just improving code structure.

### Solution

**Step 1: Immediately revert the refactoring change**
```bash
# Undo the change
git checkout .

# Or if you committed
git revert HEAD
```

**Step 2: Verify tests pass again**
```bash
pytest tests/
# All tests: PASS
```

**Step 3: Commit the test-passing state**
```bash
git add .
git commit -m "REFACTOR: reverted unsafe change, tests passing"
```

**Step 4: Try a different, smaller refactoring**
```python
# Instead of:
# - Moving method AND renaming AND changing logic
# Do:
# - Just move the method (run tests)
# - Then rename (run tests)
# - Then simplify logic (run tests)
```

**Step 5: Run tests after EACH micro-change**
```bash
# After each line of refactoring
pytest tests/
```

### Prevention
- Make tiny refactoring changes
- Run tests after each change
- Commit each successful refactoring
- Never batch refactorings

---

## Cannot Write a Failing Test

### Symptoms
- Requirement is clear
- But can't figure out how to write a test
- Test is too complex
- Test covers too much

### Root Cause
The requirement is too vague or too large to test in one cycle.

### Solution

**Step 1: Break requirement into smaller behaviors**

**Too large:**
```
Requirement: "User authentication system"
```

**Broken down:**
```
1. User can register with email and password
2. User can login with valid credentials
3. User cannot login with wrong password
4. User cannot login with non-existent email
5. User can logout
6. User session persists for 24 hours
7. User password is hashed
8. User can reset password
```

**Step 2: Write test for the smallest behavior**

```python
def test_user_can_register_with_email_and_password():
    """User can create account with email and password"""
    service = UserService()
    result = service.register("alice@example.com", "password123")
    assert result.success == True
```

**Step 3: Verify the test fails**
```bash
pytest tests/test_user_service.py::test_user_can_register_with_email_and_password
# FAIL: NameError: name 'UserService' is not defined
```

**Step 4: If test doesn't fail...**

The code already implements this behavior. Either:

**A) Don't rewrite it:**
```markdown
- Behavior already works
- Move to next behavior
```

**B) Write a different test that DOES fail:**
```python
def test_user_cannot_register_with_duplicate_email():
    """User cannot register with an email that's already taken"""
    service = UserService()
    service.register("alice@example.com", "password123")
    result = service.register("alice@example.com", "password456")
    assert result.success == False
    assert result.error == "Email already registered"
```

### Prevention
- Start with the smallest possible behavior
- Ask: "What is the ONE thing this should do?"
- Ignore edge cases initially
- Build incrementally
