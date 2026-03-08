# Operation: Move Card Between Columns

## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Valid Transition Matrix](#valid-transition-matrix)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [GraphQL Mutation](#graphql-mutation)
- [Output](#output)
- [Error Output](#error-output)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-move-card |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Kanban Orchestration |
| **Agent** | api-coordinator |

## Purpose

Move a project item (card) from its current column to a new status column, with transition validation.

## Preconditions

- Item exists on the project board
- Transition is valid (see transition matrix)
- User has permission to move cards

## Valid Transition Matrix

| From | To | Who Can Move | Precondition |
|------|----|--------------|--------------|
| Backlog | Todo | Orchestrator | Work prioritized |
| Todo | In Progress | Assigned agent | Agent starts work |
| In Progress | AI Review | Assigned agent | PR created |
| AI Review | Human Review | Integrator | Big task needing user review |
| AI Review | Merge/Release | Integrator | Small task approved |
| Human Review | Merge/Release | Orchestrator | Human approves |
| Merge/Release | Done | Auto (PR merge) | PR merged |
| Any | Blocked | Any (with reason) | Blocker identified |
| Blocked | Previous | Any | Blocker resolved |

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `repo` | string | Yes | Repository name |
| `project_number` | int | Yes | GitHub Project number |
| `issue_number` | int | Yes | Issue number to move |
| `new_status` | string | Yes | Target status column |
| `reason` | string | Conditional | Required when moving to Blocked |

## Procedure

1. Get current status of the item
2. Validate transition is allowed
3. Get project and field IDs
4. Update the status field value via GraphQL
5. Return success/failure with details

## Command

```bash
python3 scripts/amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS [--reason "Reason"]

# Examples:
python3 scripts/amia_kanban_move_card.py owner repo 1 42 "In Progress"
python3 scripts/amia_kanban_move_card.py owner repo 1 42 Blocked --reason "Missing credentials"
```

## GraphQL Mutation

```graphql
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "PVT_kwDO..."
      itemId: "PVTI_..."
      fieldId: "PVTSSF_..."
      value: { singleSelectOptionId: "..." }
    }
  ) {
    projectV2Item {
      id
    }
  }
}
```

## Output

```json
{
  "success": true,
  "issue_number": 42,
  "previous_status": "Todo",
  "new_status": "In Progress",
  "moved_by": "orchestrator"
}
```

## Error Output

```json
{
  "success": false,
  "issue_number": 42,
  "error": "INVALID_TRANSITION",
  "message": "Cannot move directly from Backlog to Done",
  "current_status": "Backlog",
  "requested_status": "Done"
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid transition | Skipped intermediate status | Follow transition matrix |
| Item not found | Issue not on board | Add issue to project first |
| Permission denied | Insufficient access | Check GitHub permissions |
| Missing reason | Moving to Blocked without reason | Provide --reason flag |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid transition |
| 2 | Item not found |
| 3 | API error |

## Related Operations

- [op-get-board-state.md](op-get-board-state.md) - Check current state
- [op-add-issue-to-board.md](op-add-issue-to-board.md) - Add issue if not on board
