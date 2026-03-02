---
name: op-refactor-code
description: REFACTOR phase - Improve code quality while keeping all tests passing
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Refactor Code (REFACTOR Phase)


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [The REFACTOR Phase Rule](#the-refactor-phase-rule)
- [Procedure](#procedure)
- [Refactoring Techniques](#refactoring-techniques)
- [Example: Python](#example-python)
- [Validation Checklist](#validation-checklist)
- [Common Mistakes](#common-mistakes)
- [When Tests Fail During Refactoring](#when-tests-fail-during-refactoring)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Improve the quality, readability, and design of the code while ensuring all tests continue to pass. Refactoring changes the structure of code without changing its behavior.

## When to Use

- After completing GREEN phase (test passes)
- When status is marked as `GREEN`
- When code has duplication, complexity, or poor naming
- Before starting the next RED phase

## Prerequisites

- All tests passing (status is `GREEN`)
- Implementation committed
- Clear understanding of what to improve

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| Production code | Code files | The GREEN phase implementation |
| Test suite | Test files | All tests that must remain passing |
| Improvement goals | List | What aspects to improve |

## Output

| Output Type | Description |
|-------------|-------------|
| Refactored code | Improved code structure |
| Test run result | ALL tests still passing |
| Git commit | Commit with "REFACTOR: improve [aspect]" message |
| Status update | Phase marked as `refactor` (cycle complete) |

## The REFACTOR Phase Rule

**Change structure, preserve behavior.**

You may:
- Rename variables, functions, classes
- Extract methods or functions
- Remove duplication
- Simplify logic
- Improve readability
- Add comments

You may NOT:
- Add new features
- Change behavior
- Break any tests

## Procedure

1. **Identify improvements**
   - Look for code smells (duplication, long methods, poor names)
   - Check for clarity and readability
   - Consider design patterns if applicable

2. **Make ONE change at a time**
   - Refactor in small steps
   - Run tests after each change
   - Commit or revert based on test results

3. **Run ALL tests after each change**
   - If tests pass: continue or commit
   - If tests fail: revert immediately

4. **Commit refactoring**
   - Stage refactored code
   - Commit with message: `REFACTOR: improve [aspect] in [feature]`

5. **Update status and complete cycle**
   - Mark status as `refactor`
   - Return to RED for next feature

## Refactoring Techniques

| Technique | When to Use | Example |
|-----------|-------------|---------|
| Rename | Poor naming | `x` -> `user_count` |
| Extract method | Long function | Break into smaller functions |
| Remove duplication | Repeated code | Create shared helper |
| Simplify conditional | Complex if/else | Use early returns |
| Extract constant | Magic numbers | `86400` -> `SECONDS_PER_DAY` |

## Example: Python

```python
# Before refactoring (GREEN phase code):
def authenticate_user(username, password):
    return AuthResult(is_authenticated=True, username=username)

# After refactoring:
def authenticate_user(username: str, password: str) -> AuthResult:
    """
    Authenticate a user with the given credentials.

    Args:
        username: The user's username
        password: The user's password

    Returns:
        AuthResult with authentication status
    """
    # TODO: Add actual password verification in next TDD cycle
    is_valid = _validate_credentials(username, password)
    return AuthResult(is_authenticated=is_valid, username=username)

def _validate_credentials(username: str, password: str) -> bool:
    """Validate user credentials. Currently always returns True."""
    # This will be properly implemented with its own failing test
    return True
```

```bash
# Run tests after refactoring
pytest -v

# All tests should still pass

# Commit the refactoring
git add src/auth.py
git commit -m "REFACTOR: add type hints and docstrings to authenticate_user"
```

## Validation Checklist

Before completing the cycle:

- [ ] All tests still pass after refactoring
- [ ] No new functionality added (only structure changed)
- [ ] Code is cleaner and more readable
- [ ] Refactoring is committed with "REFACTOR: ..." message
- [ ] Status is marked as `refactor`

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Adding features | Mixing phases | Features need failing tests first |
| Big refactoring steps | Risk of breaking | Small steps, test after each |
| Skipping tests | Unknown if broken | Always run tests |
| Changing behavior | Tests may pass but wrong | Only change structure |

## When Tests Fail During Refactoring

1. **STOP immediately**
2. **Revert to last GREEN state**
3. **Analyze what change broke it**
4. **Try smaller refactoring step**
5. **If refactoring is risky, skip it**

```bash
# If refactoring breaks tests:
git checkout -- src/auth.py
# Return to GREEN state
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Tests fail after refactoring | Revert immediately |
| Can't refactor without changing behavior | Need more tests first |
| Too much to refactor | Prioritize, do most important |

## Related Operations

- [op-implement-minimum-code.md](op-implement-minimum-code.md) - Previous phase (GREEN)
- [op-write-failing-test.md](op-write-failing-test.md) - Next cycle (RED)
- [op-verify-tdd-compliance.md](op-verify-tdd-compliance.md) - Verify discipline
