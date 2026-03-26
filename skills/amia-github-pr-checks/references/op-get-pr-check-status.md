# Operation: Get PR Check Status

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Run the Check Status Script](#step-1-run-the-check-status-script)
  - [Step 2: Parse the JSON Output](#step-2-parse-the-json-output)
  - [Step 3: Interpret Results](#step-3-interpret-results)
- [Command Variants](#command-variants)
  - [Get All Checks](#get-all-checks)
  - [Get Only Required Checks](#get-only-required-checks)
  - [Get Summary Only](#get-summary-only)
  - [Specify Repository](#specify-repository)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Check Conclusions Reference](#check-conclusions-reference)
- [Example](#example)
- [Decision Flow](#decision-flow)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Retrieve the current status of all CI/CD checks for a Pull Request to determine if it's ready to merge or requires attention.

## When to Use

- Before starting PR review
- To verify CI status before merge
- When checking if PR is ready for next gate
- To get a snapshot of all check states

## Prerequisites

- GitHub CLI authenticated
- Access to repository
- PR exists and has checks configured

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to check |
| repo | string | No | Repository in owner/repo format |
| required_only | boolean | No | Only return required checks |
| summary_only | boolean | No | Return only pass/fail summary |

## Output

| Field | Type | Description |
|-------|------|-------------|
| pr_number | integer | The PR number queried |
| total_checks | integer | Total number of checks |
| passing | integer | Number of passing checks |
| failing | integer | Number of failing checks |
| pending | integer | Number of pending checks |
| all_passing | boolean | Whether all checks pass |
| required_passing | boolean | Whether all required checks pass |
| checks | array | Individual check details |

## Steps

### Step 1: Run the Check Status Script

```bash
python3 amia_get_pr_checks.py --pr <NUMBER>
```

### Step 2: Parse the JSON Output

```json
{
  "pr_number": 123,
  "total_checks": 5,
  "passing": 3,
  "failing": 1,
  "pending": 1,
  "all_passing": false,
  "required_passing": false,
  "checks": [
    {
      "name": "build",
      "status": "completed",
      "conclusion": "success",
      "required": true
    },
    {
      "name": "test",
      "status": "completed",
      "conclusion": "failure",
      "required": true
    }
  ]
}
```

### Step 3: Interpret Results

| Field | Interpretation |
|-------|----------------|
| `all_passing: true` | PR ready for merge (if approved) |
| `all_passing: false` | PR needs attention |
| `required_passing: true` | Minimum merge requirements met |
| `pending > 0` | Checks still running |

## Command Variants

### Get All Checks

```bash
python3 amia_get_pr_checks.py --pr 123
```

### Get Only Required Checks

```bash
python3 amia_get_pr_checks.py --pr 123 --required-only
```

### Get Summary Only

```bash
python3 amia_get_pr_checks.py --pr 123 --summary-only
```

### Specify Repository

```bash
python3 amia_get_pr_checks.py --pr 123 --repo owner/repo
```

## Alternative: Direct gh CLI

```bash
# Get all checks
gh pr checks 123 --json name,status,conclusion

# Get required checks only
gh pr checks 123 --required

# Simple status view
gh pr checks 123
```

## Check Conclusions Reference

| Conclusion | Meaning | Action |
|------------|---------|--------|
| `success` | Check passed | None needed |
| `failure` | Check failed | Investigate and fix |
| `pending` | Still running | Wait for completion |
| `skipped` | Check skipped | Verify skip condition |
| `cancelled` | Check cancelled | Re-run if needed |
| `timed_out` | Check timed out | Investigate, increase timeout |
| `neutral` | Informational | Review but not blocking |
| `stale` | Check outdated | Push new commit |

## Example

```bash
# Check PR status
python3 amia_get_pr_checks.py --pr 123

# Output:
{
  "pr_number": 123,
  "total_checks": 4,
  "passing": 4,
  "failing": 0,
  "pending": 0,
  "all_passing": true,
  "required_passing": true,
  "checks": [
    {"name": "build", "status": "completed", "conclusion": "success", "required": true},
    {"name": "test", "status": "completed", "conclusion": "success", "required": true},
    {"name": "lint", "status": "completed", "conclusion": "success", "required": false},
    {"name": "coverage", "status": "completed", "conclusion": "success", "required": false}
  ]
}

# Interpretation: All checks passing, PR ready for merge
```

## Decision Flow

```
Get Check Status
    ↓
all_passing?
    ├── Yes → Proceed with merge flow
    └── No → Check pending count
              ├── pending > 0 → Wait for checks (use op-wait-for-checks)
              └── pending = 0 → Investigate failures (use op-get-check-details)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - JSON output valid |
| 1 | Invalid parameters |
| 2 | PR not found |
| 3 | API error |
| 4 | Not authenticated |

## Error Handling

| Error | Action |
|-------|--------|
| PR not found | Verify PR number and repository |
| Authentication error | Run `gh auth login` |
| No checks found | Verify CI is configured |
| Rate limit | Wait and retry |

## Related Operations

- [op-wait-for-checks.md](op-wait-for-checks.md) - Wait for pending checks
- [op-get-check-details.md](op-get-check-details.md) - Investigate failures
- [op-interpret-check-conclusions.md](op-interpret-check-conclusions.md) - Understand results
