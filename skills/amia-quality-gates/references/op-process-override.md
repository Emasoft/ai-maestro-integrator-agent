---
name: op-process-override
description: Process gate override requests when authorized
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Process Gate Override


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Override Authority Matrix](#override-authority-matrix)
- [Non-Overridable Conditions](#non-overridable-conditions)
- [Steps](#steps)
  - [Step 1: Verify Override Request](#step-1-verify-override-request)
  - [Step 2: Check Authority Level](#step-2-check-authority-level)
  - [Step 3: Validate Against Authority Matrix](#step-3-validate-against-authority-matrix)
  - [Step 4: Check for Non-Overridable Conditions](#step-4-check-for-non-overridable-conditions)
  - [Step 5: Document Override](#step-5-document-override)
- [Gate Override Applied](#gate-override-applied)
  - [Justification](#justification)
  - [Override Conditions](#override-conditions)
  - [Follow-up Required](#follow-up-required)
  - [Tracking](#tracking)
  - [Step 6: Apply Override Label](#step-6-apply-override-label)
  - [Step 7: Advance to Next Gate](#step-7-advance-to-next-gate)
  - [Step 8: Log Override for Audit](#step-8-log-override-for-audit)
- [Override Request Template](#override-request-template)
- [Override Request](#override-request)
  - [Justification](#justification)
  - [Risk Assessment](#risk-assessment)
  - [Follow-up Commitment](#follow-up-commitment)
  - [Requested By](#requested-by)
- [Example: Approved Override](#example-approved-override)
- [Gate Override Applied](#gate-override-applied)
  - [Justification](#justification)
  - [Override Conditions](#override-conditions)
  - [Follow-up Required](#follow-up-required)
  - [Tracking](#tracking)
- [Example: Denied Override](#example-denied-override)
- [Override Request DENIED](#override-request-denied)
  - [Denial Reason](#denial-reason)
  - [Required Action](#required-action)
  - [Security Issues to Fix](#security-issues-to-fix)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Handle authorized gate override requests that allow PRs to proceed despite not meeting standard thresholds. Overrides require proper authorization and documentation.

## When to Use

- When an authorized override is requested
- When urgency requires bypassing normal thresholds
- When business justification outweighs technical concerns

## Prerequisites

- Gate failure documented
- Override request received
- Override authority verified

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| gate | string | Yes | Which gate to override |
| requester | string | Yes | Who requested the override |
| justification | string | Yes | Business justification |
| authority_level | string | Yes | Authorization level |

## Output

| Field | Type | Description |
|-------|------|-------------|
| override_approved | boolean | Whether override was granted |
| override_id | string | Unique override identifier |
| conditions | array | Any conditions attached |
| follow_up_required | array | Required follow-up actions |

## Override Authority Matrix

| Gate | Confidence Score | Required Authority |
|------|------------------|-------------------|
| Pre-Review | Any | Tech Lead |
| Review | 75-79% | Senior Developer |
| Review | 70-74% | Tech Lead |
| Review | 60-69% | Engineering Manager |
| Review | < 60% | **NO OVERRIDE** |
| Pre-Merge | CI flaky | Senior Developer |
| Pre-Merge | Conflicts | Tech Lead |

## Non-Overridable Conditions

**These conditions CANNOT be overridden under any circumstances:**

| Condition | Reason |
|-----------|--------|
| Security score < 70% | Security vulnerabilities must be fixed |
| Known vulnerability | Cannot ship known security issues |
| Data loss risk | Cannot risk user data |
| Compliance violation | Legal/regulatory requirements |

## Steps

### Step 1: Verify Override Request

Confirm:
- Request is from authorized source
- Justification is provided
- Override is for an overridable condition

### Step 2: Check Authority Level

```bash
# Get requester's role (mock - actual implementation varies)
REQUESTER_ROLE=$(get_user_role "$REQUESTER")

# Map to authority level
case "$REQUESTER_ROLE" in
    "maintainer"|"admin") AUTHORITY="engineering-manager" ;;
    "senior") AUTHORITY="tech-lead" ;;
    "member") AUTHORITY="senior-developer" ;;
    *) AUTHORITY="none" ;;
esac
```

### Step 3: Validate Against Authority Matrix

Check if requester's authority level meets the requirement for the specific override.

### Step 4: Check for Non-Overridable Conditions

If any non-overridable condition exists, DENY the override:

```bash
# Check for security failures
if [ "$SECURITY_SCORE" -lt 70 ]; then
    echo "DENIED: Security failures cannot be overridden"
    exit 1
fi
```

### Step 5: Document Override

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## Gate Override Applied

**Gate**: <GATE_NAME>
**Date**: <TIMESTAMP>
**Requested By**: @<REQUESTER>
**Authorized By**: @<AUTHORIZER>

### Justification
<JUSTIFICATION_TEXT>

### Override Conditions
- [ ] <CONDITION_1>
- [ ] <CONDITION_2>

### Follow-up Required
- <FOLLOW_UP_ACTION_1>
- <FOLLOW_UP_ACTION_2>

### Tracking
- Override ID: <OVERRIDE_ID>
- Expires: <EXPIRY_IF_APPLICABLE>

**Note**: This override has been logged for audit purposes.
EOF
)"
```

### Step 6: Apply Override Label

```bash
gh pr edit <NUMBER> --add-label "gate:override-applied"
```

### Step 7: Advance to Next Gate

```bash
# Remove failed label, add passed label
gh pr edit <NUMBER> \
    --remove-label "gate:<GATE>-failed" \
    --add-label "gate:<GATE>-passed"
```

### Step 8: Log Override for Audit

Record override in audit log (implementation varies by organization).

## Override Request Template

```markdown
## Override Request

**PR**: #<NUMBER>
**Gate**: <GATE_NAME>
**Current Status**: Failed (XX%)

### Justification
<WHY_OVERRIDE_IS_NEEDED>

### Risk Assessment
- **Business Risk of Delay**: <DESCRIPTION>
- **Technical Risk of Override**: <DESCRIPTION>
- **Mitigation Plan**: <DESCRIPTION>

### Follow-up Commitment
- [ ] Will address issues in follow-up PR by <DATE>
- [ ] Will monitor for issues post-merge
- [ ] Accepts responsibility for any issues

### Requested By
@<USERNAME> - <ROLE>
```

## Example: Approved Override

```bash
# Scenario: Review gate at 77%, deadline critical
# Requester: Tech Lead
# Authority: Sufficient for 75-79% range

# Document the override
gh pr comment 123 --body "$(cat <<'EOF'
## Gate Override Applied

**Gate**: Review Gate
**Date**: 2025-02-05T15:00:00Z
**Requested By**: @tech-lead
**Authorized By**: @tech-lead (self-authorized per matrix)

### Justification
Critical hotfix for production issue affecting 1000+ users.
Confidence score 77% is due to documentation dimension (not updated).
All security and functionality checks pass.

### Override Conditions
- [x] Security dimension >= 70% (Score: 85%)
- [x] Functional dimension >= 70% (Score: 88%)
- [x] No known vulnerabilities

### Follow-up Required
- Update documentation in follow-up PR within 48 hours
- Monitor error rates post-deploy

### Tracking
- Override ID: OVR-2025-0205-001
- Follow-up Due: 2025-02-07
EOF
)"

# Apply labels
gh pr edit 123 \
    --add-label "gate:override-applied" \
    --remove-label "gate:review-failed" \
    --add-label "gate:review-passed"
```

## Example: Denied Override

```bash
# Scenario: Security score 62%
# This is non-overridable

gh pr comment 123 --body "$(cat <<'EOF'
## Override Request DENIED

**Gate**: Review Gate
**Requested By**: @developer

### Denial Reason
Security dimension score (62%) is below the non-overridable threshold of 70%.

**Security failures cannot be overridden under any circumstances.**

### Required Action
Address the security issues identified in the review and request re-review.

### Security Issues to Fix
1. SQL injection vulnerability in auth.py
2. Missing input validation in upload handler
3. Hardcoded credentials in config

These must be resolved before the PR can proceed.
EOF
)"
```

## Error Handling

| Error | Action |
|-------|--------|
| Unauthorized requester | Deny, suggest proper authority |
| Non-overridable condition | Deny, explain why |
| Missing justification | Request justification before processing |
| Insufficient documentation | Request more detail |

## Related Operations

- [op-escalate-failure.md](op-escalate-failure.md) - May lead to override request
- [override-policies.md](override-policies.md) - Complete policy reference
