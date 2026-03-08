---
name: op-execute-pre-review-gate
description: Execute Pre-Review Gate checks (tests, linting, build)
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Execute Pre-Review Gate

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Required Checks](#required-checks)
- [Warning Checks (Non-Blocking)](#warning-checks-non-blocking)
- [Steps](#steps)
  - [Step 1: Check CI Status](#step-1-check-ci-status)
  - [Step 2: Verify Tests Pass](#step-2-verify-tests-pass)
  - [Step 3: Verify Linting Clean](#step-3-verify-linting-clean)
  - [Step 4: Verify Build Success](#step-4-verify-build-success)
  - [Step 5: Verify PR Description](#step-5-verify-pr-description)
  - [Step 6: Evaluate Warnings](#step-6-evaluate-warnings)
  - [Step 7: Apply Gate Decision](#step-7-apply-gate-decision)
- [Gate Pass Criteria](#gate-pass-criteria)
- [Example](#example)
- [Failure Handling](#failure-handling)
- [Pre-Review Gate Failed](#pre-review-gate-failed)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Run automated checks before human review begins. This gate ensures basic code health before investing reviewer time.

## When to Use

- When PR is first opened
- When PR is updated with new commits
- When gate is identified as pre-review pending

## Prerequisites

- PR is open
- CI pipeline configured
- Test suite exists
- Linting tools configured

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to check |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| gate_passed | boolean | Whether all required checks passed |
| check_results | object | Individual check outcomes |
| warnings | array | Non-blocking warnings |
| next_gate | string | review (if passed) |

## Required Checks

| Check | Blocking | Description |
|-------|----------|-------------|
| Tests Pass | Yes | All unit/integration tests must pass |
| Linting Clean | Yes | No linting errors |
| Build Success | Yes | Code compiles/builds successfully |
| PR Description | Yes | PR has meaningful description |

## Warning Checks (Non-Blocking)

| Check | Description |
|-------|-------------|
| Test Coverage | Coverage below threshold triggers warning |
| Changelog Entry | Missing changelog warns but doesn't block |
| Large PR | >500 lines triggers review complexity warning |
| Style Issues | Minor style issues warn but don't block |

## Steps

### Step 1: Check CI Status

```bash
python3 amia_get_pr_checks.py --pr <NUMBER>
```

Verify:

- All required checks completed
- No required checks failing

### Step 2: Verify Tests Pass

```bash
# Check for test-related checks
gh pr checks <NUMBER> --json name,conclusion | jq '.[] | select(.name | test("test|spec"))'
```

### Step 3: Verify Linting Clean

```bash
# Check for lint-related checks
gh pr checks <NUMBER> --json name,conclusion | jq '.[] | select(.name | test("lint|eslint|ruff|pylint"))'
```

### Step 4: Verify Build Success

```bash
# Check for build-related checks
gh pr checks <NUMBER> --json name,conclusion | jq '.[] | select(.name | test("build|compile"))'
```

### Step 5: Verify PR Description

```bash
# Get PR body
BODY=$(gh pr view <NUMBER> --json body --jq '.body')
# Check if meaningful (not empty, not just template)
[ ${#BODY} -gt 50 ] && echo "Description OK" || echo "Description too short"
```

### Step 6: Evaluate Warnings

Check for warning conditions:

```bash
# Coverage check (if available)
gh pr checks <NUMBER> --json name,conclusion | jq '.[] | select(.name | test("coverage"))'

# Diff size
gh pr view <NUMBER> --json additions,deletions --jq '.additions + .deletions'
```

### Step 7: Apply Gate Decision

If all required checks pass:

```bash
gh pr edit <NUMBER> --remove-label "gate:pre-review-pending" --add-label "gate:pre-review-passed"
```

If any required check fails:

```bash
gh pr edit <NUMBER> --add-label "gate:pre-review-failed"
```

## Gate Pass Criteria

ALL of these must be true:

- [ ] All tests pass (no test failures)
- [ ] Linting passes (no lint errors)
- [ ] Build succeeds (code compiles)
- [ ] PR description exists and is meaningful

## Example

```bash
# Get all check results
python3 amia_get_pr_checks.py --pr 123

# Example output:
{
  "pr_number": 123,
  "all_passing": true,
  "checks": [
    {"name": "test", "conclusion": "success"},
    {"name": "lint", "conclusion": "success"},
    {"name": "build", "conclusion": "success"}
  ]
}

# Apply passed label
gh pr edit 123 --remove-label "gate:pre-review-pending" --add-label "gate:pre-review-passed"
```

## Failure Handling

If gate fails:

1. Apply `gate:pre-review-failed` label
2. Comment with failure details
3. Follow [Escalation Path A](escalation-paths.md)

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## Pre-Review Gate Failed

The following checks did not pass:
- <FAILING_CHECK_1>
- <FAILING_CHECK_2>

Please fix these issues and push a new commit to re-run the checks.
EOF
)"
```

## Error Handling

| Error | Action |
|-------|--------|
| CI not configured | Flag as error, cannot pass gate |
| Checks stuck pending | Wait with timeout, escalate if stuck |
| Flaky test | Apply `gate:flaky-test` warning label, investigate |

## Related Operations

- [op-identify-current-gate.md](op-identify-current-gate.md) - Determines when to run this
- [op-execute-review-gate.md](op-execute-review-gate.md) - Next gate after pass
- [op-apply-gate-label.md](op-apply-gate-label.md) - Label application details
