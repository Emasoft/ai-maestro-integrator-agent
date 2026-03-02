# Common TDD Patterns and Anti-Patterns

## Table of Contents
- [Use-Case TOC](#use-case-toc)
- [Testing Behavior, Not Implementation](#testing-behavior-not-implementation)
  - [The Rule](#the-rule)
  - [Anti-Pattern: Testing Implementation](#anti-pattern-testing-implementation)
  - [Correct Pattern: Testing Behavior](#correct-pattern-testing-behavior)
  - [More Examples](#more-examples)
- [One Assertion Per Test](#one-assertion-per-test)
  - [The Rule](#the-rule-1)
  - [Anti-Pattern: Multiple Behaviors in One Test](#anti-pattern-multiple-behaviors-in-one-test)
  - [Correct Pattern: One Test Per Behavior](#correct-pattern-one-test-per-behavior)
  - [When Multiple Assertions Are OK](#when-multiple-assertions-are-ok)
- [Arrange-Act-Assert Pattern](#arrange-act-assert-pattern)
  - [The Rule](#the-rule-2)
  - [Pattern Structure](#pattern-structure)
  - [Example](#example)
  - [Anti-Pattern: Mixed Phases](#anti-pattern-mixed-phases)
- [Edge Case Testing](#edge-case-testing)
  - [The Rule](#the-rule-3)
  - [Pattern](#pattern)
  - [Anti-Pattern: All Edge Cases at Once](#anti-pattern-all-edge-cases-at-once)
- [Dependency Isolation](#dependency-isolation)
  - [The Rule](#the-rule-4)
  - [Anti-Pattern: Shared State](#anti-pattern-shared-state)
  - [Correct Pattern: Independent Tests](#correct-pattern-independent-tests)
  - [Using Setup Methods](#using-setup-methods)
- [Test Naming Patterns](#test-naming-patterns)
  - [The Rule](#the-rule-5)
  - [Pattern: Given-When-Then](#pattern-given-when-then)
  - [Pattern: Should](#pattern-should)
  - [Pattern: Can/Cannot](#pattern-cancannot)

---

## Use-Case TOC
- When you need to understand what to test → [Testing Behavior Not Implementation](#testing-behavior-not-implementation)
- If your test has multiple assertions → [One Assertion Per Test](#one-assertion-per-test)
- When structuring test code → [Arrange-Act-Assert Pattern](#arrange-act-assert-pattern)
- If you need to test edge cases → [Edge Case Testing](#edge-case-testing)
- When dealing with dependencies → [Dependency Isolation](#dependency-isolation)

---

## Testing Behavior, Not Implementation

### The Rule

Tests should verify **what** the code does, not **how** it does it.

### Anti-Pattern: Testing Implementation

**Wrong (testing internal structure):**
```python
def test_user_service_uses_dict():
    """User service should use a dictionary"""
    service = UserService()
    assert isinstance(service.users, dict)
```

**Why it's wrong:**
- Couples test to implementation detail
- Breaks when refactoring from dict to database
- Doesn't verify actual behavior
- Provides no value to users

### Correct Pattern: Testing Behavior

**Right (testing observable behavior):**
```python
def test_user_can_register_and_login():
    """User registration enables subsequent login"""
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True
```

**Why it's right:**
- Tests user-facing behavior
- Survives refactoring (dict → database)
- Verifies actual value
- Documents expected behavior

### More Examples

**Wrong (implementation):**
```python
def test_login_calls_hash_function():
    """Login should call password hashing"""
    service = UserService()
    with mock.patch.object(service, '_hash_password') as mock_hash:
        service.login("alice@example.com", "password")
        mock_hash.assert_called_once()
```

**Right (behavior):**
```python
def test_login_rejects_wrong_password():
    """Login fails when password doesn't match"""
    service = UserService()
    service.register("alice@example.com", "correct_password")
    result = service.login("alice@example.com", "wrong_password")
    assert result.authenticated == False
```

---

## One Assertion Per Test

### The Rule

Each test should verify ONE behavior. Multiple assertions are allowed if they all verify the same behavior.

### Anti-Pattern: Multiple Behaviors in One Test

**Wrong (testing multiple behaviors):**
```python
def test_user_creation():
    user = User("alice", "alice@example.com")
    assert user.name == "alice"
    assert user.email == "alice@example.com"
    assert user.created_at is not None
    assert user.active == True
    assert user.role == "member"
```

**Why it's wrong:**
- If first assertion fails, you don't see other failures
- Hard to identify which behavior broke
- Difficult to maintain
- Violates Single Responsibility Principle

### Correct Pattern: One Test Per Behavior

**Right (one test per behavior):**
```python
def test_user_has_correct_name():
    """User is created with the specified name"""
    user = User("alice", "alice@example.com")
    assert user.name == "alice"

def test_user_has_correct_email():
    """User is created with the specified email"""
    user = User("alice", "alice@example.com")
    assert user.email == "alice@example.com"

def test_user_creation_sets_timestamp():
    """User has a creation timestamp when created"""
    user = User("alice", "alice@example.com")
    assert user.created_at is not None

def test_new_user_is_active_by_default():
    """New users are active by default"""
    user = User("alice", "alice@example.com")
    assert user.active == True

def test_new_user_has_member_role():
    """New users have member role by default"""
    user = User("alice", "alice@example.com")
    assert user.role == "member"
```

**Why it's right:**
- Each test documents one specific behavior
- Failures are immediately clear
- Easy to maintain
- Can be run independently

### When Multiple Assertions Are OK

Multiple assertions are acceptable when they verify the **same behavior**:

```python
def test_login_returns_complete_user_data():
    """Successful login returns authenticated result with user data"""
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")

    # All these assertions verify ONE behavior: "complete user data returned"
    assert result.authenticated == True
    assert result.user is not None
    assert result.user.email == "alice@example.com"
```

---

## Arrange-Act-Assert Pattern

### The Rule

Structure all tests using the AAA pattern for clarity.

### Pattern Structure

```python
def test_behavior_description():
    """Clear description of behavior"""
    # Arrange: Set up test data and conditions
    # Act: Execute the code being tested
    # Assert: Verify the result
```

### Example

```python
def test_user_can_change_password():
    """User can update their password to a new value"""
    # Arrange
    service = UserService()
    service.register("alice@example.com", "old_password")

    # Act
    service.change_password("alice@example.com", "old_password", "new_password")

    # Assert
    result = service.login("alice@example.com", "new_password")
    assert result.authenticated == True
```

### Anti-Pattern: Mixed Phases

**Wrong (mixed arrange/act/assert):**
```python
def test_user_operations():
    service = UserService()  # Arrange
    service.register("alice@example.com", "password")  # Act
    result = service.login("alice@example.com", "password")  # Act
    assert result.authenticated == True  # Assert
    service.logout("alice@example.com")  # Act
    result2 = service.is_logged_in("alice@example.com")  # Act
    assert result2 == False  # Assert
```

**Why it's wrong:**
- Tests multiple behaviors
- Hard to understand what's being tested
- Difficult to debug when it fails

---

## Edge Case Testing

### The Rule

Each edge case gets its own RED-GREEN-REFACTOR cycle.

### Pattern

**1. Happy path first:**
```python
def test_user_can_login_with_valid_credentials():
    """User can login with correct email and password"""
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True
```

**2. Then edge cases (one at a time):**
```python
def test_login_rejects_wrong_password():
    """Login fails when password is incorrect"""
    service = UserService()
    service.register("alice@example.com", "correct_password")
    result = service.login("alice@example.com", "wrong_password")
    assert result.authenticated == False

def test_login_rejects_nonexistent_email():
    """Login fails when email is not registered"""
    service = UserService()
    result = service.login("nonexistent@example.com", "password")
    assert result.authenticated == False

def test_login_rejects_empty_email():
    """Login fails when email is empty"""
    service = UserService()
    result = service.login("", "password")
    assert result.authenticated == False

def test_login_rejects_empty_password():
    """Login fails when password is empty"""
    service = UserService()
    service.register("alice@example.com", "password")
    result = service.login("alice@example.com", "")
    assert result.authenticated == False
```

### Anti-Pattern: All Edge Cases at Once

**Wrong:**
```python
def test_login_validation():
    """Test all login validation cases"""
    service = UserService()
    service.register("alice@example.com", "password")

    # Wrong: testing multiple edge cases in one test
    assert service.login("", "password").authenticated == False
    assert service.login("alice@example.com", "").authenticated == False
    assert service.login("wrong@example.com", "password").authenticated == False
    assert service.login("alice@example.com", "wrong").authenticated == False
```

---

## Dependency Isolation

### The Rule

Tests should be independent. One test's outcome should not affect another.

### Anti-Pattern: Shared State

**Wrong (tests share state):**
```python
# Global shared service
service = UserService()

def test_user_can_register():
    service.register("alice@example.com", "password")
    assert service.has_user("alice@example.com")

def test_user_can_login():
    # Depends on previous test having run first!
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True
```

**Why it's wrong:**
- Tests can't run in isolation
- Order matters (fragile)
- One test failure affects others
- Hard to debug

### Correct Pattern: Independent Tests

**Right (each test is independent):**
```python
def test_user_can_register():
    """User registration creates a new account"""
    service = UserService()  # Fresh instance
    service.register("alice@example.com", "password")
    assert service.has_user("alice@example.com")

def test_user_can_login():
    """User can login after registering"""
    service = UserService()  # Fresh instance
    service.register("alice@example.com", "password")  # Setup for this test
    result = service.login("alice@example.com", "password")
    assert result.authenticated == True
```

**Why it's right:**
- Each test stands alone
- Can run in any order
- Can run in parallel
- Easy to debug

### Using Setup Methods

**Python (unittest):**
```python
class TestUserService(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        self.service = UserService()

    def test_user_can_register(self):
        self.service.register("alice@example.com", "password")
        assert self.service.has_user("alice@example.com")

    def test_user_can_login(self):
        self.service.register("alice@example.com", "password")
        result = self.service.login("alice@example.com", "password")
        assert result.authenticated == True
```

**JavaScript (Jest):**
```javascript
describe('UserService', () => {
    let service;

    beforeEach(() => {
        service = new UserService();
    });

    test('user can register', () => {
        service.register('alice@example.com', 'password');
        expect(service.hasUser('alice@example.com')).toBe(true);
    });

    test('user can login', () => {
        service.register('alice@example.com', 'password');
        const result = service.login('alice@example.com', 'password');
        expect(result.authenticated).toBe(true);
    });
});
```

---

## Test Naming Patterns

### The Rule

Test names should describe the behavior being tested.

### Pattern: Given-When-Then

```python
def test_given_valid_credentials_when_login_then_authenticated():
    """Given valid credentials, when user logs in, then they are authenticated"""
    # ...

def test_given_wrong_password_when_login_then_not_authenticated():
    """Given wrong password, when user logs in, then they are not authenticated"""
    # ...
```

### Pattern: Should

```python
def test_should_authenticate_user_with_valid_credentials():
    """Should authenticate user with valid credentials"""
    # ...

def test_should_reject_authentication_with_wrong_password():
    """Should reject authentication with wrong password"""
    # ...
```

### Pattern: Can/Cannot

```python
def test_user_can_login_with_valid_credentials():
    """User can login with valid credentials"""
    # ...

def test_user_cannot_login_with_wrong_password():
    """User cannot login with wrong password"""
    # ...
```

Choose one pattern and use it consistently.
