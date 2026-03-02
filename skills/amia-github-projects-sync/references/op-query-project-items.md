# Operation: Query Project Items


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [GraphQL Query](#graphql-query)
- [Command: Using gh CLI](#command-using-gh-cli)
- [Output](#output)
- [Filtering by Status](#filtering-by-status)
- [Pagination](#pagination)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-query-project-items |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Projects Sync |
| **Agent** | api-coordinator |

## Purpose

Query all items (issues, PRs, draft items) in a GitHub Projects V2 project with their field values.

## Preconditions

- Project ID is known (see op-find-project)
- User has read access to the project

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | GraphQL project ID (PVT_...) |
| `first` | int | No | Number of items to fetch (default: 100) |
| `status_filter` | string | No | Filter by status column |

## Procedure

1. Query project items via GraphQL
2. Include status field value for each item
3. Include content details (issue/PR data)
4. Return structured list of items

## GraphQL Query

```graphql
query {
  node(id: "PVT_kwDO...") {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
              optionId
            }
          }
          content {
            ... on Issue {
              number
              title
              state
              url
              assignees(first: 5) {
                nodes { login }
              }
              labels(first: 10) {
                nodes { name }
              }
            }
            ... on PullRequest {
              number
              title
              state
              url
              isDraft
              mergeable
            }
            ... on DraftIssue {
              title
              body
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
```

## Command: Using gh CLI

```bash
gh project item-list PROJECT_NUMBER --owner OWNER --format json
```

## Output

```json
{
  "items": [
    {
      "id": "PVTI_...",
      "status": "In Progress",
      "content_type": "Issue",
      "number": 42,
      "title": "Implement feature X",
      "state": "OPEN",
      "assignees": ["dev1"],
      "labels": ["type:feature", "priority:high"]
    },
    {
      "id": "PVTI_...",
      "status": "AI Review",
      "content_type": "PullRequest",
      "number": 50,
      "title": "Add feature X",
      "state": "OPEN",
      "is_draft": false,
      "mergeable": "MERGEABLE"
    }
  ],
  "total_count": 25,
  "has_next_page": false
}
```

## Filtering by Status

```bash
# Get only in-progress items
gh project item-list PROJECT_NUMBER --owner OWNER --format json | \
  jq '.items[] | select(.status == "In Progress")'
```

## Pagination

For large projects (>100 items), use cursor-based pagination:

```graphql
query($cursor: String) {
  node(id: "PVT_...") {
    ... on ProjectV2 {
      items(first: 100, after: $cursor) {
        nodes { ... }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Node not found | Invalid project ID | Verify project ID format |
| Empty result | No items on board | Normal - board is empty |
| Rate limit | Too many queries | Wait for rate limit reset |

## Related Operations

- [op-find-project.md](op-find-project.md) - Get project ID first
- [op-update-item-status.md](op-update-item-status.md) - Update item after query
