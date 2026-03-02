---
name: op-implement-minimum-code
description: GREEN phase - Write minimum code to make the failing test pass
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Implement Minimum Code (GREEN Phase)


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [The GREEN Phase Rule](#the-green-phase-rule)
- [Procedure](#procedure)
- [Example: Python](#example-python)
- [Minimum Code Guidelines](#minimum-code-guidelines)
- [Validation Checklist](#validation-checklist)
- [Common Mistakes](#common-mistakes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Write the minimum amount of production code necessary to make the failing test pass. No more, no less. The goal is to make the test green as quickly as possible.

## When to Use

- After completing RED phase (failing test exists)
- When status is marked as `RED`
- After test failure has been committed

## Prerequisites

- Failing test exists and is committed
- Test failure message is clear
- Status is `RED`

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| Failing test | Test file | The RED phase test that needs to pass |
| Failure message | Text | What the test expects |
| Implementation location | Path | Where to write the code |

## Output

| Output Type | Description |
|-------------|-------------|
| Production code | Minimum code to pass the test |
| Test run result | ALL tests passing (green) |
| Git commit | Commit with "GREEN: implement [feature]" message |
| Status update | Phase marked as `GREEN` |

## The GREEN Phase Rule

**Write ONLY the code necessary to make the test pass.**

Do not:
- Add features not tested
- Optimize prematurely
- Refactor during GREEN (that's next phase)
- Write more code than needed

## Procedure

1. **Read the failing test**
   - Understand what it expects
   - Identify the function/class/method signature needed
   - Note the expected return value or behavior

2. **Write minimum implementation**
   - Create the function/class/method
   - Implement just enough to pass the test
   - Hardcode values if necessary (refactor later)

3. **Run ALL tests**
   - Execute the entire test suite
   - Verify the new test passes
   - Verify no existing tests broke

4. **Commit the implementation**
   - Stage the production code
   - Commit with message: `GREEN: implement [feature description]`

5. **Update status**
   - Mark status as `GREEN`
   - Proceed to REFACTOR phase

## Example: Python

```python
# From RED phase, we have this failing test:
# def test_authenticate_user_with_valid_credentials():
#     result = authenticate_user("testuser", "validpassword")
#     assert result.is_authenticated is True

# GREEN phase implementation (minimum code):
# src/auth.py

class AuthResult:
    def __init__(self, is_authenticated, username):
        self.is_authenticated = is_authenticated
        self.username = username

def authenticate_user(username, password):
    # Minimum implementation to pass the test
    # (will be improved in REFACTOR phase)
    return AuthResult(is_authenticated=True, username=username)
```

```bash
# Run tests - should PASS now
pytest tests/test_user_auth.py -v

# Expected output:
# PASSED test_authenticate_user_with_valid_credentials

# Run ALL tests to ensure nothing broke
pytest -v

# Commit the implementation
git add src/auth.py
git commit -m "GREEN: implement user authentication"
```

## Minimum Code Guidelines

| Guideline | Example |
|-----------|---------|
| If test expects True, return True | `return True` |
| If test expects specific value, return it | `return "expected"` |
| If test expects calculation, do minimum | Simple formula only |
| If hardcoding works, hardcode | Refactor generalizes later |

## Validation Checklist

Before moving to REFACTOR phase:

- [ ] Implementation makes the failing test pass
- [ ] ALL existing tests still pass
- [ ] No extra code beyond what test requires
- [ ] Implementation is committed with "GREEN: ..." message
- [ ] Status is marked as `GREEN`

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Over-engineering | Adding untested features | Only write what test requires |
| Refactoring during GREEN | Mixing phases | Save refactoring for next phase |
| Breaking other tests | Unintended side effects | Run full test suite before commit |
| Skipping commit | Losing checkpoint | Always commit at GREEN |

## Error Handling

| Scenario | Action |
|----------|--------|
| Test still fails | Re-read test expectations, fix implementation |
| Other tests break | Revert, understand dependencies, try again |
| Implementation too complex | Break into smaller tests/implementations |

## Related Operations

- [op-write-failing-test.md](op-write-failing-test.md) - Previous phase (RED)
- [op-refactor-code.md](op-refactor-code.md) - Next phase (REFACTOR)
- [op-verify-tdd-compliance.md](op-verify-tdd-compliance.md) - Verify discipline
