# Proactive Kanban Monitoring

## Contents

- [M.1 Overview of proactive monitoring](#m1-overview)
- [M.2 Polling configuration and frequency](#m2-polling-configuration)
- [M.3 What to check on each poll (detection table)](#m3-what-to-check-on-each-poll)
- [M.4 Running the polling script](#m4-polling-script)
- [M.5 Change detection logic (pseudocode)](#m5-change-detection-logic)
- [M.6 AI Maestro notifications for detected changes](#m6-ai-maestro-notifications)
- [M.7 Proactive monitoring checklist](#m7-proactive-monitoring-checklist)

---

## M.1 Overview

The orchestrator must PROACTIVELY monitor the GitHub Project Kanban board for changes, rather than waiting for events. This ensures timely response to card movements, status changes, and assignment updates.

## M.2 Polling Configuration

**Poll Frequency**: Every 5 minutes during active orchestration sessions.

**Polling Command**:
```bash
# Get all items from the project board
gh project item-list --owner Emasoft --format json
```

## M.3 What to Check on Each Poll

| Check | Command | Action When Detected |
|-------|---------|---------------------|
| Card movements | Compare `status` field with previous poll | Notify relevant agent of status change |
| New assignees | Compare `assignees` field | Welcome new assignee, provide context |
| Due date changes | Compare `dueDate` field | Alert if due date approaches or passes |
| New items added | Check for new `id` values | Add to backlog, notify orchestrator |
| Items removed | Check for missing `id` values | Log removal, update internal state |

## M.4 Polling Script

```bash
# Poll and detect changes (run every 5 minutes)
python scripts/kanban_poll_changes.py --owner Emasoft --project PROJECT_NUMBER --interval 300
```

## M.5 Change Detection Logic

```python
# Pseudocode for change detection
previous_state = load_previous_state()
current_state = gh_project_item_list()

for item in current_state:
    if item.id not in previous_state:
        notify("New item added", item)
    elif item.status != previous_state[item.id].status:
        notify("Card moved", item, previous_state[item.id].status, item.status)
    elif item.assignees != previous_state[item.id].assignees:
        notify("Assignment changed", item)

save_state(current_state)
```

## M.6 AI Maestro Notifications

When changes are detected, notify relevant agents using the `agent-messaging` skill.

**Assignment notification:** Send a message using the `agent-messaging` skill with:
- **Recipient**: The assigned agent
- **Subject**: `Kanban Update: Issue #123 assigned to you`
- **Priority**: `normal`
- **Content**: `{"type": "kanban-assignment", "message": "Issue #123 has been assigned to you. Current status: Todo. Please move to In Progress when starting."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Status change notification:** Send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-eoa`
- **Subject**: `Kanban Update: Issue #123 moved to AI Review`
- **Priority**: `normal`
- **Content**: `{"type": "kanban-status-change", "message": "Issue #123 moved from In Progress to AI Review by agent-name. PR likely created."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## M.7 Proactive Monitoring Checklist

- [ ] Set up polling script to run every 5 minutes
- [ ] Configure state persistence for change detection
- [ ] Set up AI Maestro notifications for detected changes
- [ ] Monitor for stale items (no movement in 24+ hours)
- [ ] Alert on blocked items without resolution progress
- [ ] Track due date proximity (warn at 24h, 48h, 1 week)
