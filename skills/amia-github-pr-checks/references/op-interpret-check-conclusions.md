---
name: op-interpret-check-conclusions
description: Interpret and act on check conclusion values
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Interpret Check Conclusions


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Conclusion Values Reference](#conclusion-values-reference)
- [Detailed Interpretation](#detailed-interpretation)
  - [success](#success)
  - [failure](#failure)
  - [pending](#pending)
  - [skipped](#skipped)
  - [cancelled](#cancelled)
  - [timed_out](#timed_out)
  - [action_required](#action_required)
  - [neutral](#neutral)
  - [stale](#stale)
- [Decision Matrix](#decision-matrix)
- [Example: Evaluating Check Results](#example-evaluating-check-results)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Understand what each check conclusion value means and determine the appropriate action to take.

## When to Use

- After retrieving check status
- When deciding if PR can proceed
- To understand check failures
- When classifying check results

## Prerequisites

- Check status retrieved
- Understanding of required vs optional checks

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conclusion | string | Yes | The check conclusion value |
| check_name | string | Yes | Name of the check |
| is_required | boolean | No | Whether check is required |

## Output

| Field | Type | Description |
|-------|------|-------------|
| blocking | boolean | Whether this blocks PR merge |
| action_required | boolean | Whether action is needed |
| recommended_action | string | What to do next |
| severity | string | critical, warning, or info |

## Conclusion Values Reference

| Conclusion | Meaning | Blocking | Action |
|------------|---------|----------|--------|
| `success` | Check passed | No | None |
| `failure` | Check failed | Yes (if required) | Investigate and fix |
| `pending` | Still running | Yes (wait) | Wait for completion |
| `skipped` | Intentionally skipped | No | Verify skip is expected |
| `cancelled` | Manually cancelled | Maybe | Determine if re-run needed |
| `timed_out` | Exceeded time limit | Yes | Investigate, increase timeout |
| `action_required` | Manual action needed | Yes | Review check details |
| `neutral` | Informational only | No | Review for insights |
| `stale` | Outdated check | Maybe | Push new commit |

## Detailed Interpretation

### success

```json
{
  "conclusion": "success",
  "interpretation": {
    "blocking": false,
    "action_required": false,
    "severity": "info",
    "recommended_action": "None - check passed"
  }
}
```

### failure

```json
{
  "conclusion": "failure",
  "interpretation": {
    "blocking": true,
    "action_required": true,
    "severity": "critical",
    "recommended_action": "Investigate failure cause, fix issues, push updated code"
  }
}
```

**For required checks**: Blocks merge, must be fixed
**For optional checks**: Warning only, review but may proceed

### pending

```json
{
  "conclusion": "pending",
  "interpretation": {
    "blocking": true,
    "action_required": false,
    "severity": "info",
    "recommended_action": "Wait for check to complete (use op-wait-for-checks)"
  }
}
```

### skipped

```json
{
  "conclusion": "skipped",
  "interpretation": {
    "blocking": false,
    "action_required": false,
    "severity": "info",
    "recommended_action": "Verify skip condition is intentional"
  }
}
```

Common skip reasons:
- Condition not met (e.g., only runs on specific branches)
- Previous job failed
- Manual skip configured

### cancelled

```json
{
  "conclusion": "cancelled",
  "interpretation": {
    "blocking": true,
    "action_required": true,
    "severity": "warning",
    "recommended_action": "Determine if cancellation was intentional, re-run if needed"
  }
}
```

May need re-run if:
- Cancelled due to new push (auto-cancelled)
- Manually cancelled by mistake
- Infrastructure issue caused cancellation

### timed_out

```json
{
  "conclusion": "timed_out",
  "interpretation": {
    "blocking": true,
    "action_required": true,
    "severity": "warning",
    "recommended_action": "Investigate slow tests/build, consider increasing timeout"
  }
}
```

Investigation steps:
1. Check which step timed out
2. Look for slow tests or operations
3. Consider parallelization
4. Increase timeout if justified

### action_required

```json
{
  "conclusion": "action_required",
  "interpretation": {
    "blocking": true,
    "action_required": true,
    "severity": "warning",
    "recommended_action": "Review check details for required manual action"
  }
}
```

Examples:
- Security scan found issues requiring review
- Approval workflow requires sign-off
- License compliance requires acknowledgment

### neutral

```json
{
  "conclusion": "neutral",
  "interpretation": {
    "blocking": false,
    "action_required": false,
    "severity": "info",
    "recommended_action": "Review informational output, no action required"
  }
}
```

Common neutral checks:
- Code coverage reports
- Documentation generators
- Metrics collectors

### stale

```json
{
  "conclusion": "stale",
  "interpretation": {
    "blocking": true,
    "action_required": true,
    "severity": "warning",
    "recommended_action": "Push new commit to trigger fresh check run"
  }
}
```

Causes:
- Check run is from an old commit
- Base branch updated, PR needs rebase
- GitHub marked as stale due to age

## Decision Matrix

| Conclusion | Required Check | Optional Check |
|------------|---------------|----------------|
| success | Proceed | Proceed |
| failure | **BLOCK** | Warning, may proceed |
| pending | Wait | Wait or proceed |
| skipped | Verify intent | Proceed |
| cancelled | Re-run | May proceed |
| timed_out | **BLOCK** | Warning |
| action_required | **BLOCK** | Review |
| neutral | Proceed | Proceed |
| stale | **BLOCK** | Update |

## Example: Evaluating Check Results

```python
def evaluate_conclusion(check):
    """Evaluate a check and determine action."""
    conclusion = check['conclusion']
    is_required = check.get('required', False)

    if conclusion == 'success':
        return {'blocking': False, 'action': 'none'}

    if conclusion == 'failure':
        if is_required:
            return {'blocking': True, 'action': 'fix_required'}
        return {'blocking': False, 'action': 'review_optional'}

    if conclusion == 'pending':
        return {'blocking': True, 'action': 'wait'}

    if conclusion in ['skipped', 'neutral']:
        return {'blocking': False, 'action': 'none'}

    if conclusion == 'timed_out':
        return {'blocking': True, 'action': 'investigate_timeout'}

    if conclusion == 'action_required':
        return {'blocking': True, 'action': 'manual_review'}

    if conclusion in ['cancelled', 'stale']:
        return {'blocking': is_required, 'action': 're_run'}

    return {'blocking': True, 'action': 'unknown_handle_manually'}
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Unknown conclusion value | Treat as blocking, investigate |
| Multiple conflicting conclusions | Use most severe |
| Check missing | Verify CI configuration |

## Related Operations

- [op-get-pr-check-status.md](op-get-pr-check-status.md) - Get check conclusions
- [op-get-check-details.md](op-get-check-details.md) - Investigate failures
- [ci-status-interpretation.md](ci-status-interpretation.md) - Full reference
