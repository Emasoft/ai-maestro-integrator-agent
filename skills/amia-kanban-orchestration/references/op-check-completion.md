# Operation: Check Board Completion


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Output](#output)
- [Completion Criteria](#completion-criteria)
- [Exit Codes](#exit-codes)
- [Stop Hook Integration](#stop-hook-integration)
- [Handling Incomplete Work at Exit](#handling-incomplete-work-at-exit)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-check-completion |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Kanban Orchestration |
| **Agent** | api-coordinator |

## Purpose

Check if all items on the project board are complete (in Done column), used by stop hooks to prevent premature exit.

## Preconditions

- Project board exists and is accessible
- Items are tracked on the board

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `repo` | string | Yes | Repository name |
| `project_number` | int | Yes | GitHub Project number |

## Procedure

1. Query all items on the board
2. Count items by status column
3. Determine completion state
4. Return appropriate exit code

## Command

```bash
python3 scripts/amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER
```

## Output

```json
{
  "complete": false,
  "summary": {
    "Backlog": 2,
    "Todo": 3,
    "In Progress": 1,
    "AI Review": 1,
    "Human Review": 1,
    "Merge/Release": 0,
    "Done": 10,
    "Blocked": 1,
    "Other": 0
  },
  "blocking_items": [
    {"issue_number": 42, "status": "In Progress", "assignee": "dev1"},
    {"issue_number": 60, "status": "Blocked", "reason": "Missing credentials"}
  ],
  "recommendation": "Complete or defer 6 pending items before exit"
}
```

## Completion Criteria

| Condition | Complete? | Exit Code |
|-----------|-----------|-----------|
| All items in Done | Yes | 0 |
| Items in Todo/In Progress/AI Review/Human Review/Merge Release | No | 1 |
| Items in Blocked | No | 2 |

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All items Done | Safe to exit |
| 1 | Items still in progress | Cannot exit - complete work first |
| 2 | Blocked items exist | Cannot exit - resolve blockers or escalate |

## Stop Hook Integration

This operation is called by the orchestrator stop hook to prevent premature exit:

```python
# In stop hook
result = check_completion(owner, repo, project_number)
if result["complete"]:
    return {"decision": "allow", "reason": "All work complete"}
else:
    return {
        "decision": "block",
        "reason": f"Incomplete items: {result['summary']}",
        "systemMessage": result["recommendation"]
    }
```

## Handling Incomplete Work at Exit

If completion check fails:

1. **Items in progress** - Wait for completion or reassign
2. **Items blocked** - Resolve blockers or escalate to user
3. **Items in AI review or human review** - Complete reviews or merge PRs
4. **Items in merge/release** - Merge PRs promptly
5. **Items deferred** - Explicitly mark as deferred with reason

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Project not found | Invalid project number | Verify project exists |
| Empty board | No items on board | Consider as complete (no work) |

## Related Operations

- [op-get-board-state.md](op-get-board-state.md) - Get full board state
- [op-move-card.md](op-move-card.md) - Move items to Done
