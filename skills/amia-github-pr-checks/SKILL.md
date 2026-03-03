---
name: amia-github-pr-checks
description: "Use when monitoring PR checks. Trigger with CI status, check verification, or PR readiness requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  tags: "github, ci-cd, pull-requests, checks, automation"
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub PR Checks Skill

## Overview

This skill enables agents to monitor, interpret, and wait for GitHub Pull Request check statuses. Use this skill when you need to:

- Verify all CI/CD checks are passing before merging
- Wait for pending checks to complete
- Understand why a check failed
- Determine if a PR is ready for merge based on required checks
- Poll for check completion with intelligent backoff

## Output

| Output Type | Format | Contents |
|-------------|--------|----------|
| Check Status Report | JSON | Complete status of all PR checks including pass/fail counts, individual check conclusions, and required check status |
| Wait Completion Report | JSON | Final status after polling, including timeout status, total wait time, and checks summary |
| Check Details | JSON | Detailed information about a specific check including duration, logs URL, and failure output |
| Exit Code | Integer | Standardized exit code (0-6) indicating success, error type, or specific failure reason |

## Instructions

Follow these steps to monitor and manage GitHub PR checks:

1. **Determine Your Objective**
   - Review the decision tree below to identify which script matches your needs
   - Consider whether you need real-time polling or just current status
   - Identify if you need all checks or only required checks

2. **Select and Execute the Appropriate Script**
   - Use `amia_get_pr_checks.py` for current status snapshots
   - Use `amia_wait_for_checks.py` for polling until completion
   - Use `amia_get_check_details.py` for investigating specific failures
   - Refer to the Scripts Reference section for command-line options

3. **Parse the JSON Output**
   - All scripts return structured JSON to stdout
   - Check the `all_passing` or `final_status` field for overall status
   - Examine individual check objects for detailed information
   - Use the exit code for automated decision-making

4. **Interpret Check Conclusions**
   - Refer to the Check Status Quick Reference table
   - Identify which checks are required vs optional
   - Determine if action is needed (see Action Required column)

5. **Take Appropriate Action**
   - If all passing: proceed with merge or next workflow step
   - If failing: investigate using `amia_get_check_details.py`
   - If pending: wait using `amia_wait_for_checks.py` with appropriate timeout
   - If timeout: check CI runner status and consider increasing timeout

6. **Handle Errors Gracefully**
   - Check exit codes (see Exit Codes section)
   - Refer to Error Handling section for common issues
   - Use debugging commands to verify authentication and access

### Checklist

Copy this checklist and track your progress:

- [ ] Verify gh CLI is authenticated: `gh auth status`
- [ ] Determine objective (current status, wait for completion, investigate failure)
- [ ] Get current PR check status: `python amia_get_pr_checks.py --pr <number>`
- [ ] Review `all_passing` field in JSON output
- [ ] If checks pending, wait for completion: `python amia_wait_for_checks.py --pr <number> --timeout <seconds>`
- [ ] If checks failing, investigate: `python amia_get_check_details.py --pr <number> --check "<name>"`
- [ ] Interpret check conclusions using Quick Reference table
- [ ] Identify required vs optional failing checks
- [ ] Take appropriate action based on results:
  - [ ] If all passing: proceed with merge
  - [ ] If failing: fix issues and push new commit
  - [ ] If timeout: check CI runner status
- [ ] Handle any errors using exit codes (0=success, 1-4=errors)
- [ ] Verify PR is ready for merge before proceeding

### When to Use This Skill

| Scenario | Script to Use |
|----------|---------------|
| Get current status of all PR checks | `amia_get_pr_checks.py` |
| Wait for all checks to finish | `amia_wait_for_checks.py` |
| Investigate a specific failing check | `amia_get_check_details.py` |
| Quick check if PR is mergeable | `amia_get_pr_checks.py --summary-only` |

## Decision Tree: Which Script Do I Need?

```
START: What do you need to know about PR checks?
│
├─► "What is the current status of all checks?"
│   └─► Use: amia_get_pr_checks.py --pr <number>
│       Returns: List of all checks with their conclusions
│
├─► "Are all required checks passing?"
│   └─► Use: amia_get_pr_checks.py --pr <number> --required-only
│       Returns: Status of only required checks
│
├─► "I need to wait until checks complete"
│   └─► Use: amia_wait_for_checks.py --pr <number> --timeout <seconds>
│       Returns: Final status after all checks complete or timeout
│
├─► "Why did a specific check fail?"
│   └─► Use: amia_get_check_details.py --pr <number> --check <name>
│       Returns: Detailed check info including logs URL
│
└─► "Is this PR ready to merge?"
    └─► Use: amia_get_pr_checks.py --pr <number> --summary-only
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

## Reference Documents

### Understanding CI Status Interpretation

For detailed guidance on interpreting check statuses, see [ci-status-interpretation.md](references/ci-status-interpretation.md):

- 1. Understanding GitHub Check Conclusions
  - 1.1 Complete list of conclusion values
  - 1.2 When each conclusion occurs
  - 1.3 How to respond to each conclusion
- 2. Required vs Optional Checks
  - 2.1 How branch protection defines required checks
  - 2.2 Identifying required checks programmatically
  - 2.3 Handling optional check failures
- 3. Check Run vs Check Suite
  - 3.1 Difference between check runs and check suites
  - 3.2 When to query which API endpoint
  - 3.3 Aggregating results from multiple providers
- 4. Common CI Providers
  - 4.1 GitHub Actions check naming conventions
  - 4.2 CircleCI integration patterns
  - 4.3 Jenkins GitHub plugin behavior
  - 4.4 Third-party status checks

### Polling Strategies

For guidance on waiting for checks, see [polling-strategies.md](references/polling-strategies.md):

- 1. When to Poll for Check Completion
  - 1.1 Scenarios requiring polling
  - 1.2 Avoiding unnecessary polling
  - 1.3 Webhook alternatives
- 2. Exponential Backoff Implementation
  - 2.1 Why exponential backoff matters
  - 2.2 Recommended backoff parameters
  - 2.3 Jitter for distributed systems
- 3. Timeout Handling
  - 3.1 Setting appropriate timeouts
  - 3.2 Graceful timeout behavior
  - 3.3 Partial completion scenarios
- 4. Partial Success Scenarios
  - 4.1 Handling mixed results
  - 4.2 Re-running failed checks
  - 4.3 Determining merge readiness with failures

## Examples

### Example 1: Check PR Status Before Merge

```bash
# Get all check statuses for PR #123
python amia_get_pr_checks.py --pr 123

# If all_passing is true, proceed with merge
# If not, investigate failing checks
```

### Example 2: Wait for CI to Complete

```bash
# Wait up to 10 minutes for all checks to complete
python amia_wait_for_checks.py --pr 456 --timeout 600

# If timed_out is true, check CI runner status
# If completed is true and final_status is all_passing, merge is safe
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

### Debugging Commands

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

## Prerequisites

- **gh CLI**: Must be installed and authenticated (`gh auth login`)
- **Repository access**: Read access to the target repository
- **Python 3.8+**: For running the scripts

## Exit Codes (Standardized)

All scripts use standardized exit codes for consistent error handling:

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

## Resources

- [references/ci-status-interpretation.md](references/ci-status-interpretation.md) - Understanding check conclusions and required checks
- [references/polling-strategies.md](references/polling-strategies.md) - When and how to poll for check completion
