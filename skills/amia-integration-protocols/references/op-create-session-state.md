# Operation: Create Session State

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify state components](#step-1-identify-state-components)
  - [Step 2: Build the state object](#step-2-build-the-state-object)
  - [Step 3: Generate session ID (if new)](#step-3-generate-session-id-if-new)
  - [Step 4: Add timestamps](#step-4-add-timestamps)
  - [Step 5: Validate state structure](#step-5-validate-state-structure)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Session State Schema](#session-state-schema)
  - [Minimal State](#minimal-state)
  - [Full State](#full-state)
- [Phase Names](#phase-names)
- [Storage Locations](#storage-locations)
- [Error Handling](#error-handling)
  - [Missing current phase](#missing-current-phase)
  - [Invalid timestamp format](#invalid-timestamp-format)
  - [State too large](#state-too-large)
- [Verification](#verification)

## Purpose

Create a structured session state snapshot that captures the current work context for preservation across session boundaries or context compactions.

## When to Use

- Before ending a session with incomplete work
- Before context compaction when important state exists
- When handing off work to another session
- Periodically during long-running tasks

## Prerequisites

1. Understanding of current task progress
2. Knowledge of what state needs to be preserved
3. Access to write session state to storage

## Procedure

### Step 1: Identify state components

Determine what needs to be captured:

- Session metadata (ID, timestamps)
- Current phase/stage of work
- Completed tasks list
- Pending tasks list
- Any accumulated data

### Step 2: Build the state object

```json
{
  "session_id": "sess_abc123",
  "started_at": "2025-02-05T10:00:00Z",
  "last_updated": "2025-02-05T14:30:00Z",
  "current_phase": "implementation",
  "completed_tasks": [
    "fetch_pr_details",
    "analyze_diff",
    "identify_changes"
  ],
  "pending_tasks": [
    "post_review_comments",
    "update_pr_status"
  ],
  "accumulated_data": {
    "pr_number": 123,
    "files_changed": 5,
    "review_comments_draft": [
      {"file": "src/auth.py", "line": 42, "comment": "Check null case"}
    ]
  },
  "checkpoints": [
    {"phase": "fetch", "completed_at": "2025-02-05T10:15:00Z"},
    {"phase": "analyze", "completed_at": "2025-02-05T11:00:00Z"}
  ]
}
```

### Step 3: Generate session ID (if new)

```bash
# Generate unique session ID
SESSION_ID="sess_$(date +%s)_$(openssl rand -hex 4)"
echo "Session ID: $SESSION_ID"
```

### Step 4: Add timestamps

```bash
# Get current timestamp in ISO 8601
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

### Step 5: Validate state structure

Ensure required fields are present:

- `session_id`
- `started_at`
- `current_phase`

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | string | no | Existing session ID or generate new |
| current_phase | string | yes | Current workflow phase |
| completed_tasks | string[] | yes | List of completed task names |
| pending_tasks | string[] | yes | List of remaining task names |
| accumulated_data | object | no | Any task-specific data to preserve |

## Output

| Field | Type | Description |
|-------|------|-------------|
| session_state | object | Complete session state object |
| session_id | string | Session identifier |
| storage_path | string | Where state should be stored |

## Example Output

```json
{
  "session_state": {
    "session_id": "sess_1707134400_a1b2c3d4",
    "started_at": "2025-02-05T10:00:00Z",
    "last_updated": "2025-02-05T14:30:00Z",
    "current_phase": "review",
    "completed_tasks": ["fetch_pr", "analyze_diff"],
    "pending_tasks": ["post_review"],
    "accumulated_data": {}
  },
  "session_id": "sess_1707134400_a1b2c3d4",
  "storage_path": "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/session_state.json"
}
```

## Session State Schema

### Minimal State

```json
{
  "session_id": "sess_xxx",
  "started_at": "2025-02-05T10:00:00Z",
  "current_phase": "phase_name"
}
```

### Full State

```json
{
  "session_id": "sess_xxx",
  "started_at": "2025-02-05T10:00:00Z",
  "last_updated": "2025-02-05T14:30:00Z",
  "current_phase": "phase_name",
  "completed_tasks": [],
  "pending_tasks": [],
  "accumulated_data": {},
  "checkpoints": [],
  "metadata": {
    "agent_id": "amia-main",
    "task_type": "pr_review",
    "priority": "normal"
  }
}
```

## Phase Names

Use consistent phase names:

- `initialization` - Setting up work
- `fetch` - Retrieving data
- `analyze` - Processing/analysis
- `implementation` - Making changes
- `review` - Reviewing work
- `finalization` - Completing work
- `cleanup` - Post-completion cleanup

## Storage Locations

```bash
# Session state storage path
STATE_PATH="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/session_state.json"

# Write state
echo "$SESSION_STATE" | jq '.' > "$STATE_PATH"

# Verify write
cat "$STATE_PATH" | jq '.session_id'
```

## Error Handling

### Missing current phase

**Cause**: current_phase not specified.

**Solution**: Always specify the current phase, even if "unknown".

### Invalid timestamp format

**Cause**: Timestamp not in ISO 8601.

**Solution**: Use format `YYYY-MM-DDTHH:MM:SSZ`.

### State too large

**Cause**: accumulated_data contains too much data.

**Solution**: Store large data externally and reference by path/ID.

## Verification

After creating state:

```bash
# Verify state is valid JSON
cat "$STATE_PATH" | jq '.' > /dev/null && echo "Valid JSON"

# Verify required fields
cat "$STATE_PATH" | jq 'has("session_id") and has("started_at") and has("current_phase")'

# Verify timestamps are valid
cat "$STATE_PATH" | jq '.started_at | fromdateiso8601'
```
