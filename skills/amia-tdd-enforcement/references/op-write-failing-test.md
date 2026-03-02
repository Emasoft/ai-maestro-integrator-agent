---
name: op-write-failing-test
description: RED phase - Write a failing test before implementing any production code
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Write Failing Test (RED Phase)


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [The Iron Law](#the-iron-law)
- [Procedure](#procedure)
- [Test Structure Pattern](#test-structure-pattern)
- [Example: Python (pytest)](#example-python-pytest)
- [Validation Checklist](#validation-checklist)
- [Common Mistakes](#common-mistakes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Create a test that documents the intended behavior of code that does not yet exist. This test MUST fail initially, confirming that the feature is not implemented.

## When to Use

- Starting implementation of any new feature
- Adding new functionality to existing code
- Fixing a bug (write test that reproduces the bug first)
- Beginning any TDD cycle

## Prerequisites

- Clear understanding of the requirement
- Test framework configured (pytest, Jest, cargo test, etc.)
- Git repository for tracking commits

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| Feature requirement | Text | What the code should do |
| Expected behavior | Text | How the code should behave |
| Test framework | String | pytest, Jest, cargo test, go test, etc. |

## Output

| Output Type | Description |
|-------------|-------------|
| Test file | New or updated test file with failing test |
| Test run result | Test execution showing FAILURE |
| Git commit | Commit with "RED: test for [feature]" message |
| Status update | Phase marked as `RED` |

## The Iron Law

**No production code may be written without a failing test that justifies its existence.**

This is the absolute rule of TDD. If you write production code without a failing test first, you are violating TDD discipline.

## Procedure

1. **Understand the requirement**
   - What should the code do?
   - What are the inputs and expected outputs?
   - What edge cases exist?

2. **Write the test**
   - Create test that calls the code that will exist
   - Assert the expected behavior
   - Use clear, descriptive test name

3. **Run the test**
   - Execute the test
   - Verify it FAILS (not passes, not errors - FAILS)
   - The failure message should be clear

4. **Commit the failing test**
   - Stage the test file
   - Commit with message: `RED: test for [feature description]`

5. **Update status**
   - Mark status as `RED`
   - Proceed to GREEN phase

## Test Structure Pattern

```python
def test_feature_does_expected_thing():
    """
    REQ: [Requirement reference]
    Verifies: [What this test verifies]
    """
    # Arrange - set up test conditions
    input_data = prepare_test_input()

    # Act - call the code under test
    result = function_under_test(input_data)

    # Assert - verify expected behavior
    assert result == expected_value
```

## Example: Python (pytest)

```python
# tests/test_user_auth.py
def test_authenticate_user_with_valid_credentials():
    """
    REQ: User authentication
    Verifies: Valid credentials return authenticated user
    """
    # Arrange
    username = "testuser"
    password = "validpassword"

    # Act
    result = authenticate_user(username, password)

    # Assert
    assert result.is_authenticated is True
    assert result.username == username
```

```bash
# Run the test - should FAIL because authenticate_user doesn't exist
pytest tests/test_user_auth.py -v

# Expected output:
# FAILED test_authenticate_user_with_valid_credentials - NameError: name 'authenticate_user' is not defined

# Commit the failing test
git add tests/test_user_auth.py
git commit -m "RED: test for user authentication"
```

## Validation Checklist

Before moving to GREEN phase:

- [ ] Test is written with clear name describing behavior
- [ ] Test calls code that will be implemented
- [ ] Test asserts expected behavior
- [ ] Test has been executed and FAILS
- [ ] Failure message is clear and meaningful
- [ ] Test is committed with "RED: ..." message
- [ ] Status is marked as `RED`

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Test passes immediately | Not testing new functionality | Ensure code doesn't exist yet |
| Test errors (not fails) | Syntax error or import issue | Fix test to properly call code |
| Vague test name | Unclear what's being tested | Use descriptive name: test_X_does_Y |
| Multiple assertions | Testing too much at once | One behavior per test |

## Error Handling

| Scenario | Action |
|----------|--------|
| Test passes on first run | Delete/revert, verify you're testing new functionality |
| Test throws error (not failure) | Fix test syntax, ensure proper imports |
| Can't write a failing test | Requirement may be unclear, clarify first |

## Related Operations

- [op-implement-minimum-code.md](op-implement-minimum-code.md) - Next phase (GREEN)
- [op-verify-tdd-compliance.md](op-verify-tdd-compliance.md) - Verify discipline
- [op-handle-tdd-violation.md](op-handle-tdd-violation.md) - If rule violated
