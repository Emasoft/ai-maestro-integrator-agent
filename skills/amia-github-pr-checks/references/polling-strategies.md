# Polling Strategies for GitHub PR Checks

This document provides guidance on efficiently polling for GitHub PR check completion, implementing proper backoff strategies, handling timeouts, and dealing with partial success scenarios.

## Contents

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

---

## 1. When to Poll for Check Completion

### 1.1 Scenarios Requiring Polling

Polling is necessary when:

1. **Automated merge workflows**: Wait for all checks before auto-merging
2. **Deployment pipelines**: Ensure tests pass before deploying
3. **Notification systems**: Alert when checks complete
4. **CI monitoring dashboards**: Track real-time status
5. **Batch operations**: Process multiple PRs as checks complete

**Example scenario**: An orchestrator agent needs to merge a PR after all checks pass:
```
1. Create PR
2. Wait for checks to start (may take seconds)
3. Poll until all checks complete
4. If all pass, merge PR
5. If any fail, notify and await fix
```

### 1.2 Avoiding Unnecessary Polling

Before implementing polling, consider:

| Question | If Yes | If No |
|----------|--------|-------|
| Is real-time status critical? | Poll | Use webhooks |
| Running in CI environment? | Poll | Consider webhooks |
| Need status for single PR? | Poll | Webhooks may be overkill |
| Have webhook infrastructure? | Use webhooks | Poll |
| Rate limits a concern? | Use webhooks + poll fallback | Poll |

**Anti-patterns to avoid**:
- Polling every second (wastes API quota)
- Polling indefinitely (should timeout)
- Polling already-completed checks
- Polling without backoff

### 1.3 Webhook Alternatives

When polling is not ideal, use GitHub webhooks:

**Relevant webhook events**:
- `check_run` - Individual check status changes
- `check_suite` - Suite completion
- `status` - Legacy status API changes
- `pull_request` - PR state changes

**Webhook payload for check_run**:
```json
{
  "action": "completed",
  "check_run": {
    "id": 123456,
    "name": "build",
    "status": "completed",
    "conclusion": "success",
    "pull_requests": [{"number": 42}]
  }
}
```

**Hybrid approach**: Use webhooks for notification, poll as fallback:
```python
# Webhook handler marks check as complete
# Background worker polls for any missed updates
# Reconcile every 5 minutes
```

---

## 2. Exponential Backoff Implementation

### 2.1 Why Exponential Backoff Matters

**Problems with fixed-interval polling**:
- Wastes API quota during long builds
- Unnecessary load on GitHub servers
- May hit rate limits (5000 requests/hour for authenticated)
- Inefficient resource usage

**Benefits of exponential backoff**:
- Efficient API usage
- Respects server resources
- Automatically adapts to check duration
- Reduces rate limit risk

### 2.2 Recommended Backoff Parameters

**Standard parameters for PR check polling**:

| Parameter | Recommended Value | Rationale |
|-----------|------------------|-----------|
| Initial interval | 10 seconds | Catches quick checks |
| Maximum interval | 120 seconds | Balances freshness/efficiency |
| Multiplier | 1.5 | Gradual increase |
| Maximum attempts | 60 | ~30 min total with backoff |

**Implementation formula**:
```
interval = min(initial * (multiplier ^ attempt), max_interval)
```

**Example progression** (initial=10, multiplier=1.5, max=120):
```
Attempt 1:  10 seconds
Attempt 2:  15 seconds
Attempt 3:  22 seconds
Attempt 4:  34 seconds
Attempt 5:  51 seconds
Attempt 6:  76 seconds
Attempt 7:  114 seconds
Attempt 8+: 120 seconds (capped)
```

**Python implementation**:
```python
import time

def poll_with_backoff(check_fn, initial=10, multiplier=1.5, max_interval=120, max_attempts=60):
    """
    Poll with exponential backoff until check_fn returns True or max_attempts reached.

    Args:
        check_fn: Callable that returns (done: bool, result: any)
        initial: Initial wait interval in seconds
        multiplier: Backoff multiplier
        max_interval: Maximum wait interval
        max_attempts: Maximum number of attempts

    Returns:
        Final result from check_fn
    """
    interval = initial
    for attempt in range(max_attempts):
        done, result = check_fn()
        if done:
            return result

        time.sleep(interval)
        interval = min(interval * multiplier, max_interval)

    raise TimeoutError(f"Polling timed out after {max_attempts} attempts")
```

