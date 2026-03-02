# Implementation Procedure Part 1: Writing Tests

## Table of Contents
- [Use-Case TOC](#use-case-toc)
- [Step 1: Understand the Requirement](#step-1-understand-the-requirement)
- [Step 2: Write the Failing Test](#step-2-write-the-failing-test)
  - [Test Structure Pattern](#test-structure-pattern)
  - [Test Naming Convention](#test-naming-convention)
  - [Writing the Test](#writing-the-test)
  - [Running the Test](#running-the-test)
  - [Commit the Failing Test](#commit-the-failing-test)

---

## Use-Case TOC
- When starting to implement a new feature → [Step 1: Understand the Requirement](#step-1-understand-the-requirement)
- If you need to write a failing test → [Step 2: Write the Failing Test](#step-2-write-the-failing-test)
- When you need test structure guidance → [Test Structure Pattern](#test-structure-pattern)

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

**Next:** [Part 2: Implementation and Refactoring](implementation-procedure-part2-implementation-refactor.md)
