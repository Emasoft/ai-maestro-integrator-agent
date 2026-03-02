# Stop Hook Integration

## Table of Contents

- 8.1 [The stop hook's role in orchestration](#81-stop-hook-role)
- 8.2 [Board state queries performed by stop hook](#82-board-queries)
- 8.3 [Completion criteria: when can orchestrator exit](#83-completion-criteria)
- 8.4 [Handling incomplete work at exit time](#84-incomplete-work)
- 8.5 [Blocked items and exit policy](#85-blocked-items)
- 8.6 [Stop hook configuration options](#86-configuration)
- 8.7 [Manual override of stop hook](#87-manual-override)
- 8.8 [Stop hook error handling](#88-error-handling)

---

## 8.1 Stop Hook Role

The stop hook is a critical safety mechanism that prevents the orchestrator from exiting with incomplete work.

### Purpose

```
Stop hook ensures:
1. All assigned work is complete
2. No items are left in progress
3. Blocked items are acknowledged
4. Board state is consistent
```

### When Stop Hook Fires

The stop hook runs when:
- Orchestrator attempts to exit session
- User requests session end
- Conversation reaches natural conclusion
- Agent calls stop/exit command

### Stop Hook Flow

```
Orchestrator attempts to exit
         │
         ▼
   ┌─────────────┐
   │ Stop Hook   │
   │ Triggered   │
   └─────┬───────┘
         │
         ▼
   ┌─────────────┐
   │ Query Board │
   │ State       │
   └─────┬───────┘
         │
         ▼
   ┌─────────────┐     NO      ┌─────────────┐
   │ All Work    ├────────────►│ Block Exit  │
   │ Complete?   │             │ Show Status │
   └─────┬───────┘             └─────────────┘
         │
         │ YES
         ▼
   ┌─────────────┐
   │ Allow Exit  │
   │ Session End │
   └─────────────┘
```

---

## 8.2 Board Queries

The stop hook performs these queries against the Kanban board.

### Query 1: Get All Non-Done Items

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            fieldValues(first: 5) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                state
                assignees(first: 3) { nodes { login } }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | select(.fieldValues.nodes[] | select(.field.name == "Status" and .name != "Done" and .name != "Backlog"))
'
```

### Query 2: Count by Status

```bash
gh api graphql -f query='...' | jq '
  [.data.node.items.nodes[].fieldValues.nodes[] | select(.field.name == "Status") | .name]
  | group_by(.)
  | map({status: .[0], count: length})
'
```

### Query 3: Items Assigned to This Session

```bash
SESSION_AGENT="orchestrator-master"

# Get items where orchestrator is involved
gh api graphql -f query='...' | jq --arg agent "$SESSION_AGENT" '
  .data.node.items.nodes[]
  | select(.content.assignees.nodes[] | .login == $agent)
'
```

---

## 8.3 Completion Criteria

The orchestrator can exit when these criteria are met.

### Criteria Matrix

| Status | Count | Can Exit? |
|--------|-------|-----------|
| Backlog | Any | Yes (not started) |
| Todo | 0 | Yes |
| Todo | >0 | Only if unassigned or deferred |
| In Progress | 0 | Yes |
| In Progress | >0 | No |
| AI Review | 0 | Yes |
| AI Review | >0 | No (unless handoff) |
| Done | Any | Yes |
| Blocked | 0 | Yes |
| Blocked | >0 | Only if acknowledged |

### Simple Rule

```
CAN_EXIT = (In Progress == 0) AND (AI Review == 0 OR handoff) AND (Blocked == 0 OR acknowledged)
```

### Exit Decision Logic

```python
def can_exit(board_state):
    in_progress = count_status(board_state, "In Progress")
    in_review = count_status(board_state, "AI Review")
    blocked = count_status(board_state, "Blocked")

    if in_progress > 0:
        return False, f"{in_progress} items still in progress"

    if in_review > 0:
        # Check if handoff is documented
        if not all_reviews_handed_off(board_state):
            return False, f"{in_review} items in review without handoff"

    if blocked > 0:
        # Check if blockers are acknowledged
        if not all_blockers_acknowledged(board_state):
            return False, f"{blocked} blocked items need acknowledgment"

    return True, "All work complete"
```

---

## 8.4 Incomplete Work

When work is incomplete at exit time, the stop hook provides options.

### Option 1: Complete Work First

```
Stop hook message:
"Cannot exit. 2 items still In Progress:
- #42: Auth module (assigned to @agent-1)
- #45: API client (assigned to @agent-2)

Please complete these items or defer them before exiting."
```

### Option 2: Defer Items

Move items back to Todo with deferral comment:

```bash
# Defer item to next session
gh issue comment 42 --body "$(cat <<'EOF'
## Deferred

**Deferred by:** @orchestrator-master
**Reason:** Session ending, work not complete
**State at deferral:** Implementation 60% complete
**Next steps:** Complete validation logic, write tests
**Branch:** feature/issue-42-auth-core

Moving back to Todo for next session.
EOF
)"

# Move to Todo
# [GraphQL mutation to update status]

# Remove in-progress label if any
gh issue edit 42 --remove-label "in-progress"
```

### Option 3: Force Exit (Not Recommended)

If absolutely necessary, force exit with override (see 8.7).

### Deferral Tracking

When deferring, ensure next session can pick up:
1. Document current state in comment
2. List remaining work
3. Note any context that would be lost
4. Branch name for code in progress

---

## 8.5 Blocked Items

Blocked items require special handling at exit time.

### Blocked Item Policy

```
IF blocked items exist:
  1. List all blocked items
  2. Show blocker reason for each
  3. Require acknowledgment
  4. Document that blockers are known
  5. Allow exit if acknowledged
```

### Acknowledgment Process

```bash
# Stop hook shows:
"The following items are blocked:
- #42: Auth module - Missing database credentials
- #48: Payment flow - Stripe API down

Do you acknowledge these blockers will remain unresolved? (yes/no)"

# If yes, add acknowledgment comment
gh issue comment 42 --body "$(cat <<'EOF'
## Blocker Acknowledged

Session ending with this item blocked.
Blocker: Missing database credentials
Acknowledged by: @orchestrator-master
Time: 2024-01-15 17:00 UTC

This blocker will be addressed in next session or escalated.
EOF
)"
```

### Exit with Blocked Items

After acknowledgment:
1. Blocked items stay in Blocked status
2. Escalation timeline continues
3. Next session inherits blocked items
4. Human may be notified if duration threshold exceeded

---

## 8.6 Configuration

The stop hook can be configured for different behaviors.

### Configuration Options

```json
{
  "stop_hook": {
    "enabled": true,
    "strict_mode": true,
    "allow_in_review_exit": false,
    "require_blocker_ack": true,
    "auto_defer_threshold_minutes": 30,
    "notify_on_incomplete": true
  }
}
```

### Option Descriptions

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | true | Enable stop hook checks |
| `strict_mode` | true | No exit with any incomplete work |
| `allow_in_review_exit` | false | Allow exit with items in review |
| `require_blocker_ack` | true | Require blocker acknowledgment |
| `auto_defer_threshold_minutes` | 30 | Auto-defer if stuck this long |
| `notify_on_incomplete` | true | Send notification on blocked exit |

### Per-Project Override

```bash
# Set project-specific config
gh api repos/OWNER/REPO/contents/design/config/stop-hook-config.json \
  --method PUT \
  --field message="Update stop hook config" \
  --field content="$(base64 config.json)"
```

---

## 8.7 Manual Override

In exceptional cases, the stop hook can be overridden.

### Override Command

```bash
# Force exit (requires explicit confirmation)
/stop --force --reason "Emergency: critical production issue requires attention"
```

### Override Requirements

1. **Explicit `--force` flag**
2. **Mandatory `--reason`**
3. **Logged to audit trail**
4. **Creates override comment on all incomplete items**

### Override Comment

```markdown
## Forced Exit Override

**Exit forced by:** @orchestrator-master
**Reason:** Emergency: critical production issue requires attention
**Items affected:** #42, #45, #48
**Time:** 2024-01-15 17:00 UTC

Work was left incomplete due to forced exit. Next session should:
1. Review state of these items
2. Resume or defer as appropriate
3. Address any blockers
```

### When Override Is Acceptable

| Scenario | Override Acceptable? |
|----------|---------------------|
| Emergency production issue | Yes |
| Context window exhausted | Yes (after deferral attempt) |
| User explicitly requests | Yes |
| Just wants to stop | No (must complete or defer) |
| Tired of working | No |

---

## 8.8 Error Handling

The stop hook can encounter errors. Here's how to handle them.

### Error: Cannot Query Board

```
Stop hook error: Failed to query project board
Error: GraphQL query failed: 401 Unauthorized

Actions:
1. Check gh auth status
2. Verify project ID is correct
3. Retry query
4. If persistent, allow exit with warning
```

### Error: Project Not Found

```
Stop hook error: Project not found
Project ID: PVT_kwDO... not found

Actions:
1. Verify project exists
2. Check project permissions
3. Update project ID in config
4. Allow exit with warning if project deleted
```

### Error: Rate Limited

```
Stop hook error: Rate limited
Retry after: 60 seconds

Actions:
1. Wait for rate limit reset
2. Retry query
3. If urgent, allow exit with warning
```

### Fallback Behavior

If stop hook cannot complete its checks:

```python
def stop_hook_fallback():
    """Fallback when stop hook fails"""

    # Log the failure
    log_error("Stop hook failed, using fallback")

    # Warn user
    print("WARNING: Could not verify board state.")
    print("Manual verification recommended before exit.")

    # Ask for confirmation
    response = input("Exit anyway? (yes/no): ")

    if response.lower() == "yes":
        # Log override
        log_audit("Exit with stop hook failure", {
            "reason": "Stop hook error",
            "user_confirmed": True
        })
        return True
    else:
        return False
```

### Audit Trail

All stop hook events are logged:

```json
{
  "event": "stop_hook",
  "timestamp": "2024-01-15T17:00:00Z",
  "result": "blocked",
  "reason": "2 items in progress",
  "items": [42, 45],
  "action_taken": "exit_blocked"
}
```