### 2.3 Jitter for Distributed Systems

When multiple agents poll simultaneously, add jitter to prevent thundering herd:

**Jitter formula**:
```
actual_interval = interval * (0.5 + random() * 0.5)
```

This provides 50-100% of the calculated interval.

**Why jitter helps**:
- Spreads requests over time
- Reduces simultaneous API calls
- Prevents correlated failures
- Improves overall system stability

**Full implementation with jitter**:
```python
import random
import time

def poll_with_jitter(check_fn, initial=10, multiplier=1.5, max_interval=120, max_attempts=60):
    interval = initial
    for attempt in range(max_attempts):
        done, result = check_fn()
        if done:
            return result

        # Add jitter: 50-100% of interval
        jittered = interval * (0.5 + random.random() * 0.5)
        time.sleep(jittered)
        interval = min(interval * multiplier, max_interval)

    raise TimeoutError("Polling timed out")
```

---

## 3. Timeout Handling

### 3.1 Setting Appropriate Timeouts

**Factors affecting timeout choice**:

| Factor | Impact on Timeout |
|--------|-------------------|
| Project build time | Longer builds need longer timeout |
| Test suite size | Large suites need more time |
| External dependencies | Flaky deps need buffer |
| Historical duration | Base on p95 of past runs |
| CI runner speed | Self-hosted may be slower |

**Recommended timeouts by project type**:

| Project Type | Recommended Timeout |
|--------------|---------------------|
| Simple library (tests only) | 10-15 minutes |
| Web application (build + test) | 20-30 minutes |
| Monorepo (multiple workflows) | 45-60 minutes |
| Large project (extensive CI) | 60-90 minutes |

**Calculating timeout from history**:
```bash
# Get recent workflow run durations
gh run list --limit 50 --json durationMs \
  --jq '[.[].durationMs] | (sort | .[length * 0.95 | floor]) / 60000'
```

### 3.2 Graceful Timeout Behavior

When timeout occurs, the script should:

1. **Report current state**: Show which checks are pending
2. **Provide actionable info**: Include links to check logs
3. **Exit with distinct code**: Use exit code 2 for timeout
4. **Not fail silently**: Always produce output

**Timeout response structure**:
```json
{
  "timed_out": true,
  "completed": false,
  "wait_time_seconds": 1800,
  "pending_checks": [
    {
      "name": "integration-tests",
      "status": "in_progress",
      "started_at": "2024-01-15T10:00:00Z",
      "details_url": "https://github.com/..."
    }
  ],
  "completed_checks": {
    "passing": 4,
    "failing": 0
  },
  "message": "Timeout after 30 minutes. 1 check still pending."
}
```

### 3.3 Partial Completion Scenarios

Handle cases where some checks complete while others are stuck:

**Scenario 1: Most checks pass, one stuck**
- Action: Report timeout, show stuck check
- Decision: May allow manual merge override

