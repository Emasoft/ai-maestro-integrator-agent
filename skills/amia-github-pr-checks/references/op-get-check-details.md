# Operation: Get Check Details

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Run the Check Details Script](#step-1-run-the-check-details-script)
  - [Step 2: Parse the Output](#step-2-parse-the-output)
  - [Step 3: Analyze Failure](#step-3-analyze-failure)
- [Command Variants](#command-variants)
  - [Basic Check Details](#basic-check-details)
  - [Include Logs URL](#include-logs-url)
  - [Check with Spaces in Name](#check-with-spaces-in-name)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Understanding Check Output](#understanding-check-output)
  - [Output Structure](#output-structure)
  - [Annotations](#annotations)
- [Common Failure Patterns](#common-failure-patterns)
- [Example: Investigating Test Failure](#example-investigating-test-failure)
- [Example: Build Failure](#example-build-failure)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Retrieve detailed information about a specific CI check to investigate failures or understand check behavior.

## When to Use

- When a check has failed and you need to understand why
- When investigating flaky tests
- When check behavior is unexpected
- To get logs URL for failed checks

## Prerequisites

- GitHub CLI authenticated
- Check has run (not pending)
- Know the check name

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| check_name | string | Yes | Name of the check to investigate |
| include_logs_url | boolean | No | Include URL to check logs |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| name | string | Check name |
| status | string | completed, queued, in_progress |
| conclusion | string | success, failure, etc. |
| started_at | string | ISO timestamp when started |
| completed_at | string | ISO timestamp when completed |
| duration_seconds | integer | How long the check ran |
| details_url | string | URL to check details page |
| logs_url | string | URL to raw logs (if requested) |
| output | object | Check output with title and summary |

## Steps

### Step 1: Run the Check Details Script

```bash
python3 amia_get_check_details.py --pr <NUMBER> --check "<CHECK_NAME>"
```

### Step 2: Parse the Output

```json
{
  "name": "test",
  "status": "completed",
  "conclusion": "failure",
  "started_at": "2025-02-05T10:00:00Z",
  "completed_at": "2025-02-05T10:05:30Z",
  "duration_seconds": 330,
  "details_url": "https://github.com/owner/repo/runs/12345",
  "output": {
    "title": "3 tests failed",
    "summary": "test_auth.py::test_login FAILED\ntest_auth.py::test_logout FAILED\ntest_db.py::test_connection FAILED"
  }
}
```

### Step 3: Analyze Failure

Based on the output:

- Review the failure summary
- Click details_url for full output
- Check logs_url for raw logs

## Command Variants

### Basic Check Details

```bash
python3 amia_get_check_details.py --pr 123 --check "test"
```

### Include Logs URL

```bash
python3 amia_get_check_details.py --pr 123 --check "build" --include-logs-url
```

### Check with Spaces in Name

```bash
python3 amia_get_check_details.py --pr 123 --check "Run Tests"
```

## Alternative: Direct gh CLI

```bash
# List all checks to find exact name
gh pr checks 123 --json name,conclusion,detailsUrl

# Get specific check details via API
gh api repos/{owner}/{repo}/check-runs/{check_run_id}
```

## Understanding Check Output

### Output Structure

```json
{
  "output": {
    "title": "Brief failure description",
    "summary": "Detailed information about what failed",
    "text": "Full output text (may be truncated)",
    "annotations_count": 3,
    "annotations_url": "URL to annotations"
  }
}
```

### Annotations

Annotations point to specific lines in code:

```json
{
  "annotations": [
    {
      "path": "src/auth.py",
      "start_line": 42,
      "end_line": 42,
      "annotation_level": "failure",
      "message": "AssertionError: Expected True, got False"
    }
  ]
}
```

## Common Failure Patterns

| Failure Type | Output Indicators | Action |
|--------------|-------------------|--------|
| Test failure | "tests failed", assertion errors | Review test output, fix code |
| Lint error | "linting errors", style violations | Run linter locally, fix issues |
| Build failure | "compilation failed", syntax errors | Check build logs, fix syntax |
| Timeout | "timed out", "exceeded time limit" | Optimize slow code, increase timeout |
| Resource limit | "out of memory", "disk full" | Optimize resource usage |

## Example: Investigating Test Failure

```bash
# Get test check details
python3 amia_get_check_details.py --pr 123 --check "test" --include-logs-url

# Output:
{
  "name": "test",
  "status": "completed",
  "conclusion": "failure",
  "duration_seconds": 245,
  "details_url": "https://github.com/owner/repo/actions/runs/12345",
  "logs_url": "https://github.com/owner/repo/actions/runs/12345/logs",
  "output": {
    "title": "Test suite failed",
    "summary": "3 of 150 tests failed\n\nFailed tests:\n- test_auth.py::test_login_invalid_password\n- test_auth.py::test_token_refresh\n- test_db.py::test_connection_timeout"
  }
}

# Next steps:
# 1. Click details_url to view full run
# 2. Download logs from logs_url
# 3. Reproduce failures locally
```

## Example: Build Failure

```bash
python3 amia_get_check_details.py --pr 123 --check "build"

# Output:
{
  "name": "build",
  "conclusion": "failure",
  "output": {
    "title": "Build failed",
    "summary": "Compilation error in src/main.py:42\nSyntaxError: unexpected indent"
  }
}

# Action: Fix syntax error at src/main.py line 42
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Check not found |
| 3 | API error |
| 4 | Not authenticated |

## Error Handling

| Error | Action |
|-------|--------|
| Check not found | Verify check name spelling (case-sensitive) |
| Multiple checks with same name | Use full workflow/job name |
| Logs expired | Check GitHub Actions retention settings |
| Truncated output | Download full logs from logs_url |

## Related Operations

- [op-get-pr-check-status.md](op-get-pr-check-status.md) - Get all check names
- [op-wait-for-checks.md](op-wait-for-checks.md) - Wait for check completion
- [ci-status-interpretation.md](ci-status-interpretation.md) - Understanding conclusions
