---
name: op-wait-for-checks
description: Wait for PR checks to complete with polling
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Wait for Checks


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Run the Wait Script](#step-1-run-the-wait-script)
  - [Step 2: Monitor Progress](#step-2-monitor-progress)
  - [Step 3: Parse Final Output](#step-3-parse-final-output)
- [Command Variants](#command-variants)
  - [Standard Wait (10 minute timeout)](#standard-wait-10-minute-timeout)
  - [Wait for Required Checks Only](#wait-for-required-checks-only)
  - [Custom Polling Interval](#custom-polling-interval)
  - [Long-Running CI (30 minute timeout)](#long-running-ci-30-minute-timeout)
- [Timeout Recommendations](#timeout-recommendations)
- [Polling Strategy](#polling-strategy)
- [Example](#example)
- [Example: Timeout Scenario](#example-timeout-scenario)
- [Decision Flow After Waiting](#decision-flow-after-waiting)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Handling Long-Running CI](#handling-long-running-ci)
- [Related Operations](#related-operations)

## Purpose

Poll GitHub and wait for all PR checks to complete before proceeding with merge or review decisions.

## When to Use

- When checks are still pending
- Before making merge decisions
- When you need to wait for CI completion
- After pushing new commits

## Prerequisites

- GitHub CLI authenticated
- PR has CI checks configured
- Checks have been triggered

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to monitor |
| timeout | integer | No | Maximum wait time in seconds (default: 600) |
| interval | integer | No | Polling interval in seconds (default: 30) |
| required_only | boolean | No | Wait only for required checks |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| pr_number | integer | The PR number monitored |
| completed | boolean | Whether all checks completed |
| timed_out | boolean | Whether timeout was reached |
| final_status | string | all_passing, some_failing, or pending |
| wait_time_seconds | integer | Total time waited |
| checks_summary | object | Final counts of passing/failing/pending |

## Steps

### Step 1: Run the Wait Script

```bash
python3 amia_wait_for_checks.py --pr <NUMBER> --timeout 600
```

### Step 2: Monitor Progress

The script will poll at regular intervals and output progress:
```
Waiting for checks on PR #123...
  Poll 1: 2 pending, 3 passing, 0 failing
  Poll 2: 1 pending, 4 passing, 0 failing
  Poll 3: 0 pending, 5 passing, 0 failing
Checks complete!
```

### Step 3: Parse Final Output

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

## Command Variants

### Standard Wait (10 minute timeout)

```bash
python3 amia_wait_for_checks.py --pr 123 --timeout 600
```

### Wait for Required Checks Only

```bash
python3 amia_wait_for_checks.py --pr 123 --required-only --timeout 300
```

### Custom Polling Interval

```bash
python3 amia_wait_for_checks.py --pr 123 --interval 60
```

### Long-Running CI (30 minute timeout)

```bash
python3 amia_wait_for_checks.py --pr 123 --timeout 1800
```

## Timeout Recommendations

| CI Type | Recommended Timeout |
|---------|---------------------|
| Quick tests | 5 minutes (300s) |
| Standard CI | 10 minutes (600s) |
| Full test suite | 20 minutes (1200s) |
| Integration tests | 30 minutes (1800s) |

## Polling Strategy

The script uses intelligent polling:
1. Initial interval: 30 seconds
2. After 5 minutes: 60 second intervals
3. After 15 minutes: 120 second intervals

This reduces API calls while maintaining responsiveness.

## Example

```bash
# Wait up to 10 minutes for all checks
python3 amia_wait_for_checks.py --pr 123 --timeout 600

# Output on completion:
{
  "pr_number": 123,
  "completed": true,
  "timed_out": false,
  "final_status": "all_passing",
  "wait_time_seconds": 245,
  "checks_summary": {
    "passing": 5,
    "failing": 0,
    "pending": 0
  }
}
```

## Example: Timeout Scenario

```bash
# CI taking too long
python3 amia_wait_for_checks.py --pr 123 --timeout 60

# Output:
{
  "pr_number": 123,
  "completed": false,
  "timed_out": true,
  "final_status": "pending",
  "wait_time_seconds": 60,
  "checks_summary": {
    "passing": 2,
    "failing": 0,
    "pending": 3
  }
}
```

## Decision Flow After Waiting

```
Wait for Checks
    ↓
completed?
    ├── Yes → Check final_status
    │         ├── all_passing → Proceed with merge
    │         └── some_failing → Investigate failures
    └── No (timed_out) → Check CI runner status
                         ├── Runner healthy → Increase timeout, retry
                         └── Runner issue → Escalate
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - checks completed (may include failures) |
| 1 | Invalid parameters |
| 2 | PR not found |
| 3 | Timeout reached (timed_out: true) |
| 4 | Not authenticated |

## Error Handling

| Error | Action |
|-------|--------|
| Timeout reached | Check CI runner status, may need longer timeout |
| Checks stuck pending | Investigate CI infrastructure |
| Network interruption | Script handles retries automatically |
| Rate limit | Script uses backoff automatically |

## Handling Long-Running CI

If CI regularly times out:

1. **Investigate CI performance**
   - Review test suite for slow tests
   - Check for resource constraints
   - Consider parallelization

2. **Adjust timeout**
   - Use longer timeout for known slow pipelines
   - Set timeout based on historical CI duration

3. **Use required-only flag**
   - Wait only for critical checks
   - Let non-required checks complete asynchronously

## Related Operations

- [op-get-pr-check-status.md](op-get-pr-check-status.md) - Get current status snapshot
- [op-get-check-details.md](op-get-check-details.md) - Investigate failures after wait
- [polling-strategies.md](polling-strategies.md) - Detailed polling strategies
