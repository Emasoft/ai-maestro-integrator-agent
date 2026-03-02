---
name: op-escalate-failure
description: Follow escalation path when a quality gate fails
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Escalate Gate Failure


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Escalation Paths by Gate](#escalation-paths-by-gate)
- [Severity Levels](#severity-levels)
- [Escalation Path A: Pre-Review Gate Failure](#escalation-path-a-pre-review-gate-failure)
  - [Steps](#steps)
  - [Actions by Failure Type](#actions-by-failure-type)
- [Escalation Path B: Review Gate Failure](#escalation-path-b-review-gate-failure)
  - [Steps](#steps)
  - [Override Authority Matrix](#override-authority-matrix)
- [Escalation Path C: Pre-Merge Gate Failure](#escalation-path-c-pre-merge-gate-failure)
  - [Steps](#steps)
  - [Actions by Failure Type](#actions-by-failure-type)
- [Escalation Path D: Post-Merge Gate Failure (Critical)](#escalation-path-d-post-merge-gate-failure-critical)
  - [Steps](#steps)
  - [Revert Authority Matrix](#revert-authority-matrix)
- [Example: Complete Escalation](#example-complete-escalation)
- [Review Gate Failed - Security Threshold Not Met](#review-gate-failed-security-threshold-not-met)
  - [Security Issues Found](#security-issues-found)
  - [Required Actions](#required-actions)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Follow the appropriate escalation path when a quality gate fails. Ensures proper notification and action based on failure type and severity.

## When to Use

- When any quality gate fails
- When gate failure requires stakeholder notification
- When automated remediation is not possible

## Prerequisites

- Gate failure identified
- Failure reason documented
- Knowledge of escalation paths

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| gate | string | Yes | Which gate failed |
| failure_type | string | Yes | Type of failure |
| severity | string | Yes | critical, high, medium, or low |
| details | string | Yes | Detailed failure description |

## Output

| Field | Type | Description |
|-------|------|-------------|
| escalation_path | string | A, B, C, or D |
| notifications_sent | array | Who was notified |
| actions_taken | array | Immediate actions performed |
| next_steps | array | Required follow-up actions |

## Escalation Paths by Gate

| Gate | Path | Primary Contact |
|------|------|-----------------|
| Pre-Review | A | PR Author |
| Review | B | PR Author + Reviewers |
| Pre-Merge | C | PR Author + Maintainers |
| Post-Merge | D | Maintainers + On-Call |

## Severity Levels

| Severity | Response Time | Action |
|----------|---------------|--------|
| Critical | Immediate | Block merge, notify maintainers |
| High | < 4 hours | Block merge, notify author |
| Medium | < 24 hours | Comment on PR, request changes |
| Low | Best effort | Add warning label |

## Escalation Path A: Pre-Review Gate Failure

### Steps

1. **Apply failure label**
   ```bash
   gh pr edit <NUMBER> --add-label "gate:pre-review-failed"
   ```

2. **Comment with failure details**
   ```bash
   gh pr comment <NUMBER> --body "## Pre-Review Gate Failed

   **Failure Type**: <TYPE>
   **Details**: <DETAILS>

   Please fix the issues and push updated code."
   ```

3. **Notify author** (via GitHub mention)

### Actions by Failure Type

| Failure Type | Action |
|--------------|--------|
| Tests failing | List failing tests, suggest fixes |
| Linting errors | Provide lint output |
| Build failure | Share build logs |
| Missing description | Request PR description |

## Escalation Path B: Review Gate Failure

### Steps

1. **Apply failure label and request changes**
   ```bash
   gh pr edit <NUMBER> --add-label "gate:review-failed"
   gh pr review <NUMBER> --request-changes --body "<REVIEW_COMMENTS>"
   ```

2. **Document findings in review report**

3. **Notify author and assigned reviewers:** Send a message using the `agent-messaging` skill with:
   - **Recipient**: `orchestrator-eoa`
   - **Subject**: `Review Gate Failed: PR #<NUMBER>`
   - **Priority**: `high`
   - **Content**: `{"type": "gate-failure", "message": "PR #<NUMBER> failed review gate. Confidence: XX%. Issues: <SUMMARY>"}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Override Authority Matrix

For urgent cases, overrides may be requested:

| Confidence Score | Override Authority |
|------------------|-------------------|
| 75-79% | Senior Developer |
| 70-74% | Tech Lead |
| 60-69% | Engineering Manager |
| < 60% | No override allowed |

**Note**: Security dimension failures CANNOT be overridden.

## Escalation Path C: Pre-Merge Gate Failure

### Steps

1. **Apply failure label**
   ```bash
   gh pr edit <NUMBER> --add-label "gate:pre-merge-failed"
   ```

2. **Document blocking issue**
   ```bash
   gh pr comment <NUMBER> --body "## Pre-Merge Gate Failed

   **Blocking Issue**: <ISSUE>

   **Required Action**: <ACTION>"
   ```

3. **Notify author and maintainers**

### Actions by Failure Type

| Failure Type | Action |
|--------------|--------|
| Merge conflicts | Author must resolve conflicts |
| CI failure | Investigate and fix or re-run |
| Approval invalid | Request re-review |
| Branch outdated | Update branch with base |

## Escalation Path D: Post-Merge Gate Failure (Critical)

### Steps

1. **Apply failure label**
   ```bash
   gh pr edit <NUMBER> --add-label "gate:post-merge-failed"
   ```

2. **Assess severity and rollback need**

3. **Notify maintainers immediately:** Send a message using the `agent-messaging` skill with:
   - **Recipient**: `orchestrator-eoa`
   - **Subject**: `[CRITICAL] Post-Merge Failure: PR #<NUMBER>`
   - **Priority**: `urgent`
   - **Content**: `{"type": "post-merge-failure", "message": "CRITICAL: PR #<NUMBER> broke main branch. Immediate action required."}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

4. **Initiate revert if necessary**
   ```bash
   git revert <MERGE_COMMIT>
   gh pr create --title "Revert PR #<NUMBER>" --body "Emergency revert due to main branch failure"
   ```

### Revert Authority Matrix

| Condition | Authority |
|-----------|-----------|
| Build broken | Any maintainer |
| Tests failing (new) | Any maintainer |
| Security vulnerability | Security team |
| Performance degradation | Tech lead approval |

## Example: Complete Escalation

```bash
# Gate: Review
# Failure: Security score 65% (below 70% threshold)

# Step 1: Apply labels
gh pr edit 123 --add-label "gate:review-failed"

# Step 2: Request changes with details
gh pr review 123 --request-changes --body "$(cat <<'EOF'
## Review Gate Failed - Security Threshold Not Met

**Security Dimension Score**: 65% (Required: 70%)

### Security Issues Found

1. **SQL Injection Risk** (Critical)
   - File: `src/db/queries.py:42`
   - Issue: User input not sanitized before query

2. **Hardcoded Credentials** (High)
   - File: `config/settings.py:15`
   - Issue: API key hardcoded in source

### Required Actions
- [ ] Use parameterized queries for all database operations
- [ ] Move credentials to environment variables

**Note**: Security failures cannot be overridden.
EOF
)"

# Step 3: Notify via AI Maestro
# Send a message using the agent-messaging skill with:
#   Recipient: orchestrator-eoa
#   Subject: Security Gate Failure: PR #123
#   Priority: high
#   Content: {"type": "security-gate-failure", "message": "PR #123 failed security gate (65%). SQL injection and hardcoded credentials found. Requires fixes before merge."}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.
```

## Error Handling

| Error | Action |
|-------|--------|
| Cannot reach stakeholder | Use alternate contact, document attempts |
| Override requested but not authorized | Document denial, escalate to higher authority |
| Revert fails | Manual intervention required, alert on-call |

## Related Operations

- [op-execute-pre-review-gate.md](op-execute-pre-review-gate.md) - Path A trigger
- [op-execute-review-gate.md](op-execute-review-gate.md) - Path B trigger
- [op-execute-pre-merge-gate.md](op-execute-pre-merge-gate.md) - Path C trigger
- [op-execute-post-merge-gate.md](op-execute-post-merge-gate.md) - Path D trigger
- [op-process-override.md](op-process-override.md) - Override handling
