# Operation: Poll Kanban Board for Changes


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Polling Configuration](#polling-configuration)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Change Detection Logic](#change-detection-logic)
- [What to Check on Each Poll](#what-to-check-on-each-poll)
- [AI Maestro Notifications](#ai-maestro-notifications)
  - [Assignment Notification](#assignment-notification)
  - [Status Change Notification](#status-change-notification)
- [Output](#output)
- [Stale Item Detection](#stale-item-detection)
- [Error Handling](#error-handling)
- [Checklist for Proactive Monitoring](#checklist-for-proactive-monitoring)
- [Related Operations](#related-operations)

> **Note**: The `kanban_poll_changes.py` script referenced in this document is not yet implemented. Use `amia_kanban_get_board_state.py` with periodic polling as a workaround.

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-poll-kanban-changes |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Kanban Orchestration |
| **Agent** | api-coordinator |

## Purpose

Proactively poll the GitHub Project Kanban board to detect changes (card movements, assignments, new items) and notify relevant agents.

## Preconditions

- Previous board state is available for comparison
- AI Maestro is available for notifications
- Polling interval is configured

## Polling Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Poll Frequency | Every 5 minutes | During active orchestration |
| State Persistence | JSON file | Store previous state for comparison |

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `project_number` | int | Yes | GitHub Project number |
| `interval` | int | No | Poll interval in seconds (default: 300) |
| `state_file` | string | No | Path to state persistence file |

## Procedure

1. Load previous board state from file
2. Query current board state from GitHub
3. Compare each item for changes
4. Detect new items, removed items, status changes, assignment changes
5. Send AI Maestro notifications for detected changes
6. Save current state for next poll

## Command

```bash
python scripts/kanban_poll_changes.py --owner Emasoft --project PROJECT_NUMBER --interval 300
```

## Change Detection Logic

```python
previous_state = load_previous_state()
current_state = gh_project_item_list()

for item in current_state:
    if item.id not in previous_state:
        notify("New item added", item)
    elif item.status != previous_state[item.id].status:
        notify("Card moved", item, previous_state[item.id].status, item.status)
    elif item.assignees != previous_state[item.id].assignees:
        notify("Assignment changed", item)

for item_id in previous_state:
    if item_id not in current_state:
        notify("Item removed", previous_state[item_id])

save_state(current_state)
```

## What to Check on Each Poll

| Check | Compare Field | Action When Detected |
|-------|---------------|---------------------|
| Card movements | `status` | Notify relevant agent of status change |
| New assignees | `assignees` | Welcome new assignee, provide context |
| Due date changes | `dueDate` | Alert if due date approaches or passes |
| New items added | `id` presence | Add to tracking, notify orchestrator |
| Items removed | `id` absence | Log removal, update internal state |

## AI Maestro Notifications

### Assignment Notification

Send a message using the `agent-messaging` skill with:
- **Recipient**: The assigned agent
- **Subject**: `Kanban Update: Issue #123 assigned to you`
- **Priority**: `normal`
- **Content**: `{"type": "kanban-assignment", "message": "Issue #123 has been assigned to you. Current status: Todo. Please move to In Progress when starting."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Status Change Notification

Send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `Kanban Update: Issue #123 moved to AI Review`
- **Priority**: `normal`
- **Content**: `{"type": "kanban-status-change", "message": "Issue #123 moved from In Progress to AI Review by agent-name. PR likely created."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## Output

```json
{
  "poll_timestamp": "2024-01-15T10:00:00Z",
  "changes_detected": 3,
  "changes": [
    {"type": "status_change", "issue": 42, "from": "Todo", "to": "In Progress"},
    {"type": "new_item", "issue": 50},
    {"type": "assignment_change", "issue": 30, "new_assignee": "dev2"}
  ],
  "notifications_sent": 3
}
```

## Stale Item Detection

Flag items with no movement in 24+ hours:

```python
for item in current_state:
    if item.last_updated < (now - 24_hours):
        if item.status in ["In Progress", "AI Review", "Human Review", "Merge & Release"]:
            notify_orchestrator("Stale item", item)
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| State file not found | First run | Initialize empty state |
| API rate limit | Too many polls | Increase interval |
| AI Maestro unavailable | Service down | Queue notifications for retry |

## Checklist for Proactive Monitoring

- [ ] Set up polling script to run every 5 minutes
- [ ] Configure state persistence for change detection
- [ ] Set up AI Maestro notifications for detected changes
- [ ] Monitor for stale items (no movement in 24+ hours)
- [ ] Alert on blocked items without resolution progress
- [ ] Track due date proximity (warn at 24h, 48h, 1 week)

## Related Operations

- [op-get-board-state.md](op-get-board-state.md) - Get current state
- [op-move-card.md](op-move-card.md) - Triggered by detected changes
