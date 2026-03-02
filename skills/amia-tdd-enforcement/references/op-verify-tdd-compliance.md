---
name: op-verify-tdd-compliance
description: Verify that a PR or commit history follows TDD discipline
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Verify TDD Compliance


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [TDD Commit Pattern](#tdd-commit-pattern)
- [Verification Procedure](#verification-procedure)
- [Example Verification](#example-verification)
- [Compliance Criteria](#compliance-criteria)
- [Verification Script](#verification-script)
- [Violation Types](#violation-types)
- [Handling Violations](#handling-violations)
- [Validation Checklist](#validation-checklist)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Verify that code changes in a pull request or branch follow proper TDD discipline by examining commit history and ensuring tests were written before implementation.

## When to Use

- Reviewing a pull request for merge eligibility
- Auditing a branch for TDD compliance
- Verifying remote developer agents followed TDD
- Quality gate check before merge

## Prerequisites

- Git repository with commit history
- Access to the PR or branch being verified
- Understanding of TDD commit patterns

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| PR number or branch | String | The changes to verify |
| Repository | String | Repository location |

## Output

| Output Type | Description |
|-------------|-------------|
| Compliance report | TDD compliance status (pass/fail) |
| Commit analysis | Pattern matching results |
| Violations | List of TDD discipline violations |
| Recommendations | How to fix violations |

## TDD Commit Pattern

Valid TDD follows this commit pattern:

```
RED: test for [feature]     <- Test written FIRST
GREEN: implement [feature]  <- Implementation SECOND
REFACTOR: improve [aspect]  <- Refactoring THIRD
```

Each feature should have commits in this order.

## Verification Procedure

1. **Get commit history for PR/branch**
   ```bash
   git log --oneline origin/main..HEAD
   # or
   gh pr view <NUMBER> --json commits
   ```

2. **Check for RED-GREEN-REFACTOR pattern**
   ```bash
   git log --oneline | grep -E "^[a-f0-9]+ (RED|GREEN|REFACTOR):"
   ```

3. **Verify order is correct**
   - RED must come before GREEN for same feature
   - GREEN must come before REFACTOR for same feature
   - No GREEN without preceding RED

4. **Check test coverage**
   - New production code must have corresponding tests
   - Tests must exist in commits before implementation

5. **Generate compliance report**

## Example Verification

```bash
# Get commits in the PR
git log --oneline origin/main..feature-branch

# Expected good pattern:
# abc1234 REFACTOR: improve error handling in login
# def5678 GREEN: implement user login
# 789abcd RED: test for user login
# 111aaa REFACTOR: clean up auth module
# 222bbb GREEN: implement logout
# 333ccc RED: test for logout

# Bad pattern (no RED before GREEN):
# abc1234 GREEN: implement user login
# def5678 GREEN: implement logout
# <- Missing RED commits = TDD violation
```

## Compliance Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| RED before GREEN | Every GREEN has preceding RED | GREEN without RED |
| Test coverage | All new code has tests | Code without tests |
| Commit messages | Follow RED/GREEN/REFACTOR pattern | Missing or wrong prefixes |
| Cycle completion | RED->GREEN->REFACTOR | Incomplete cycles |

## Verification Script

```bash
#!/bin/bash
# Simple TDD compliance check

COMMITS=$(git log --oneline origin/main..HEAD)

# Count phase commits
RED_COUNT=$(echo "$COMMITS" | grep -c "^[a-f0-9]* RED:")
GREEN_COUNT=$(echo "$COMMITS" | grep -c "^[a-f0-9]* GREEN:")
REFACTOR_COUNT=$(echo "$COMMITS" | grep -c "^[a-f0-9]* REFACTOR:")

echo "TDD Compliance Report"
echo "===================="
echo "RED commits: $RED_COUNT"
echo "GREEN commits: $GREEN_COUNT"
echo "REFACTOR commits: $REFACTOR_COUNT"

# Basic check: GREEN should not exceed RED
if [ "$GREEN_COUNT" -gt "$RED_COUNT" ]; then
    echo "WARNING: More GREEN than RED commits - possible TDD violation"
    exit 1
fi

echo "TDD compliance: PASS"
exit 0
```

## Violation Types

| Violation | Description | Severity |
|-----------|-------------|----------|
| Missing RED | GREEN commit without preceding RED | Critical |
| Wrong order | GREEN before RED for same feature | Critical |
| No commit messages | Missing RED/GREEN/REFACTOR prefixes | Major |
| Incomplete cycle | RED without GREEN, or GREEN without REFACTOR | Minor |

## Handling Violations

When violations are found:

1. **Document the violation**
2. **Request correction from developer**
3. **Block merge until corrected**
4. **Use op-handle-tdd-violation for recovery**

## Validation Checklist

- [ ] All GREEN commits have preceding RED commits
- [ ] Commit messages follow RED/GREEN/REFACTOR pattern
- [ ] Test files exist for all new production code
- [ ] Cycles are complete (RED->GREEN->REFACTOR)
- [ ] No production code without tests

## Error Handling

| Scenario | Action |
|----------|--------|
| No TDD commits found | Request resubmission with proper TDD |
| Partial compliance | Note violations, request fixes |
| Cannot determine order | Manual review needed |

## Related Operations

- [op-write-failing-test.md](op-write-failing-test.md) - RED phase
- [op-implement-minimum-code.md](op-implement-minimum-code.md) - GREEN phase
- [op-refactor-code.md](op-refactor-code.md) - REFACTOR phase
- [op-handle-tdd-violation.md](op-handle-tdd-violation.md) - Fix violations
