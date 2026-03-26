# Operation: Save PR State Comment

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Prepare state data](#step-1-prepare-state-data)
  - [Step 2: Build comment body](#step-2-build-comment-body)
- [AMIA Review State](#amia-review-state)
  - [Patterns Observed](#patterns-observed)
  - [Blockers](#blockers)
  - [Next Steps](#next-steps)
  - [Step 3: Check for existing state comment](#step-3-check-for-existing-state-comment)
  - [Step 4: Update or create comment](#step-4-update-or-create-comment)
  - [Step 5: Verify comment was saved](#step-5-verify-comment-was-saved)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [State Comment Format](#state-comment-format)
- [AMIA Review State](#amia-review-state)
  - [Patterns Observed](#patterns-observed)
  - [Blockers](#blockers)
  - [Next Steps](#next-steps)
- [Status Values](#status-values)
- [Error Handling](#error-handling)
  - [Permission denied](#permission-denied)
  - [PR not found](#pr-not-found)
  - [Comment too long](#comment-too-long)
  - [Update failed](#update-failed)
- [Complete Save Script](#complete-save-script)
- [AMIA Review State](#amia-review-state)
  - [Patterns Observed](#patterns-observed)
  - [Next Steps](#next-steps)
- [Verification](#verification)

## Purpose

Persist the current PR review session state as a comment on the GitHub PR, enabling state recovery in future sessions.

## When to Use

- Before ending a PR review session
- After completing significant review milestones
- Before context compaction during long reviews
- When handing off PR review to another session

## Prerequisites

1. GitHub CLI authenticated with write access
2. PR number known
3. State data prepared for persistence

## Procedure

### Step 1: Prepare state data

```bash
PR_NUMBER=123
STATUS="review_in_progress"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build state JSON
STATE_JSON=$(jq -n \
  --arg pr "$PR_NUMBER" \
  --arg status "$STATUS" \
  --arg ts "$TIMESTAMP" \
  --argjson patterns '["Pattern 1", "Pattern 2"]' \
  --argjson blockers '[]' \
  --arg next "Continue middleware review" \
  '{
    pr: ($pr | tonumber),
    status: $status,
    timestamp: $ts,
    patterns_observed: $patterns,
    blockers: $blockers,
    next_steps: $next
  }')
```

### Step 2: Build comment body

```bash
COMMENT_BODY="<!-- AMIA-SESSION-STATE $STATE_JSON -->

## AMIA Review State

**Status**: $STATUS
**Last Updated**: $TIMESTAMP

### Patterns Observed
$(echo "$STATE_JSON" | jq -r '.patterns_observed[]' | sed 's/^/- /')

### Blockers
$(echo "$STATE_JSON" | jq -r 'if .blockers | length > 0 then .blockers[] else "None" end' | sed 's/^/- /')

### Next Steps
$(echo "$STATE_JSON" | jq -r '.next_steps')

---
*This comment is automatically maintained by AMIA session memory.*"
```

### Step 3: Check for existing state comment

```bash
# Find existing AMIA state comment
EXISTING_COMMENT=$(gh pr view "$PR_NUMBER" --comments --json comments | jq -r '
  .comments[]
  | select(.body | contains("AMIA-SESSION-STATE"))
  | .id
' | head -1)
```

### Step 4: Update or create comment

```bash
if [ -n "$EXISTING_COMMENT" ]; then
  # Update existing comment
  gh api \
    -X PATCH \
    "/repos/{owner}/{repo}/issues/comments/$EXISTING_COMMENT" \
    -f body="$COMMENT_BODY"
  echo "Updated existing state comment"
else
  # Create new comment
  gh pr comment "$PR_NUMBER" --body "$COMMENT_BODY"
  echo "Created new state comment"
fi
```

### Step 5: Verify comment was saved

```bash
# Verify state is retrievable
VERIFY=$(gh pr view "$PR_NUMBER" --comments --json comments | jq -r '
  .comments[]
  | select(.body | contains("AMIA-SESSION-STATE"))
  | .body
' | head -1)

if echo "$VERIFY" | grep -q "$TIMESTAMP"; then
  echo "State saved successfully"
else
  echo "ERROR: State verification failed"
  exit 1
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pr_number | number | yes | PR to add comment to |
| status | string | yes | Review status |
| patterns_observed | string[] | no | Code patterns noted |
| blockers | string[] | no | Blocking issues |
| next_steps | string | no | Planned next actions |
| files_reviewed | string[] | no | Files already reviewed |

## Output

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether comment was saved |
| comment_id | string | ID of the comment |
| action | string | created or updated |
| timestamp | string | When state was saved |

## Example Output

```json
{
  "success": true,
  "comment_id": "IC_kwDOABCDEF12345",
  "action": "updated",
  "timestamp": "2025-02-05T14:30:00Z"
}
```

## State Comment Format

```markdown
<!-- AMIA-SESSION-STATE {"pr": 123, "status": "review_in_progress", "timestamp": "2025-02-05T14:30:00Z", "patterns_observed": ["Inconsistent error handling"], "blockers": [], "next_steps": "Review middleware"} -->

## AMIA Review State

**Status**: review_in_progress
**Last Updated**: 2025-02-05T14:30:00Z

### Patterns Observed
- Inconsistent error handling

### Blockers
- None

### Next Steps
Review middleware

---
*This comment is automatically maintained by AMIA session memory.*
```

## Status Values

| Status | Meaning |
|--------|---------|
| `review_pending` | Review not yet started |
| `review_in_progress` | Actively reviewing |
| `changes_requested` | Review complete, changes needed |
| `approved` | Review complete, approved |
| `blocked` | Review blocked by external issue |

## Error Handling

### Permission denied

**Cause**: Cannot post comments to PR.

**Solution**: Verify GitHub token has write access.

### PR not found

**Cause**: PR number is invalid or PR was deleted.

**Solution**: Verify PR number, check repository.

### Comment too long

**Cause**: State data exceeds GitHub comment limits.

**Solution**: Reduce patterns_observed or split into multiple comments.

### Update failed

**Cause**: Existing comment cannot be updated.

**Solution**: Try deleting and recreating comment.

## Complete Save Script

```bash
#!/bin/bash
# save_pr_state_comment.sh

PR_NUMBER="$1"
STATUS="$2"
PATTERNS="$3"  # JSON array
NEXT_STEPS="$4"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build state JSON
STATE_JSON=$(jq -n \
  --arg pr "$PR_NUMBER" \
  --arg status "$STATUS" \
  --arg ts "$TIMESTAMP" \
  --argjson patterns "$PATTERNS" \
  --arg next "$NEXT_STEPS" \
  '{pr: ($pr | tonumber), status: $status, timestamp: $ts, patterns_observed: $patterns, blockers: [], next_steps: $next}')

# Build comment
COMMENT="<!-- AMIA-SESSION-STATE $STATE_JSON -->

## AMIA Review State

**Status**: $STATUS
**Last Updated**: $TIMESTAMP

### Patterns Observed
$(echo "$PATTERNS" | jq -r '.[]' | sed 's/^/- /')

### Next Steps
$NEXT_STEPS

---
*Automatically maintained by AMIA.*"

# Check for existing
EXISTING=$(gh pr view "$PR_NUMBER" --comments --json comments | jq -r '
  .comments[] | select(.body | contains("AMIA-SESSION-STATE")) | .id
' | head -1)

if [ -n "$EXISTING" ]; then
  gh api -X PATCH "/repos/{owner}/{repo}/issues/comments/$EXISTING" -f body="$COMMENT"
  echo '{"success": true, "action": "updated"}'
else
  gh pr comment "$PR_NUMBER" --body "$COMMENT"
  echo '{"success": true, "action": "created"}'
fi
```

## Verification

After saving:

```bash
# Verify state was saved
gh pr view "$PR_NUMBER" --comments --json comments | jq -r '
  .comments[]
  | select(.body | contains("AMIA-SESSION-STATE"))
  | .body
' | grep -oP '(?<=AMIA-SESSION-STATE ).*(?= -->)'
```
