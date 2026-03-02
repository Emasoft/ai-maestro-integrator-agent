# Implementation Procedure Part 1: Test Creation

## Table of Contents

- [Step 1: Understand the Requirement](#step-1-understand-the-requirement) - When starting to implement a new feature
- [Step 2: Write the Failing Test](#step-2-write-the-failing-test) - If you need to write a failing test
  - [Test Structure Pattern](#test-structure-pattern) - When you need test structure guidance
  - [Test Naming Convention](#test-naming-convention) - How to name tests properly
  - [Writing the Test](#writing-the-test) - Examples in Python, JavaScript, Java
  - [Running the Test](#running-the-test) - How to verify test fails
  - [Commit the Failing Test](#commit-the-failing-test) - RED phase commit
- [Step 3: Make the Test Pass](#step-3-make-the-test-pass) - When you have a failing test and need to implement
  - [Minimum Implementation Rules](#minimum-implementation-rules) - What to do and avoid
  - [Implementation Example](#implementation-example) - Minimum code examples
  - [Run All Tests](#run-all-tests) - Verify implementation works
  - [Commit the Implementation](#commit-the-implementation) - GREEN phase commit

---

## Step 1: Understand the Requirement

Before writing any code or test:

**Questions to Answer:**
1. What is the single behavior to implement?
2. What are the input conditions?
3. What is the expected output or behavior?
4. What constraints or edge cases exist for this specific feature?

**Process:**
1. Read the requirement carefully
2. Identify ONE behavior to implement
3. Break down complex requirements into smaller behaviors
4. Write down expected inputs and outputs
5. List any constraints or validations

**Example:**

Requirement: "Users should be able to log in with email and password"

Analysis:
- **Behavior:** User authentication with credentials
- **Input:** Email (string), Password (string)
- **Output:** LoginResult (authenticated: bool, user: User)
- **Constraints:** Email must exist, password must match

**Decomposition:**
1. User can login with valid credentials (valid email + matching password)
2. User cannot login with invalid email (email doesn't exist)
3. User cannot login with wrong password (email exists, password mismatch)
4. User cannot login with empty email
5. User cannot login with empty password

Each of these becomes ONE RED-GREEN-REFACTOR cycle.

---

## Step 2: Write the Failing Test

Create a test file following your language conventions.

### Test Structure Pattern

All tests must follow the **Arrange-Act-Assert** pattern:

```python
def test_behavior_description():
    """Clear description of what behavior is tested"""
    # Arrange: Set up test data and conditions
    # Act: Call the code being tested
    # Assert: Verify the result matches expectation
```

### Test Naming Convention

Test names must clearly describe what is being tested:

**Format:** `test_[subject]_[action]_[condition]`

**Examples:**
- `test_user_can_login_with_valid_credentials`
- `test_user_cannot_login_with_invalid_email`
- `test_user_cannot_login_with_wrong_password`
- `test_email_validation_rejects_malformed_email`

### Writing the Test

**Example (Python):**

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

**Example (JavaScript):**

```javascript
test('user can login with valid credentials', () => {
    // Arrange
    const userService = new UserService();
    userService.register('alice@example.com', 'secure_password');

    // Act
    const result = userService.login('alice@example.com', 'secure_password');

    // Assert
    expect(result.authenticated).toBe(true);
    expect(result.user.email).toBe('alice@example.com');
});
```

**Example (Java):**

```java
@Test
public void testUserCanLoginWithValidCredentials() {
    // Arrange
    UserService userService = new UserService();
    userService.register("alice@example.com", "secure_password");

    // Act
    LoginResult result = userService.login("alice@example.com", "secure_password");

    // Assert
    assertTrue(result.isAuthenticated());
    assertEquals("alice@example.com", result.getUser().getEmail());
}
```

### Running the Test

**Run the test to confirm it fails:**

```bash
# Python
pytest tests/test_user_service.py::test_user_can_login_with_valid_credentials

# JavaScript
npm test -- test_user_service.test.js

# Java
mvn test -Dtest=UserServiceTest#testUserCanLoginWithValidCredentials
```

**Expected Result:**
```
FAIL: NameError: name 'UserService' is not defined
```
or
```
FAIL: Cannot find module 'UserService'
```
or
```
FAIL: UserService cannot be resolved to a type
```

### Commit the Failing Test

```bash
git add tests/test_user_service.py
git commit -m "RED: test for user login with valid credentials

- Test: test_user_can_login_with_valid_credentials
- Expected behavior: User can authenticate with correct credentials
- Current result: FAIL (UserService not defined)"
```

**Mark status as: `RED`**

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

## Next Steps

After completing the GREEN phase, proceed to:
- [Part 2: Implementation & Refactoring](implementation-procedure-part2-implementation-refactor.md) - Step 4 (Refactor) and Complete Procedure Example
