# RED-GREEN-REFACTOR Cycle

## Table of Contents
- [Use-Case TOC](#use-case-toc)
- [Phase 1: RED (Write Failing Test)](#phase-1-red-write-failing-test)
- [Phase 2: GREEN (Write Minimum Implementation)](#phase-2-green-write-minimum-implementation)
- [Phase 3: REFACTOR (Improve Code Quality)](#phase-3-refactor-improve-code-quality)
- [Cycle Flow](#cycle-flow)
- [Cycle Completion](#cycle-completion)

---

## Use-Case TOC
- When starting a new feature → [Phase 1: RED](#phase-1-red-write-failing-test)
- If you have a failing test and need to implement → [Phase 2: GREEN](#phase-2-green-write-minimum-implementation)
- When all tests pass and code needs improvement → [Phase 3: REFACTOR](#phase-3-refactor-improve-code-quality)
- If you need to understand the complete cycle flow → [Cycle Flow](#cycle-flow)
- When completing one cycle and starting the next → [Cycle Completion](#cycle-completion)

---

## Phase 1: RED (Write Failing Test)

**Objective:** Create a test that documents the intended behavior and fails.

**Steps:**
1. Write a new test that specifies one aspect of the desired behavior
2. The test must be atomic: it tests one thing only
3. Run the test to confirm it fails
4. The failure message must be clear and specific
5. Commit this test (status: `pending`)

**Constraints:**
- No production code can be written in this phase
- The test must actually fail, not pass
- The test must be runnable and produce a measurable failure

**Status:** `RED` - test exists and fails, awaiting implementation

**Git Commit Message Format:**
```
RED: test for [feature name]

- Test: test_function_name
- Expected behavior: [brief description]
- Current result: FAIL
```

**Example RED Phase:**

Test file: `tests/test_user_service.py`
```python
def test_user_can_login_with_valid_credentials():
    """User can authenticate with correct username and password"""
    # Arrange
    user_service = UserService()
    user_service.register("alice@example.com", "secure_password")

    # Act
    result = user_service.login("alice@example.com", "secure_password")

    # Assert
    assert result.authenticated == True
    assert result.user.email == "alice@example.com"
```

Run test:
```bash
pytest tests/test_user_service.py::test_user_can_login_with_valid_credentials
# FAIL: NameError: name 'UserService' is not defined
```

Commit:
```bash
git add tests/test_user_service.py
git commit -m "RED: test for user login with valid credentials

- Test: test_user_can_login_with_valid_credentials
- Expected behavior: User can authenticate with correct credentials
- Current result: FAIL (UserService not defined)"
```

---

## Phase 2: GREEN (Write Minimum Implementation)

**Objective:** Write the minimum code necessary to make the test pass.

**Steps:**
1. Write production code that makes the failing test pass
2. The code must be the absolute minimum to satisfy the test
3. The code does not need to be elegant or complete
4. Run the test suite to confirm the previously failing test now passes
5. All other tests must continue to pass (no regressions)
6. Commit the implementation (status: `green`)

**Constraints:**
- Only write code that makes the specific test pass
- Do not write code for future features or edge cases
- No speculative code
- If tests fail, fix the code until tests pass
- Do not modify the test to make it pass

**Status:** `GREEN` - test passes, code is implemented

**Git Commit Message Format:**
```
GREEN: implement [feature name]

- Implemented: [brief description]
- Test: test_function_name
- All tests: PASS
```

**Example GREEN Phase:**

Production file: `src/user_service.py`
```python
class UserService:
    def __init__(self):
        self.users = {}

    def register(self, email, password):
        self.users[email] = password

    def login(self, email, password):
        if email in self.users and self.users[email] == password:
            class Result:
                authenticated = True
                user = type('User', (), {'email': email})()
            return Result()
        return None
```

Run test:
```bash
pytest tests/test_user_service.py::test_user_can_login_with_valid_credentials
# PASS
```

Commit:
```bash
git add src/user_service.py
git commit -m "GREEN: implement user login with valid credentials

- Implemented: UserService with login method
- Test: test_user_can_login_with_valid_credentials
- All tests: PASS"
```

---

## Phase 3: REFACTOR (Improve Code Quality)

**Objective:** Improve code quality, readability, and design without changing behavior.

**Steps:**
1. The test still passes from Phase 2
2. Improve code quality: remove duplication, improve naming, simplify logic
3. Improve design: extract methods, apply patterns, reduce complexity
4. Run tests after each change to ensure behavior is unchanged
5. If a test fails, revert the refactoring and try a different approach
6. Commit the refactored code (status: `refactor`)

**Constraints:**
- No new functionality can be added
- No test changes (except to improve clarity without changing assertion)
- Each refactoring change must pass all tests
- Must preserve the exact behavior the tests specify

**Status:** `REFACTOR` - code improved while maintaining all test assertions

**Git Commit Message Format:**
```
REFACTOR: improve [aspect] in [feature name]

- Changes: [brief description]
- Test: test_function_name
- All tests: PASS
```

**Example REFACTOR Phase:**

Production file: `src/user_service.py` (refactored)
```python
class LoginResult:
    def __init__(self, authenticated, user=None):
        self.authenticated = authenticated
        self.user = user

class User:
    def __init__(self, email):
        self.email = email

class UserService:
    def __init__(self):
        self.users = {}  # email -> hashed_password mapping

    def register(self, email, password):
        # In real code: use bcrypt or similar
        self.users[email] = self._hash_password(password)

    def login(self, email, password) -> LoginResult:
        if not self._user_exists(email):
            return LoginResult(authenticated=False)

        if self._password_matches(email, password):
            user = User(email)
            return LoginResult(authenticated=True, user=user)

        return LoginResult(authenticated=False)

    def _user_exists(self, email: str) -> bool:
        return email in self.users

    def _password_matches(self, email: str, password: str) -> bool:
        # In real code: use bcrypt or similar to verify
        return self.users[email] == password

    def _hash_password(self, password: str) -> str:
        # In real code: use bcrypt or similar
        return password
```

Run tests:
```bash
pytest tests/
# All tests: PASS
```

Commit:
```bash
git add src/user_service.py
git commit -m "REFACTOR: improve code structure in user login

- Changes: Extracted Result and User classes, added helper methods
- Test: test_user_can_login_with_valid_credentials
- All tests: PASS"
```

---

## Cycle Flow

```
┌─────────────────────────────────────┐
│  START: New Feature Requirement     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  1. RED: Write Failing Test         │
│  - Understand requirement           │
│  - Write test that fails            │
│  - Commit with "RED: ..." message   │
│  - Status: RED                      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  2. GREEN: Implement Minimum Code   │
│  - Write production code            │
│  - Make test pass                   │
│  - All tests pass                   │
│  - Commit with "GREEN: ..." message │
│  - Status: GREEN                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  3. REFACTOR: Improve Code          │
│  - Enhance quality                  │
│  - Maintain behavior                │
│  - All tests still pass             │
│  - Commit with "REFACTOR: ..."      │
│  - Status: REFACTOR                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Decision: More features?           │
│  YES → Return to step 1 (RED)       │
│  NO → Complete                      │
└─────────────────────────────────────┘
```

---

## Cycle Completion

After completing one RED-GREEN-REFACTOR cycle:

1. All tests pass
2. Code quality is improved
3. Behavior is documented by tests
4. Git history shows clear RED → GREEN → REFACTOR sequence
5. Status tracking updated
6. Return to Phase 1 to implement the next feature

**Verification Checklist:**
- [ ] All tests pass
- [ ] Code meets quality standards
- [ ] No untested production code exists
- [ ] Git history shows proper TDD sequence
- [ ] Status tracking is updated
- [ ] Ready for next feature
