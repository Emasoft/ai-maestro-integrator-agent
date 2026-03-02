---
name: op-handle-tdd-violation
description: Handle and recover from TDD discipline violations
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Handle TDD Violation


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Common Violations](#common-violations)
- [Recovery Procedure](#recovery-procedure)
  - [Option 1: Retroactive Test (Preferred)](#option-1-retroactive-test-preferred)
  - [Option 2: Rebase and Reorder (If safe)](#option-2-rebase-and-reorder-if-safe)
  - [Option 3: New PR with Proper TDD](#option-3-new-pr-with-proper-tdd)
- [Violation Documentation Template](#violation-documentation-template)
- [TDD Violation Report](#tdd-violation-report)
  - [What happened](#what-happened)
  - [Impact](#impact)
  - [Recovery action taken](#recovery-action-taken)
  - [Prevention](#prevention)
- [Example: Retroactive Test Recovery](#example-retroactive-test-recovery)
- [Validation After Recovery](#validation-after-recovery)
- [Prevention Measures](#prevention-measures)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Detect, document, and recover from violations of TDD discipline. When production code is written without a failing test first, this operation guides the correction process.

## When to Use

- When TDD verification reveals violations
- When production code was committed without tests
- When GREEN commit has no preceding RED commit
- When a developer admits skipping TDD

## Prerequisites

- Identified TDD violation
- Git access to the affected branch
- Ability to modify commits (if rebasing)

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| Violation type | String | Missing RED, wrong order, etc. |
| Affected commits | List | The non-compliant commits |
| Feature code | Path | The production code without tests |

## Output

| Output Type | Description |
|-------------|-------------|
| Violation report | Documentation of what went wrong |
| Recovery plan | Steps to fix the violation |
| Corrected commits | Properly ordered TDD commits |
| Compliance verification | Proof of correction |

## Common Violations

| Violation | Description | Severity |
|-----------|-------------|----------|
| Code without test | Production code committed without test | Critical |
| Missing RED | GREEN commit without preceding RED | Critical |
| Skipped REFACTOR | Direct RED to new RED | Minor |
| Wrong order | Code committed before test | Critical |

## Recovery Procedure

### Option 1: Retroactive Test (Preferred)

When production code exists without tests:

1. **Write tests for existing code**
   - Create tests that verify current behavior
   - Ensure tests would have failed before code existed

2. **Amend commit history** (if not yet pushed)
   ```bash
   # Create the test that "should have" been written first
   git add tests/test_feature.py
   git commit -m "RED: test for [feature] (retroactive)"

   # Amend the production commit to reference the test
   # Note: Only if commit is local
   ```

3. **Document the violation**
   - Note in commit message that this was retroactive
   - Add to PR description

### Option 2: Rebase and Reorder (If safe)

When commits are local and can be reordered:

```bash
# Interactive rebase to reorder commits
git rebase -i origin/main

# In editor, move test commit before implementation
# pick abc1234 GREEN: implement feature  <- move down
# pick def5678 RED: test for feature     <- move up

# After rebase:
# pick def5678 RED: test for feature
# pick abc1234 GREEN: implement feature
```

### Option 3: New PR with Proper TDD

When history cannot be fixed:

1. **Close the violating PR**
2. **Create new branch**
3. **Implement from scratch using TDD**
4. **Submit new PR with proper commits**

## Violation Documentation Template

```markdown
## TDD Violation Report

**Date:** [YYYY-MM-DD]
**Commits affected:** [list]
**Violation type:** [Missing RED / Wrong order / Code without test]

### What happened
[Description of the violation]

### Impact
[What TDD principles were violated]

### Recovery action taken
[Option 1/2/3 and specific steps]

### Prevention
[How to avoid this in future]
```

## Example: Retroactive Test Recovery

```bash
# Situation: src/auth.py was committed without tests

# Step 1: Write the tests that should have existed
# tests/test_auth.py
def test_authenticate_user_returns_authenticated_result():
    result = authenticate_user("testuser", "password")
    assert result.is_authenticated is True

# Step 2: Verify test passes with existing code
pytest tests/test_auth.py -v
# PASSED (because code exists)

# Step 3: Commit with violation note
git add tests/test_auth.py
git commit -m "RED: test for authenticate_user (retroactive - violation recovery)"

# Step 4: Document in PR
# Add note explaining the recovery
```

## Validation After Recovery

- [ ] Tests now exist for all production code
- [ ] Tests verify correct behavior
- [ ] Documentation explains the violation
- [ ] Future violations will be prevented

## Prevention Measures

1. **Pre-commit hooks** - Block commits without test files
2. **CI checks** - Verify RED-GREEN-REFACTOR pattern
3. **Code review** - Explicitly check for TDD compliance
4. **Status tracking** - Use status markers to track phase

## Error Handling

| Scenario | Action |
|----------|--------|
| Cannot rebase (pushed) | Use Option 1 or 3 |
| Tests hard to write retroactively | May indicate poor design |
| Violation in merged code | Document and add tests in new PR |

## Related Operations

- [op-verify-tdd-compliance.md](op-verify-tdd-compliance.md) - Detect violations
- [op-write-failing-test.md](op-write-failing-test.md) - Proper RED phase
- [op-implement-minimum-code.md](op-implement-minimum-code.md) - Proper GREEN phase
