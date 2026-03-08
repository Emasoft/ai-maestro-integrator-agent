# Operation: Load Handoff Documents

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Define handoff directory](#step-1-define-handoff-directory)
  - [Step 2: Check directory exists](#step-2-check-directory-exists)
  - [Step 3: Load current handoff](#step-3-load-current-handoff)
  - [Step 4: Load patterns learned](#step-4-load-patterns-learned)
  - [Step 5: Load session state JSON (if exists)](#step-5-load-session-state-json-if-exists)
  - [Step 6: Parse current handoff](#step-6-parse-current-handoff)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Handoff Directory Structure](#handoff-directory-structure)
- [Current Handoff Format](#current-handoff-format)
- [Task](#task)
- [Progress](#progress)
- [Blockers](#blockers)
- [Next Steps](#next-steps)
- [Context Links](#context-links)
- [Error Handling](#error-handling)
  - [Directory not found](#directory-not-found)
  - [File permission denied](#file-permission-denied)
  - [Corrupted JSON](#corrupted-json)
  - [Empty files](#empty-files)
- [Complete Loading Script](#complete-loading-script)
- [Verification](#verification)

## Purpose

Load handoff documents from the standard AMIA integration directory to restore session context and continue work from a previous session.

## When to Use

- At session start when handoff documents may exist
- When resuming integration work after context compaction
- When picking up work handed off by another agent

## Prerequisites

1. `$CLAUDE_PROJECT_DIR` environment variable set
2. Read access to handoff directory

## Procedure

### Step 1: Define handoff directory

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
```

### Step 2: Check directory exists

```bash
if [ ! -d "$HANDOFF_DIR" ]; then
  echo "No handoff directory found"
  exit 0  # Not an error - may be first session
fi
```

### Step 3: Load current handoff

```bash
CURRENT_HANDOFF="$HANDOFF_DIR/current.md"

if [ -f "$CURRENT_HANDOFF" ]; then
  echo "Found current handoff document"
  CURRENT_CONTENT=$(cat "$CURRENT_HANDOFF")
else
  echo "No current handoff document"
  CURRENT_CONTENT=""
fi
```

### Step 4: Load patterns learned

```bash
PATTERNS_FILE="$HANDOFF_DIR/patterns-learned.md"

if [ -f "$PATTERNS_FILE" ]; then
  echo "Found patterns-learned document"
  PATTERNS_CONTENT=$(cat "$PATTERNS_FILE")
else
  PATTERNS_CONTENT=""
fi
```

### Step 5: Load session state JSON (if exists)

```bash
STATE_FILE="$HANDOFF_DIR/session_state.json"

if [ -f "$STATE_FILE" ]; then
  echo "Found session state JSON"
  SESSION_STATE=$(cat "$STATE_FILE" | jq '.')
else
  SESSION_STATE="{}"
fi
```

### Step 6: Parse current handoff

```bash
# Extract sections from current handoff markdown
if [ -n "$CURRENT_CONTENT" ]; then
  # Extract task description
  TASK=$(echo "$CURRENT_CONTENT" | sed -n '/^## Task/,/^##/p' | head -n -1)

  # Extract progress
  PROGRESS=$(echo "$CURRENT_CONTENT" | sed -n '/^## Progress/,/^##/p' | head -n -1)

  # Extract blockers
  BLOCKERS=$(echo "$CURRENT_CONTENT" | sed -n '/^## Blockers/,/^##/p' | head -n -1)

  # Extract next steps
  NEXT_STEPS=$(echo "$CURRENT_CONTENT" | sed -n '/^## Next Steps/,/^##/p' | head -n -1)
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| handoff_dir | string | no | Custom handoff directory (uses default if not specified) |
| include_patterns | boolean | no | Whether to load patterns-learned.md |

## Output

| Field | Type | Description |
|-------|------|-------------|
| found | boolean | Whether any handoff docs were found |
| current_handoff | object | Parsed current handoff document |
| patterns_learned | string | Content of patterns-learned.md |
| session_state | object | Parsed session_state.json |
| files_found | string[] | List of handoff files found |

## Example Output

```json
{
  "found": true,
  "current_handoff": {
    "task": "Review PR #123 for security issues",
    "progress": "Reviewed auth module, found 2 issues",
    "blockers": "None",
    "next_steps": "Review middleware next"
  },
  "patterns_learned": "## Error Handling\n- Found inconsistent try/catch...",
  "session_state": {
    "session_id": "sess_abc123",
    "current_phase": "review"
  },
  "files_found": ["current.md", "patterns-learned.md", "session_state.json"]
}
```

## Handoff Directory Structure

```
$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/
  current.md           - Current task handoff
  patterns-learned.md  - Patterns observed across sessions
  session_state.json   - Structured session state
  release-history.md   - Release tracking (for release work)
  archive/             - Archived handoffs
```

## Current Handoff Format

```markdown
# AMIA Integration Handoff

**Created**: 2025-02-05T10:00:00Z
**Last Updated**: 2025-02-05T14:30:00Z
**Agent**: amia-main

## Task

Review PR #123 for security issues in authentication flow.

## Progress

- [x] Fetched PR details
- [x] Analyzed diff
- [x] Reviewed auth module
- [ ] Review middleware
- [ ] Post review comments

## Blockers

None currently.

## Next Steps

1. Review middleware changes
2. Check for SQL injection vulnerabilities
3. Post review comments

## Context Links

- PR: https://github.com/owner/repo/pull/123
- Issue: https://github.com/owner/repo/issues/456
```

## Error Handling

### Directory not found

**Cause**: Handoff directory doesn't exist.

**Solution**: This is normal for first session. Proceed without loaded state.

### File permission denied

**Cause**: Cannot read handoff files.

**Solution**: Check file permissions, verify CLAUDE_PROJECT_DIR is correct.

### Corrupted JSON

**Cause**: session_state.json is invalid.

**Solution**: Ignore JSON state, use markdown handoff instead.

### Empty files

**Cause**: Handoff files exist but are empty.

**Solution**: Treat as no handoff found.

## Complete Loading Script

```bash
#!/bin/bash
# load_handoff_docs.sh

HANDOFF_DIR="${1:-$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration}"

echo "=== Loading AMIA Handoff Documents ==="

# Initialize result
RESULT='{"found": false, "files_found": []}'

if [ ! -d "$HANDOFF_DIR" ]; then
  echo "$RESULT"
  exit 0
fi

FILES_FOUND=()

# Load current.md
if [ -f "$HANDOFF_DIR/current.md" ]; then
  FILES_FOUND+=("current.md")
  CURRENT=$(cat "$HANDOFF_DIR/current.md")
fi

# Load patterns-learned.md
if [ -f "$HANDOFF_DIR/patterns-learned.md" ]; then
  FILES_FOUND+=("patterns-learned.md")
  PATTERNS=$(cat "$HANDOFF_DIR/patterns-learned.md")
fi

# Load session_state.json
if [ -f "$HANDOFF_DIR/session_state.json" ]; then
  FILES_FOUND+=("session_state.json")
  STATE=$(cat "$HANDOFF_DIR/session_state.json" | jq '.' 2>/dev/null || echo '{}')
fi

# Build result
if [ ${#FILES_FOUND[@]} -gt 0 ]; then
  echo "Found ${#FILES_FOUND[@]} handoff file(s)"
  jq -n \
    --argjson found true \
    --argjson files "$(printf '%s\n' "${FILES_FOUND[@]}" | jq -R . | jq -s .)" \
    '{found: $found, files_found: $files}'
else
  echo '{"found": false, "files_found": []}'
fi
```

## Verification

After loading:

```bash
# Check if handoff was found
if [ "$FOUND" = "true" ]; then
  echo "Loaded handoff documents"
  echo "Files: ${FILES_FOUND[*]}"

  # Display task summary
  if [ -n "$CURRENT" ]; then
    echo "Current task:"
    echo "$CURRENT" | head -20
  fi
else
  echo "No handoff documents found - starting fresh"
fi
```
