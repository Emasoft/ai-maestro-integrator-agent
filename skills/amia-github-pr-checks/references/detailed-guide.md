# GitHub PR Checks Skill — Detailed Guide

## Table of Contents

- [Decision Tree](#decision-tree-which-script-do-i-need)
- [Check Status Quick Reference](#check-status-quick-reference)
- [Scripts Reference](#scripts-reference)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes-standardized)
- [Debugging Commands](#debugging-commands)

## Decision Tree: Which Script Do I Need?

```
START: What do you need to know about PR checks?
|
+-> "What is the current status of all checks?"
|   -> Use: amia_get_pr_checks.py --pr <number>
|      Returns: List of all checks with their conclusions
|
+-> "Are all required checks passing?"
|   -> Use: amia_get_pr_checks.py --pr <number> --required-only
|      Returns: Status of only required checks
|
+-> "I need to wait until checks complete"
|   -> Use: amia_wait_for_checks.py --pr <number> --timeout <seconds>
|      Returns: Final status after all checks complete or timeout
|
+-> "Why did a specific check fail?"
|   -> Use: amia_get_check_details.py --pr <number> --check <name>
|      Returns: Detailed check info including logs URL
|
+-> "Is this PR ready to merge?"
    -> Use: amia_get_pr_checks.py --pr <number> --summary-only
       Returns: Simple pass/fail summary
```

## Check Status Quick Reference

| Conclusion | Meaning | Action Required |
|------------|---------|-----------------|
| `success` | Check passed | None |
| `failure` | Check failed | Investigate and fix |
| `pending` | Check still running | Wait or investigate if stuck |
| `skipped` | Check was skipped | Usually OK, verify skip condition |
| `cancelled` | Check was cancelled | Re-run if needed |
| `timed_out` | Check exceeded time limit | Optimize or increase timeout |
| `action_required` | Manual action needed | Review check details |
| `neutral` | Neither pass nor fail | Check is informational only |
| `stale` | Check is outdated | Push new commit to trigger |

## Scripts Reference

### 1. amia_get_pr_checks.py

**Purpose**: Retrieve all check statuses for a Pull Request.

**Usage**:

```bash
# Get all checks for PR #123
python amia_get_pr_checks.py --pr 123

# Get only required checks
python amia_get_pr_checks.py --pr 123 --required-only

# Get summary only (pass/fail count)
python amia_get_pr_checks.py --pr 123 --summary-only

# Specify repository (if not in git directory)
python amia_get_pr_checks.py --pr 123 --repo owner/repo
```

**Output Format**:

```json
{
  "pr_number": 123,
  "total_checks": 5,
  "passing": 3,
  "failing": 1,
  "pending": 1,
  "skipped": 0,
  "all_passing": false,
  "required_passing": false,
  "checks": [
    {
      "name": "build",
      "status": "completed",
      "conclusion": "success",
      "required": true
    }
  ]
}
```

### 2. amia_wait_for_checks.py

**Purpose**: Poll and wait for all PR checks to complete.

**Usage**:

```bash
# Wait up to 10 minutes for checks
python amia_wait_for_checks.py --pr 123 --timeout 600

# Wait only for required checks
python amia_wait_for_checks.py --pr 123 --required-only --timeout 300

# Custom polling interval (default 30s)
python amia_wait_for_checks.py --pr 123 --interval 60
```

**Output Format**:

```json
{
  "pr_number": 123,
  "completed": true,
  "timed_out": false,
  "final_status": "all_passing",
  "wait_time_seconds": 180,
  "checks_summary": {
    "passing": 5,
    "failing": 0,
    "pending": 0
  }
}
```

### 3. amia_get_check_details.py

**Purpose**: Get detailed information about a specific check.

**Usage**:

```bash
# Get details for a specific check
python amia_get_check_details.py --pr 123 --check "build"

# Include logs URL
python amia_get_check_details.py --pr 123 --check "test" --include-logs-url
```

**Output Format**:

```json
{
  "name": "build",
  "status": "completed",
  "conclusion": "failure",
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:05:30Z",
  "duration_seconds": 330,
  "details_url": "https://github.com/...",
  "logs_url": "https://github.com/.../logs",
  "output": {
    "title": "Build failed",
    "summary": "Compilation error in src/main.py"
  }
}
```

## Error Handling

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "No checks found" | PR has no CI configured | Verify repository has CI workflows |
| Checks stuck in "pending" | CI runner unavailable | Check GitHub Actions status page |
| Required check missing | Branch protection misconfigured | Review repository settings |
| Timeout while waiting | CI taking too long | Increase timeout or check CI performance |
| Authentication error | gh CLI not logged in | Run `gh auth login` |

## Exit Codes (Standardized)

All scripts use standardized exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Output is valid JSON with check data |
| 1 | Invalid parameters | Bad PR number, missing required args |
| 2 | Resource not found | PR or check does not exist |
| 3 | API error | Network, rate limit, timeout waiting for checks |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | N/A for these scripts |
| 6 | Not mergeable | N/A for these scripts |

**Note:** `amia_wait_for_checks.py` returns exit code 3 on timeout. Check the JSON output's `timed_out` field for details.

## Debugging Commands

```bash
# Verify gh CLI authentication
gh auth status

# Check repository access
gh repo view owner/repo

# Manual check inspection
gh pr checks <number> --json name,status,conclusion

# View raw API response
gh api repos/owner/repo/commits/SHA/check-runs
```