**Scenario 2: Some checks fail, others pending**
- Action: Could exit early (already know PR won't pass)
- Optimization: `--fail-fast` flag to stop on first failure

**Scenario 3: Checks never start**
- Cause: Runner unavailable, workflow syntax error
- Action: Alert, check GitHub Actions status

**Early exit implementation**:
```python
def wait_for_checks(pr_number, timeout, fail_fast=False):
    """Wait for checks, optionally exiting early on failure."""
    start = time.time()

    while time.time() - start < timeout:
        checks = get_pr_checks(pr_number)

        # Exit early if any check failed (when fail_fast=True)
        if fail_fast and any(c['conclusion'] == 'failure' for c in checks):
            return {'completed': True, 'status': 'failure', 'early_exit': True}

        # Check if all done
        if all(c['status'] == 'completed' for c in checks):
            return {'completed': True, 'status': determine_status(checks)}

        time.sleep(get_backoff_interval())

    return {'completed': False, 'timed_out': True}
```

---

## 4. Partial Success Scenarios

### 4.1 Handling Mixed Results

When checks have mixed results (some pass, some fail, some skipped):

**Classification**:
```python
def classify_checks(checks):
    """Classify checks into categories for decision making."""
    return {
        'passing': [c for c in checks if c['conclusion'] == 'success'],
        'failing': [c for c in checks if c['conclusion'] == 'failure'],
        'pending': [c for c in checks if c['status'] != 'completed'],
        'skipped': [c for c in checks if c['conclusion'] == 'skipped'],
        'neutral': [c for c in checks if c['conclusion'] == 'neutral'],
        'other': [c for c in checks if c['conclusion'] in
                  ['cancelled', 'timed_out', 'action_required']]
    }
```

**Decision matrix**:

| Required Failing | Optional Failing | Pending | Action |
|------------------|------------------|---------|--------|
| 0 | 0 | 0 | Safe to merge |
| 0 | 1+ | 0 | Merge with warning |
| 1+ | Any | Any | Block merge |
| 0 | Any | 1+ | Wait for pending |

### 4.2 Re-running Failed Checks

**When to re-run**:
- Flaky test (intermittent failure)
- Infrastructure issue (runner problem)
- Timeout (resource contention)

**When NOT to re-run**:
- Genuine code failure
- Security vulnerability found
- Deliberate test coverage gap

**Re-run implementation**:
```bash
# Re-run a specific check run
gh api repos/OWNER/REPO/check-runs/CHECK_RUN_ID/rerequest -X POST

# Re-run failed jobs in a workflow
gh run rerun RUN_ID --failed

# Re-run entire workflow
gh run rerun RUN_ID
```

**Automated re-run strategy**:
```python
def handle_failed_check(check, max_retries=1):
    """Re-run failed check if eligible."""
    # Don't retry genuine failures
    if check['conclusion'] == 'failure':
        # Check if it's a flaky test pattern
        if 'flaky' in check['name'].lower():
            return rerun_check(check['id'])

    # Retry infrastructure issues
    if check['conclusion'] in ['timed_out', 'startup_failure']:
        if check.get('retry_count', 0) < max_retries:
            return rerun_check(check['id'])

    return False
```

### 4.3 Determining Merge Readiness with Failures

**Merge readiness algorithm**:

```python
def is_merge_ready(pr_number, allow_optional_failures=False):
    """
    Determine if PR is ready to merge based on check status.

    Args:
        pr_number: Pull request number
        allow_optional_failures: If True, only required checks must pass

    Returns:
        dict with 'ready', 'reason', and 'details'
    """
    checks = get_pr_checks(pr_number)
    required_checks = get_required_checks(pr_number)

    # Check if any required checks are pending
    pending_required = [c for c in checks
                       if c['name'] in required_checks
                       and c['status'] != 'completed']
    if pending_required:
        return {
            'ready': False,
            'reason': 'required_pending',
            'details': [c['name'] for c in pending_required]
        }

    # Check if any required checks failed
    failed_required = [c for c in checks
                      if c['name'] in required_checks
                      and c['conclusion'] == 'failure']
    if failed_required:
        return {
            'ready': False,
            'reason': 'required_failed',
            'details': [c['name'] for c in failed_required]
        }

    # Check optional failures
    failed_optional = [c for c in checks
                      if c['name'] not in required_checks
                      and c['conclusion'] == 'failure']
    if failed_optional and not allow_optional_failures:
        return {
            'ready': False,
            'reason': 'optional_failed',
            'details': [c['name'] for c in failed_optional]
        }

    return {
        'ready': True,
        'reason': 'all_passing' if not failed_optional else 'required_passing',
        'details': []
    }
```

**Output examples**:

```json
// All passing
{
  "ready": true,
  "reason": "all_passing",
  "details": []
}

// Required failing
{
  "ready": false,
  "reason": "required_failed",
  "details": ["build", "test"]
}

// Optional failing but allowed
{
  "ready": true,
  "reason": "required_passing",
  "details": []
}
```
