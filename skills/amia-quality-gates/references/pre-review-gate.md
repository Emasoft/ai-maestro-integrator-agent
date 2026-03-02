# Pre-Review Gate

## Table of Contents

- [Purpose](#purpose)
- [Required Checks](#required-checks)
  - [1. Tests Pass](#1-tests-pass)
  - [2. Linting Pass](#2-linting-pass)
  - [3. Build Success](#3-build-success)
  - [4. PR Description Present](#4-pr-description-present)
  - [5. Issue Linked](#5-issue-linked)
- [Warning Conditions (Non-Blocking)](#warning-conditions-non-blocking)
- [Gate Pass Procedure](#gate-pass-procedure)
- [Gate Fail Procedure](#gate-fail-procedure)
- [Re-Evaluation Triggers](#re-evaluation-triggers)
- [Troubleshooting](#troubleshooting)
  - [Flaky Test Failures](#flaky-test-failures)
  - [Infrastructure Issues](#infrastructure-issues)

## Purpose

The Pre-Review Gate ensures basic code quality before human reviewers invest time. It verifies that automated checks pass and the PR has sufficient context.

## Required Checks

### 1. Tests Pass

**Check**: All test suites execute successfully
**Command**: `gh pr checks $PR_NUMBER | grep test`
**Pass Criteria**: All test jobs return success
**Failure Action**: Comment with test output, apply `gate:pre-review-failed`

### 2. Linting Pass

**Check**: No linting errors
**Command**: `gh pr checks $PR_NUMBER | grep lint`
**Pass Criteria**: Linting job returns success
**Failure Action**: Comment with lint errors, apply `gate:pre-review-failed`

### 3. Build Success

**Check**: Code builds without errors
**Command**: `gh pr checks $PR_NUMBER | grep build`
**Pass Criteria**: Build job returns success
**Failure Action**: Comment with build log, apply `gate:pre-review-failed`

### 4. PR Description Present

**Check**: PR has non-empty description
**Command**: `gh pr view $PR_NUMBER --json body -q .body`
**Pass Criteria**: Body is not empty
**Failure Action**: Request description from author

### 5. Issue Linked

**Check**: PR links to an issue
**Command**: `gh pr view $PR_NUMBER --json closingIssuesReferences`
**Pass Criteria**: At least one issue referenced
**Failure Action**: Request issue link from author (warning only)

## Warning Conditions (Non-Blocking)

| Condition | Warning Label | Trigger |
|-----------|--------------|---------|
| Test coverage < 80% | `gate:coverage-warning` | Coverage report shows < 80% |
| Large PR (30+ files) | `gate:large-pr` | File count > 30 |
| No changelog entry | `gate:changelog-needed` | CHANGELOG.md not modified |
| Style issues | `gate:style-issues` | Minor formatting issues detected |

## Gate Pass Procedure

```bash
# Verify all checks
gh pr checks $PR_NUMBER

# Apply passed label
gh pr edit $PR_NUMBER --add-label "gate:pre-review-passed"

# Remove pending label if present
gh pr edit $PR_NUMBER --remove-label "gate:pre-review-pending"

# Notify reviewers
gh pr comment $PR_NUMBER --body "✅ Pre-review gate passed. Ready for code review."
```

## Gate Fail Procedure

```bash
# Apply failed label
gh pr edit $PR_NUMBER --add-label "gate:pre-review-failed"

# Comment with specific failures
gh pr comment $PR_NUMBER --body "❌ Pre-review gate failed:

- Tests: [PASS/FAIL with details]
- Linting: [PASS/FAIL with details]
- Build: [PASS/FAIL with details]
- Description: [PASS/FAIL]

Please address failures and push fixes. Gate will re-evaluate on next commit."

# Follow Escalation Path A if author unresponsive
```

## Re-Evaluation Triggers

The Pre-Review Gate automatically re-evaluates when:
- New commits are pushed
- CI jobs are manually re-run
- Gate checks are manually triggered via `/amia-run-gate pre-review` command

## Troubleshooting

### Flaky Test Failures

If tests fail intermittently:
1. Add `gate:flaky-test` label
2. Re-run CI
3. If persistent, require test stabilization before advancing

### Infrastructure Issues

If CI infrastructure fails (not code issues):
1. Document infrastructure failure
2. Apply `gate:ci-infrastructure-issue` label
3. Escalate to AMOA for resolution
4. Do not block PR for infrastructure issues (but do not advance either until resolved)
