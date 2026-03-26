# Operation: Add Issue to Project Board

## Table of Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [GraphQL Mutation](#graphql-mutation)
- [Getting Issue Node ID](#getting-issue-node-id)
- [Output](#output)
- [Setting Initial Status](#setting-initial-status)
- [Error Handling](#error-handling)
- [Verification](#verification)
- [Bulk Add Issues](#bulk-add-issues)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-add-issue-to-board |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Kanban Orchestration |
| **Agent** | api-coordinator |

## Purpose

Add a GitHub Issue to a Projects V2 board, placing it in the Backlog column by default.

## Preconditions

- Issue exists in the repository
- Project board exists
- User has permission to add items to the project

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `repo` | string | Yes | Repository name |
| `project_number` | int | Yes | GitHub Project number |
| `issue_number` | int | Yes | Issue to add |
| `initial_status` | string | No | Initial column (default: Backlog) |

## Procedure

1. Get the project ID from project number
2. Get the issue node ID
3. Add the issue to the project
4. Optionally set initial status column
5. Verify the issue appears on the board

## Command

```bash
# Using gh CLI
gh project item-add PROJECT_NUMBER --owner OWNER --url "https://github.com/OWNER/REPO/issues/ISSUE_NUMBER"

# Example
gh project item-add 1 --owner Emasoft --url "https://github.com/Emasoft/myrepo/issues/42"
```

## GraphQL Mutation

```graphql
mutation {
  addProjectV2ItemById(
    input: {
      projectId: "PVT_kwDO..."
      contentId: "I_kwDO..."  # Issue node ID
    }
  ) {
    item {
      id
    }
  }
}
```

## Getting Issue Node ID

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      issue(number: 42) {
        id
      }
    }
  }
'
```

## Output

```json
{
  "added": true,
  "issue_number": 42,
  "project_item_id": "PVTI_...",
  "initial_status": "Backlog"
}
```

## Setting Initial Status

After adding, move to desired column:

```bash
# Move to Todo if ready to start
python3 scripts/amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER Todo
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Issue not found | Invalid issue number | Verify issue exists |
| Project not found | Invalid project number | Use `gh project list` to find correct number |
| Already on board | Issue already added | No action needed |
| Permission denied | Insufficient access | Check project permissions |

## Verification

After adding, verify the issue appears:

```bash
gh project item-list PROJECT_NUMBER --owner OWNER --format json | \
  jq '.items[] | select(.content.number == 42)'
```

## Bulk Add Issues

For multiple issues:

```bash
for ISSUE in 42 43 44 45; do
  gh project item-add 1 --owner Emasoft --url "https://github.com/Emasoft/myrepo/issues/$ISSUE"
done
```

## Related Operations

- [op-create-module-issue.md](op-create-module-issue.md) - Create issue first
- [op-move-card.md](op-move-card.md) - Move to desired column
- [op-get-board-state.md](op-get-board-state.md) - Verify board state
