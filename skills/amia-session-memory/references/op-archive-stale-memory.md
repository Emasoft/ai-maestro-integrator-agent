# Operation: Archive Stale Memory

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify stale memory sources](#step-1-identify-stale-memory-sources)
  - [Step 2: Check handoff document staleness](#step-2-check-handoff-document-staleness)
  - [Step 3: Check PR state (if PR-related)](#step-3-check-pr-state-if-pr-related)
  - [Step 4: Archive handoff document](#step-4-archive-handoff-document)
  - [Step 5: Archive session state JSON](#step-5-archive-session-state-json)
  - [Step 6: Clean up PR state comments (optional)](#step-6-clean-up-pr-state-comments-optional)
  - [Step 7: Report archival actions](#step-7-report-archival-actions)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Staleness Criteria](#staleness-criteria)
- [Archive Structure](#archive-structure)
- [Error Handling](#error-handling)
  - [Archive directory not writable](#archive-directory-not-writable)
  - [File move fails](#file-move-fails)
  - [PR lookup fails](#pr-lookup-fails)
- [Complete Archive Script](#complete-archive-script)
- [Verification](#verification)

## Purpose

Move outdated or no-longer-relevant memory state to an archive location, preventing it from being incorrectly loaded in future sessions.

## When to Use

- When memory is older than threshold (default: 7 days)
- When PR has been merged/closed
- When release has been completed
- When task has been cancelled
- During periodic maintenance

## Prerequisites

1. `$CLAUDE_PROJECT_DIR` environment variable set
2. Write access to handoff and archive directories
3. Knowledge of what makes memory "stale"

## Procedure

### Step 1: Identify stale memory sources

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
ARCHIVE_DIR="$HANDOFF_DIR/archive"
STALE_THRESHOLD_DAYS=7

# Create archive directory if needed
mkdir -p "$ARCHIVE_DIR"

# Find stale files by modification time
find "$HANDOFF_DIR" -maxdepth 1 -name "*.md" -mtime +$STALE_THRESHOLD_DAYS -type f
```

### Step 2: Check handoff document staleness

```bash
CURRENT_HANDOFF="$HANDOFF_DIR/current.md"

if [ -f "$CURRENT_HANDOFF" ]; then
  # Extract last updated timestamp
  LAST_UPDATED=$(grep -oP '(?<=\*\*Last Updated\*\*: ).*' "$CURRENT_HANDOFF")

  # Calculate age
  if [ -n "$LAST_UPDATED" ]; then
    LAST_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$LAST_UPDATED" "+%s" 2>/dev/null || date -d "$LAST_UPDATED" "+%s")
    NOW_EPOCH=$(date "+%s")
    AGE_DAYS=$(( (NOW_EPOCH - LAST_EPOCH) / 86400 ))

    if [ $AGE_DAYS -gt $STALE_THRESHOLD_DAYS ]; then
      echo "Handoff is stale ($AGE_DAYS days old)"
      ARCHIVE_HANDOFF=true
    fi
  fi
fi
```

### Step 3: Check PR state (if PR-related)

```bash
# Extract PR number from handoff
PR_URL=$(grep -oP 'https://github.com/[^/]+/[^/]+/pull/\d+' "$CURRENT_HANDOFF" | head -1)
if [ -n "$PR_URL" ]; then
  PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')

  # Check PR state
  PR_STATE=$(gh pr view "$PR_NUMBER" --json state --jq '.state')

  if [ "$PR_STATE" = "MERGED" ] || [ "$PR_STATE" = "CLOSED" ]; then
    echo "PR is $PR_STATE - memory is stale"
    ARCHIVE_HANDOFF=true
  fi
fi
```

### Step 4: Archive handoff document

```bash
if [ "$ARCHIVE_HANDOFF" = "true" ]; then
  ARCHIVE_TS=$(date +%Y%m%d_%H%M%S)
  ARCHIVE_NAME="handoff_${ARCHIVE_TS}.md"

  mv "$CURRENT_HANDOFF" "$ARCHIVE_DIR/$ARCHIVE_NAME"
  echo "Archived handoff to $ARCHIVE_DIR/$ARCHIVE_NAME"
fi
```

### Step 5: Archive session state JSON

```bash
STATE_FILE="$HANDOFF_DIR/session_state.json"

if [ -f "$STATE_FILE" ]; then
  # Check state age
  STATE_TS=$(cat "$STATE_FILE" | jq -r '.last_updated // .started_at')

  if [ -n "$STATE_TS" ]; then
    STATE_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$STATE_TS" "+%s" 2>/dev/null)
    NOW_EPOCH=$(date "+%s")
    STATE_AGE_DAYS=$(( (NOW_EPOCH - STATE_EPOCH) / 86400 ))

    if [ $STATE_AGE_DAYS -gt $STALE_THRESHOLD_DAYS ]; then
      mv "$STATE_FILE" "$ARCHIVE_DIR/session_state_${ARCHIVE_TS}.json"
      echo "Archived session state"
    fi
  fi
fi
```

### Step 6: Clean up PR state comments (optional)

```bash
# For merged/closed PRs, the state comment can be removed
if [ "$PR_STATE" = "MERGED" ] || [ "$PR_STATE" = "CLOSED" ]; then
  # Find and delete AMIA state comment
  COMMENT_ID=$(gh pr view "$PR_NUMBER" --comments --json comments | jq -r '
    .comments[]
    | select(.body | contains("AMIA-SESSION-STATE"))
    | .id
  ' | head -1)

  if [ -n "$COMMENT_ID" ]; then
    # Note: Deletion is optional - may want to keep for history
    # gh api -X DELETE "/repos/{owner}/{repo}/issues/comments/$COMMENT_ID"
    echo "PR state comment could be removed: $COMMENT_ID"
  fi
fi
```

### Step 7: Report archival actions

```json
{
  "archived_files": [
    "handoff_20250205_143000.md",
    "session_state_20250205_143000.json"
  ],
  "reason": "PR #123 merged",
  "archive_location": "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/archive/"
}
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| stale_threshold_days | number | no | Days before considering stale (default: 7) |
| check_pr_state | boolean | no | Whether to check PR merged/closed status |
| delete_pr_comments | boolean | no | Whether to delete PR state comments |
| dry_run | boolean | no | Preview without making changes |

## Output

| Field | Type | Description |
|-------|------|-------------|
| files_archived | string[] | List of files moved to archive |
| comments_removed | string[] | List of PR comments removed |
| reason | string | Why memory was archived |
| dry_run | boolean | Whether this was a preview |

## Example Output

```json
{
  "files_archived": [
    "handoff_20250205_143000.md",
    "session_state_20250205_143000.json"
  ],
  "comments_removed": [],
  "reason": "Age exceeds 7 days and PR #123 is MERGED",
  "dry_run": false
}
```

## Staleness Criteria

| Source | Stale Condition |
|--------|-----------------|
| Handoff document | Age > 7 days |
| Session state | Age > 7 days |
| PR state comment | PR is MERGED or CLOSED |
| Release history | Never (keep all releases) |
| Patterns learned | Never (accumulating knowledge) |

## Archive Structure

```
$HANDOFF_DIR/archive/
  handoff_20250201_100000.md
  handoff_20250205_143000.md
  session_state_20250201_100000.json
  session_state_20250205_143000.json
```

## Error Handling

### Archive directory not writable

**Cause**: Permission denied.

**Solution**: Check directory permissions.

### File move fails

**Cause**: Source or destination issue.

**Solution**: Check paths and permissions.

### PR lookup fails

**Cause**: Network or auth issue.

**Solution**: Skip PR state check, use age only.

## Complete Archive Script

```bash
#!/bin/bash
# archive_stale_memory.sh

HANDOFF_DIR="${1:-$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration}"
THRESHOLD_DAYS="${2:-7}"
DRY_RUN="${3:-false}"

ARCHIVE_DIR="$HANDOFF_DIR/archive"
ARCHIVE_TS=$(date +%Y%m%d_%H%M%S)

echo "=== Archiving Stale Memory ==="
echo "Threshold: $THRESHOLD_DAYS days"

mkdir -p "$ARCHIVE_DIR"

# Check current.md
CURRENT="$HANDOFF_DIR/current.md"
if [ -f "$CURRENT" ]; then
  FILE_AGE=$(( ($(date +%s) - $(stat -f %m "$CURRENT")) / 86400 ))
  if [ $FILE_AGE -gt $THRESHOLD_DAYS ]; then
    echo "Handoff is $FILE_AGE days old - stale"
    if [ "$DRY_RUN" = "false" ]; then
      mv "$CURRENT" "$ARCHIVE_DIR/handoff_$ARCHIVE_TS.md"
      echo "Archived: current.md"
    else
      echo "[DRY RUN] Would archive: current.md"
    fi
  fi
fi

# Check session_state.json
STATE="$HANDOFF_DIR/session_state.json"
if [ -f "$STATE" ]; then
  FILE_AGE=$(( ($(date +%s) - $(stat -f %m "$STATE")) / 86400 ))
  if [ $FILE_AGE -gt $THRESHOLD_DAYS ]; then
    echo "Session state is $FILE_AGE days old - stale"
    if [ "$DRY_RUN" = "false" ]; then
      mv "$STATE" "$ARCHIVE_DIR/session_state_$ARCHIVE_TS.json"
      echo "Archived: session_state.json"
    else
      echo "[DRY RUN] Would archive: session_state.json"
    fi
  fi
fi

echo "=== Archive Complete ==="
```

## Verification

After archiving:

```bash
# Verify files were moved
ls -la "$ARCHIVE_DIR/"

# Verify current directory is clean
ls -la "$HANDOFF_DIR/" | grep -v archive

# Check archive count
echo "Total archived files: $(ls -1 "$ARCHIVE_DIR/" | wc -l)"
```
