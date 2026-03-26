---
name: op-load-pr-memory
description: "Load PR review state from GitHub PR comments"
procedure: support-skill
workflow-instruction: support
---

# Operation: Load PR Memory

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify PR exists and is accessible](#step-1-verify-pr-exists-and-is-accessible)
  - [Step 2: Fetch PR comments](#step-2-fetch-pr-comments)
  - [Step 3: Find AMIA state comment](#step-3-find-amia-state-comment)
  - [Step 4: Parse state from comment](#step-4-parse-state-from-comment)
  - [Step 5: Extract state fields](#step-5-extract-state-fields)
  - [Step 6: Verify state freshness](#step-6-verify-state-freshness)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [State Comment Format](#state-comment-format)
- [AMIA Review State](#amia-review-state)
- [State Fields](#state-fields)
- [Error Handling](#error-handling)
  - [PR not found](#pr-not-found)
  - [No state comment found](#no-state-comment-found)
  - [Invalid state JSON](#invalid-state-json)
  - [State is stale](#state-is-stale)
- [Verification](#verification)

## Purpose

Retrieve session state that was stored in GitHub PR comments from a previous session, enabling continuation of PR review work.

## When to Use

- Resuming a PR review that was started in a previous session
- After context compaction when PR review state needs restoration
- When another agent handed off PR review work

## Prerequisites

1. GitHub CLI authenticated (`gh auth status`)
2. PR number is known
3. Read access to PR comments

## Procedure

### Step 1: Verify PR exists and is accessible

```bash
PR_NUM=123

# Check PR exists
gh pr view "$PR_NUM" --json number,state,title > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Cannot access PR #$PR_NUM"
  exit 1
fi
```

### Step 2: Fetch PR comments

```bash
# Get all comments on the PR
PR_COMMENTS=$(gh pr view "$PR_NUM" --comments --json comments)
```

### Step 3: Find AMIA state comment

```bash
# Extract AMIA session state from comments
STATE_COMMENT=$(echo "$PR_COMMENTS" | jq -r '
  .comments[]
  | select(.body | contains("AMIA-SESSION-STATE"))
  | .body
')

if [ -z "$STATE_COMMENT" ]; then
  echo "No AMIA session state found in PR comments"
  exit 0  # Not an error - may be new review
fi
```

### Step 4: Parse state from comment

```bash
# Extract JSON from HTML comment marker
STATE_JSON=$(echo "$STATE_COMMENT" | grep -oP '(?<=<!-- AMIA-SESSION-STATE ).*(?= -->)')

# Parse as JSON
STATE=$(echo "$STATE_JSON" | jq '.')
if [ $? -ne 0 ]; then
  echo "Failed to parse state JSON"
  exit 1
fi
```

### Step 5: Extract state fields

```bash
# Get state fields
PR_STATUS=$(echo "$STATE" | jq -r '.status')
LAST_REVIEWED=$(echo "$STATE" | jq -r '.timestamp')
PATTERNS_OBSERVED=$(echo "$STATE" | jq -r '.patterns_observed // []')
BLOCKERS=$(echo "$STATE" | jq -r '.blockers // []')
NEXT_STEPS=$(echo "$STATE" | jq -r '.next_steps // ""')

echo "PR Review State:"
echo "  Status: $PR_STATUS"
echo "  Last Reviewed: $LAST_REVIEWED"
echo "  Patterns: $PATTERNS_OBSERVED"
```

### Step 6: Verify state freshness

```bash
# Compare state timestamp with PR activity
PR_UPDATED=$(gh pr view "$PR_NUM" --json updatedAt --jq '.updatedAt')
STATE_TS=$(echo "$STATE" | jq -r '.timestamp')

# If PR updated after state, warn about potential staleness
if [[ "$PR_UPDATED" > "$STATE_TS" ]]; then
  echo "WARNING: PR was updated after last review state"
  echo "  State: $STATE_TS"
  echo "  PR Updated: $PR_UPDATED"
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pr_number | number | yes | The PR number to load state for |
| verify_freshness | boolean | no | Whether to check for PR updates |

## Output

| Field | Type | Description |
|-------|------|-------------|
| found | boolean | Whether state was found |
| status | string | PR review status |
| timestamp | string | When state was last updated |
| patterns_observed | string[] | Code patterns noted |
| blockers | string[] | Blocking issues identified |
| next_steps | string | Planned next actions |
| stale | boolean | Whether state may be outdated |

## Example Output

```json
{
  "found": true,
  "status": "review_in_progress",
  "timestamp": "2025-02-04T15:42:00Z",
  "patterns_observed": [
    "Error handling inconsistent in middleware",
    "Missing null checks in auth module"
  ],
  "blockers": [],
  "next_steps": "Request changes for error handling",
  "stale": false
}
```

## State Comment Format

The state is stored in PR comments using this format:

```markdown
<!-- AMIA-SESSION-STATE {"pr": 123, "status": "review_in_progress", "timestamp": "2025-02-04T15:42:00Z", "patterns_observed": ["Pattern 1"], "blockers": [], "next_steps": "Continue review"} -->

## AMIA Review State

**Status**: Review in progress
**Last Updated**: 2025-02-04T15:42:00Z
**Patterns Observed**: Error handling inconsistent in middleware
**Blockers**: None
**Next Steps**: Request changes for error handling
```

## State Fields

| Field | Description |
|-------|-------------|
| pr | PR number |
| status | review_pending, review_in_progress, changes_requested, approved, blocked |
| timestamp | ISO 8601 timestamp |
| patterns_observed | Array of code pattern observations |
| blockers | Array of blocking issues |
| next_steps | Description of planned next actions |
| files_reviewed | Array of files already reviewed |
| comments_made | Count or array of review comments |

## Error Handling

### PR not found

**Cause**: PR number doesn't exist or was deleted.

**Solution**: Verify PR number is correct, check repository.

### No state comment found

**Cause**: No previous AMIA review session for this PR.

**Solution**: This is normal for first review - start fresh.

### Invalid state JSON

**Cause**: State comment was corrupted or manually edited.

**Solution**: Ignore corrupted state, start fresh review.

### State is stale

**Cause**: PR was updated after last review session.

**Solution**: Load state but verify changes since last review.

## Verification

After loading state:

```bash
# Verify state is usable
if [ "$FOUND" = "true" ]; then
  echo "Resuming review from status: $STATUS"

  # Check for staleness
  if [ "$STALE" = "true" ]; then
    echo "Note: PR has been updated since last review"
    echo "Recommend re-checking changed files"
  fi

  # Continue from next_steps
  echo "Next action: $NEXT_STEPS"
else
  echo "Starting fresh review"
fi
```
