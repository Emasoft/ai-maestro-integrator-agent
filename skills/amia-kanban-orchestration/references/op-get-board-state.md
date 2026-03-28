# Operation: Get Board State

## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [GraphQL Query](#graphql-query)
- [Output](#output)
- [Column Definitions](#column-definitions)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-get-board-state |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Kanban Orchestration |
| **Agent** | api-coordinator |

## Purpose

Get the complete state of a GitHub Projects V2 board, including all items grouped by their status column.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- GitHub Projects V2 is enabled for the repository
- GraphQL API access is available

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `repo` | string | Yes | Repository name |
| `project_number` | int | Yes | GitHub Project number |

## Procedure

1. Query the project using GraphQL API
2. Get all items with their status field values
3. Group items by status column
4. Return structured JSON response

## Command

```bash
python3 scripts/amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER
```

## GraphQL Query

```graphql
query {
  repository(owner: "OWNER", name: "REPO") {
    projectV2(number: PROJECT_NUMBER) {
      items(first: 100) {
        nodes {
          id
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
            }
          }
          content {
            ... on Issue {
              number
              title
              state
              assignees(first: 5) {
                nodes { login }
              }
            }
          }
        }
      }
    }
  }
}
```

## Output

```json
{
  "Backlog": [
    {"issue_number": 10, "title": "Future feature", "assignees": []}
  ],
  "Todo": [
    {"issue_number": 20, "title": "Ready to start", "assignees": ["dev1"]}
  ],
  "In Progress": [
    {"issue_number": 30, "title": "Being worked on", "assignees": ["dev2"]}
  ],
  "AI Review": [
    {"issue_number": 40, "title": "PR created, Integrator reviewing", "assignees": ["dev1"]}
  ],
  "Human Review": [],
  "Merge/Release": [],
  "Done": [
    {"issue_number": 50, "title": "Completed", "assignees": ["dev2"]}
  ],
  "Blocked": [
    {"issue_number": 60, "title": "Waiting for input", "assignees": ["dev1"]}
  ]
}
```

## Column Definitions

| Column | Code | Meaning |
|--------|------|---------|
| Backlog | `backlog` | Not scheduled |
| Todo | `todo` | Ready to start |
| In Progress | `in-progress` | Active work |
| AI Review | `ai-review` | Integrator reviews ALL tasks |
| Human Review | `human-review` | User reviews BIG tasks only |
| Merge/Release | `merge-release` | Ready to merge |
| Done | `done` | Completed and merged |
| Blocked | `blocked` | Cannot proceed |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Project not found | Invalid project number | Use `gh project list --owner OWNER` to find correct number |
| Auth error | gh not authenticated | Run `gh auth login` |
| Rate limit | Too many API calls | Wait for rate limit reset |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error |
| 2 | Project not found |

## Related Operations

- [op-move-card.md](op-move-card.md) - Move cards between columns
- [op-check-completion.md](op-check-completion.md) - Check if all items done
