# Implementation Procedure Part 2: Implementation and Refactoring

## Table of Contents
- [Use-Case TOC](#use-case-toc)
- [Step 3: Make the Test Pass](#step-3-make-the-test-pass)
  - [Minimum Implementation Rules](#minimum-implementation-rules)
  - [Implementation Example](#implementation-example)
  - [Run All Tests](#run-all-tests)
  - [Commit the Implementation](#commit-the-implementation)
- [Step 4: Refactor](#step-4-refactor)
  - [Refactoring Targets](#refactoring-targets)
  - [Refactoring Process](#refactoring-process)
  - [Refactored Example](#refactored-example)
  - [Commit Each Refactoring](#commit-each-refactoring)

---

## Use-Case TOC
- When you have a failing test and need to implement → [Step 3: Make the Test Pass](#step-3-make-the-test-pass)
- If tests pass and code needs improvement → [Step 4: Refactor](#step-4-refactor)

---

## Step 3: Make the Test Pass

Write production code to make the test pass.

### Minimum Implementation Rules

**Do:**
- Write ONLY the code needed to make the test pass
- Use the simplest solution that works
- Hardcode values if it makes the test pass
- Create minimal classes and methods

**Don't:**
- Add extra features not tested
- Write code for future requirements
- Refactor in this phase
- Add error handling not tested
- Implement edge cases not tested

### Implementation Example

**Python (Minimum Code):**

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

**JavaScript (Minimum Code):**

```javascript
class UserService {
    constructor() {
        this.users = {};
    }

    register(email, password) {
        this.users[email] = password;
    }

    login(email, password) {
        if (this.users[email] === password) {
            return {
                authenticated: true,
                user: { email: email }
            };
        }
        return { authenticated: false };
    }
}
```

**Java (Minimum Code):**

```java
public class UserService {
    private Map<String, String> users = new HashMap<>();

    public void register(String email, String password) {
        users.put(email, password);
    }

    public LoginResult login(String email, String password) {
        if (users.containsKey(email) && users.get(email).equals(password)) {
            return new LoginResult(true, new User(email));
        }
        return new LoginResult(false, null);
    }
}
```

### Run All Tests

```bash
# Python
pytest tests/

# JavaScript
npm test

# Java
mvn test
```

**Expected Result:**
```
All tests: PASS
```

### Commit the Implementation

```bash
git add src/user_service.py
git commit -m "GREEN: implement user login with valid credentials

- Implemented: UserService with login method
- Test: test_user_can_login_with_valid_credentials
- All tests: PASS"
```

**Mark status as: `GREEN`**

---

## Step 4: Refactor

Improve the code quality while maintaining behavior.

### Refactoring Targets

**Code Quality:**
- Remove duplication
- Improve variable and method names
- Simplify complex logic
- Extract magic numbers to constants

**Design Quality:**
- Extract methods for clarity
- Apply design patterns
- Separate concerns
- Reduce coupling

### Refactoring Process

**1. Identify improvement opportunities**
**2. Make ONE small change**
**3. Run tests**
**4. If tests pass → commit**
**5. If tests fail → revert**
**6. Repeat until satisfied**

### Refactored Example

**Python (Refactored):**

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

**JavaScript (Refactored):**

```javascript
class LoginResult {
    constructor(authenticated, user = null) {
        this.authenticated = authenticated;
        this.user = user;
    }
}

class User {
    constructor(email) {
        this.email = email;
    }
}

class UserService {
    constructor() {
        this.users = new Map(); // email -> hashedPassword
    }

    register(email, password) {
        const hashedPassword = this._hashPassword(password);
        this.users.set(email, hashedPassword);
    }

    login(email, password) {
        if (!this._userExists(email)) {
            return new LoginResult(false);
        }

        if (this._passwordMatches(email, password)) {
            const user = new User(email);
            return new LoginResult(true, user);
        }

        return new LoginResult(false);
    }

    _userExists(email) {
        return this.users.has(email);
    }

    _passwordMatches(email, password) {
        const storedPassword = this.users.get(email);
        return storedPassword === password; // In real code: use bcrypt
    }

    _hashPassword(password) {
        return password; // In real code: use bcrypt
    }
}
```

### Commit Each Refactoring

```bash
git add src/user_service.py
git commit -m "REFACTOR: extract LoginResult and User classes

- Changes: Extracted inline classes to proper class definitions
- Test: test_user_can_login_with_valid_credentials
- All tests: PASS"

git add src/user_service.py
git commit -m "REFACTOR: add helper methods for user validation

- Changes: Extracted _user_exists and _password_matches methods
- Test: test_user_can_login_with_valid_credentials
- All tests: PASS"
```

**Mark status as: `REFACTOR`**

---

**Previous:** [Part 1: Writing Tests](implementation-procedure-part1-writing-tests.md)
**Next:** [Part 3: Complete Example](implementation-procedure-part3-complete-example.md)
