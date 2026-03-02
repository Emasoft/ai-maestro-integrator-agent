# TDD Troubleshooting - Part 4: Workflow Issues

## Table of Contents
- [Unsure What to Test Next](#unsure-what-to-test-next)
  - [Symptoms](#symptoms)
  - [Solution](#solution)
  - [Prevention](#prevention)
- [Tests Are Too Slow](#tests-are-too-slow)
  - [Symptoms](#symptoms-1)
  - [Solution](#solution-1)
  - [Prevention](#prevention-1)

---

## Unsure What to Test Next

### Symptoms
- Completed current cycle
- Not sure what behavior to implement next
- Many possible options

### Solution

**Step 1: List all remaining behaviors**

```markdown
## User Authentication - Remaining Behaviors

- [ ] User can login with valid credentials
- [ ] User cannot login with wrong password
- [ ] User cannot login with non-existent email
- [ ] User cannot login with empty email
- [ ] User cannot login with empty password
- [ ] User can logout
- [ ] User session persists
- [ ] Password is hashed
```

**Step 2: Choose the next most important behavior**

Priority order:
1. **Happy path** (if not done): Most common use case
2. **Critical failures**: Security, data loss prevention
3. **Common edge cases**: Empty inputs, nulls
4. **Rare edge cases**: Unusual conditions

**Step 3: Write test for that behavior (RED phase)**

**Step 4: If still unsure, ask:**

- "What would break the system if missing?"
- "What do users do most often?"
- "What could go wrong?"
- "What would I manually test?"

### Prevention
- Maintain a backlog of behaviors
- Prioritize before starting TDD
- Focus on value, not coverage
- Build incrementally

---

## Tests Are Too Slow

### Symptoms
- Test suite takes minutes to run
- Slows down RED-GREEN-REFACTOR cycle
- Hesitant to run tests frequently

### Solution

**Step 1: Measure test execution time**

```bash
pytest tests/ --durations=10
# Shows 10 slowest tests
```

**Step 2: Identify slow tests**

Common causes:
- Database operations
- Network calls
- File I/O
- Sleep/wait calls

**Step 3: Optimize slow tests**

**Strategy A: Use test doubles**

```python
# Slow (real database)
def test_user_can_register():
    db = Database(connection_string)  # Slow!
    service = UserService(db)
    service.register("alice@example.com", "password")
    user = db.find_user("alice@example.com")
    assert user is not None

# Fast (in-memory)
def test_user_can_register():
    db = InMemoryDatabase()  # Fast!
    service = UserService(db)
    service.register("alice@example.com", "password")
    user = db.find_user("alice@example.com")
    assert user is not None
```

**Strategy B: Separate unit and integration tests**

```bash
# Fast unit tests (run frequently)
pytest tests/unit/

# Slow integration tests (run before commit)
pytest tests/integration/
```

**Step 4: Run subset of tests during development**

```bash
# Run only tests for current feature
pytest tests/test_user_service.py

# Run all tests before commit
pytest tests/
```

### Prevention
- Keep unit tests fast (<100ms each)
- Use in-memory databases for tests
- Use test doubles (in-memory implementations) for external services
- Run slow tests less frequently
