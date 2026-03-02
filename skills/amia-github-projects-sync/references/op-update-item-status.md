# Operation: Update Project Item Status


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Getting Field and Option IDs](#getting-field-and-option-ids)
  - [Get Status Field ID](#get-status-field-id)
  - [Example Response](#example-response)
- [GraphQL Mutation](#graphql-mutation)
- [Command](#command)
- [Using gh CLI](#using-gh-cli)
- [Output](#output)
- [Standard Status Options](#standard-status-options)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-update-item-status |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Projects Sync |
| **Agent** | api-coordinator |

## Purpose

Update the Status field of a project item to move it between columns on the Kanban board.

## Preconditions

- Project ID and item ID are known
- Status field ID and option IDs are known
- User has write access to the project

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | GraphQL project ID (PVT_...) |
| `item_id` | string | Yes | GraphQL item ID (PVTI_...) |
| `field_id` | string | Yes | Status field ID (PVTSSF_...) |
| `option_id` | string | Yes | Target status option ID |

## Getting Field and Option IDs

### Get Status Field ID

```graphql
query {
  node(id: "PVT_kwDO...") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}
```

### Example Response

```json
{
  "id": "PVTSSF_lADO...",
  "name": "Status",
  "options": [
    {"id": "47fc9ee4", "name": "Backlog"},
    {"id": "98236657", "name": "Todo"},
    {"id": "f75ad846", "name": "In Progress"},
    {"id": "47fc9ee5", "name": "AI Review"},
    {"id": "a1b2c3d4", "name": "Human Review"},
    {"id": "e5f6g7h8", "name": "Merge/Release"},
    {"id": "98236658", "name": "Done"},
    {"id": "f75ad847", "name": "Blocked"}
  ]
}
```

## GraphQL Mutation

```graphql
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "PVT_kwDO..."
      itemId: "PVTI_..."
      fieldId: "PVTSSF_..."
      value: {
        singleSelectOptionId: "f75ad846"  # In Progress
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}
```

## Command

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "PVT_kwDO..."
      itemId: "PVTI_..."
      fieldId: "PVTSSF_..."
      value: { singleSelectOptionId: "f75ad846" }
    }
  ) {
    projectV2Item { id }
  }
}'
```

## Using gh CLI

```bash
gh project item-edit \
  --id ITEM_ID \
  --field-id FIELD_ID \
  --project-id PROJECT_ID \
  --single-select-option-id OPTION_ID
```

## Output

```json
{
  "data": {
    "updateProjectV2ItemFieldValue": {
      "projectV2Item": {
        "id": "PVTI_..."
      }
    }
  }
}
```

## Standard Status Options

| Status | Typical Option ID Pattern |
|--------|---------------------------|
| Backlog | Varies per project |
| Todo | Varies per project |
| In Progress | Varies per project |
| AI Review | Varies per project |
| Human Review | Varies per project |
| Merge/Release | Varies per project |
| Done | Varies per project |
| Blocked | Varies per project |

**Note:** Option IDs are project-specific. Always query the project to get correct IDs.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Field not found | Invalid field ID | Query project fields first |
| Option not found | Invalid option ID | Query field options first |
| Item not found | Invalid item ID | Verify item exists on board |
| Permission denied | No write access | Check project permissions |

## Related Operations

- [op-query-project-items.md](op-query-project-items.md) - Get item IDs
- [op-find-project.md](op-find-project.md) - Get project ID
