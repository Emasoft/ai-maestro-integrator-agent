---
name: op-deserialize-session-state
description: "Parse and load session state from JSON storage"
procedure: support-skill
workflow-instruction: support
---

# Operation: Deserialize Session State


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Locate state file](#step-1-locate-state-file)
  - [Step 2: Read state file](#step-2-read-state-file)
  - [Step 3: Parse JSON](#step-3-parse-json)
  - [Step 4: Extract fields](#step-4-extract-fields)
  - [Step 5: Validate loaded state](#step-5-validate-loaded-state)
  - [Step 6: Log loaded state](#step-6-log-loaded-state)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Storage Locations](#storage-locations)
  - [Primary Location](#primary-location)
  - [Alternative Locations](#alternative-locations)
- [Deserialization Patterns](#deserialization-patterns)
  - [From File](#from-file)
  - [From PR Comment](#from-pr-comment)
  - [From Environment Variable](#from-environment-variable)
- [Complete Deserialization Script](#complete-deserialization-script)
- [Error Handling](#error-handling)
  - [File not found](#file-not-found)
  - [Invalid JSON](#invalid-json)
  - [Empty file](#empty-file)
  - [Corrupted data](#corrupted-data)
- [Verification](#verification)

## Purpose

Load and parse session state from JSON storage into usable form for resuming work.

## When to Use

- At session start to check for existing state
- When resuming work from a previous session
- When loading state passed from another agent
- When recovering from session interruption

## Prerequisites

1. Valid JSON state stored in known location
2. Read access to state storage location

## Procedure

### Step 1: Locate state file

```bash
# Standard state location
STATE_PATH="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/session_state.json"

# Check if exists
if [ -f "$STATE_PATH" ]; then
  echo "State file found: $STATE_PATH"
else
  echo "No state file found"
  exit 0  # Not an error - may be new session
fi
```

### Step 2: Read state file

```bash
# Read raw content
STATE_RAW=$(cat "$STATE_PATH")

# Verify non-empty
if [ -z "$STATE_RAW" ]; then
  echo "State file is empty"
  exit 0
fi
```

### Step 3: Parse JSON

```bash
# Parse and validate JSON
STATE=$(echo "$STATE_RAW" | jq '.')

if [ $? -ne 0 ]; then
  echo "Failed to parse state JSON"
  exit 1
fi
```

### Step 4: Extract fields

```bash
# Extract individual fields
SESSION_ID=$(echo "$STATE" | jq -r '.session_id')
STARTED_AT=$(echo "$STATE" | jq -r '.started_at')
CURRENT_PHASE=$(echo "$STATE" | jq -r '.current_phase')
LAST_UPDATED=$(echo "$STATE" | jq -r '.last_updated // .started_at')

# Extract arrays
COMPLETED_TASKS=$(echo "$STATE" | jq -r '.completed_tasks // []')
PENDING_TASKS=$(echo "$STATE" | jq -r '.pending_tasks // []')

# Extract nested data
ACCUMULATED_DATA=$(echo "$STATE" | jq '.accumulated_data // {}')
```

### Step 5: Validate loaded state

```bash
# Use op-validate-session-state
# Validation should pass before proceeding
```

### Step 6: Log loaded state

```bash
echo "=== Loaded Session State ==="
echo "Session ID: $SESSION_ID"
echo "Started: $STARTED_AT"
echo "Last Updated: $LAST_UPDATED"
echo "Current Phase: $CURRENT_PHASE"
echo "Completed Tasks: $(echo "$COMPLETED_TASKS" | jq -r 'length')"
echo "Pending Tasks: $(echo "$PENDING_TASKS" | jq -r 'length')"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| state_path | string | no | Path to state file (uses default if not specified) |
| state_json | string | no | Raw JSON string (alternative to file path) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| found | boolean | Whether state was found |
| session_id | string | Loaded session identifier |
| current_phase | string | Current workflow phase |
| completed_tasks | string[] | List of completed task names |
| pending_tasks | string[] | List of remaining task names |
| accumulated_data | object | Task-specific preserved data |
| age_seconds | number | Age of state since last update |

## Example Output

```json
{
  "found": true,
  "session_id": "sess_1707134400_a1b2c3d4",
  "current_phase": "review",
  "completed_tasks": ["fetch_pr", "analyze_diff"],
  "pending_tasks": ["post_review"],
  "accumulated_data": {
    "pr_number": 123,
    "review_comments": []
  },
  "age_seconds": 3600
}
```

## Storage Locations

### Primary Location

```
$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/session_state.json
```

### Alternative Locations

```bash
# PR-specific state (stored in PR comment)
gh pr view 123 --comments --json comments | jq -r '
  .comments[] | select(.body | contains("AMIA-SESSION-STATE")) | .body
' | grep -oP '(?<=AMIA-SESSION-STATE ).*(?= -->)' | jq '.'

# Issue-specific state
gh issue view 456 --comments --json comments | jq -r '
  .comments[] | select(.body | contains("AMIA-SESSION-STATE")) | .body
'
```

## Deserialization Patterns

### From File

```bash
STATE=$(cat "$STATE_PATH" | jq '.')
```

### From PR Comment

```bash
# Extract state from PR comment
PR_COMMENTS=$(gh pr view 123 --comments --json comments)
STATE=$(echo "$PR_COMMENTS" | jq -r '
  .comments[]
  | select(.body | contains("AMIA-SESSION-STATE"))
  | .body
  | capture("<!-- AMIA-SESSION-STATE (?<json>.*) -->")
  | .json
' | jq '.')
```

### From Environment Variable

```bash
# If state passed via env var
STATE=$(echo "$AMIA_SESSION_STATE" | base64 -d | jq '.')
```

## Complete Deserialization Script

```bash
#!/bin/bash
# deserialize_session_state.sh

STATE_PATH="${1:-$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/session_state.json}"

echo "=== Deserializing Session State ==="

# Check file exists
if [ ! -f "$STATE_PATH" ]; then
  echo '{"found": false}'
  exit 0
fi

# Read and parse
STATE_RAW=$(cat "$STATE_PATH")
if [ -z "$STATE_RAW" ]; then
  echo '{"found": false, "error": "empty_file"}'
  exit 0
fi

# Validate JSON
if ! STATE=$(echo "$STATE_RAW" | jq '.'); then
  echo '{"found": false, "error": "invalid_json"}'
  exit 1
fi

# Calculate age
LAST_TS=$(echo "$STATE" | jq -r '.last_updated // .started_at')
if [ -n "$LAST_TS" ]; then
  # macOS compatible
  LAST_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$LAST_TS" "+%s" 2>/dev/null || date -d "$LAST_TS" "+%s")
  NOW_EPOCH=$(date "+%s")
  AGE_SECONDS=$((NOW_EPOCH - LAST_EPOCH))
else
  AGE_SECONDS=0
fi

# Build output
echo "$STATE" | jq --argjson age "$AGE_SECONDS" '. + {found: true, age_seconds: $age}'
```

## Error Handling

### File not found

**Cause**: No state file exists at expected location.

**Solution**: This is normal for new sessions. Return `found: false`.

### Invalid JSON

**Cause**: State file contains invalid JSON.

**Solution**: Attempt recovery from backup or start fresh.

### Empty file

**Cause**: State file exists but is empty.

**Solution**: Treat as no state found.

### Corrupted data

**Cause**: State file has partial/corrupted data.

**Solution**: Validate structure, reject if invalid.

## Verification

After deserialization:

```bash
# Run deserialization
RESULT=$(./deserialize_session_state.sh)

# Check if state was found
if echo "$RESULT" | jq -e '.found == true' > /dev/null; then
  echo "State loaded successfully"

  # Get current phase to resume
  PHASE=$(echo "$RESULT" | jq -r '.current_phase')
  echo "Resuming from phase: $PHASE"
else
  echo "No previous state - starting fresh"
fi
```
