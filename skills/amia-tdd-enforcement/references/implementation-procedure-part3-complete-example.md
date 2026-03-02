# Implementation Procedure Part 3: Complete Example

## Use-Case TOC
- When you need a complete RED-GREEN-REFACTOR walkthrough → [Complete Procedure Example](#complete-procedure-example)

---

## Complete Procedure Example

**Feature:** User can login with valid credentials

### RED Phase

**1. Write test:**
```python
def test_user_can_login_with_valid_credentials():
    user_service = UserService()
    user_service.register("alice@example.com", "password")
    result = user_service.login("alice@example.com", "password")
    assert result.authenticated == True
```

**2. Run test:**
```
FAIL: NameError: name 'UserService' is not defined
```

**3. Commit:**
```bash
git commit -m "RED: test for user login with valid credentials"
```

### GREEN Phase

**4. Write minimum code:**
```python
class UserService:
    def __init__(self):
        self.users = {}

    def register(self, email, password):
        self.users[email] = password

    def login(self, email, password):
        if self.users.get(email) == password:
            return type('Result', (), {'authenticated': True})()
```

**5. Run tests:**
```
All tests: PASS
```

**6. Commit:**
```bash
git commit -m "GREEN: implement user login with valid credentials"
```

### REFACTOR Phase

**7. Improve code:**
```python
class LoginResult:
    def __init__(self, authenticated):
        self.authenticated = authenticated

class UserService:
    def __init__(self):
        self.users = {}

    def register(self, email, password):
        self.users[email] = password

    def login(self, email, password) -> LoginResult:
        authenticated = self.users.get(email) == password
        return LoginResult(authenticated)
```

**8. Run tests:**
```
All tests: PASS
```

**9. Commit:**
```bash
git commit -m "REFACTOR: extract LoginResult class"
```

**10. Return to RED phase for next behavior**

---

**Previous:** [Part 2: Implementation and Refactoring](implementation-procedure-part2-implementation-refactor.md)
