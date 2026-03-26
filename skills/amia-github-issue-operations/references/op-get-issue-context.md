# Operation: Get Issue Context

## Table of Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Output](#output)
- [With Comments Included](#with-comments-included)
- [GraphQL Query](#graphql-query)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Use Cases](#use-cases)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-get-issue-context |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Issue Operations |
| **Agent** | api-coordinator |

## Purpose

Get complete context for a GitHub Issue including metadata, labels, assignees, milestone, linked PRs, and comments count.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- Issue exists in the repository
- User has read access

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `issue_number` | int | Yes | Issue number to query |
| `include_comments` | bool | No | Include full comment content |

## Procedure

1. Query issue metadata using gh CLI
2. Parse labels, assignees, milestone
3. Get linked PR references
4. Return structured JSON

## Command

```bash
./scripts/amia_get_issue_context.py --repo owner/repo --issue 123

# With comments
./scripts/amia_get_issue_context.py --repo owner/repo --issue 123 --include-comments
```

## Alternative: Direct gh CLI

```bash
gh issue view 123 --repo owner/repo --json number,title,state,body,labels,assignees,milestone,comments
```

## Output

```json
{
  "number": 123,
  "title": "Bug: Application crashes on startup",
  "state": "open",
  "body": "## Description\nThe app crashes when...",
  "labels": ["bug", "P1", "component:core"],
  "assignees": ["developer1"],
  "milestone": "v2.0",
  "comments_count": 5,
  "linked_prs": [456, 789],
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

## With Comments Included

```json
{
  "number": 123,
  "title": "Bug: Application crashes on startup",
  "comments": [
    {
      "author": "dev1",
      "body": "I can reproduce this...",
      "created_at": "2024-01-11T09:00:00Z"
    },
    {
      "author": "dev2",
      "body": "Found the root cause...",
      "created_at": "2024-01-12T15:00:00Z"
    }
  ]
}
```

## GraphQL Query

```graphql
query {
  repository(owner: "owner", name: "repo") {
    issue(number: 123) {
      number
      title
      state
      body
      labels(first: 20) {
        nodes { name }
      }
      assignees(first: 10) {
        nodes { login }
      }
      milestone { title }
      comments { totalCount }
      timelineItems(itemTypes: [CROSS_REFERENCED_EVENT], first: 20) {
        nodes {
          ... on CrossReferencedEvent {
            source {
              ... on PullRequest { number }
            }
          }
        }
      }
    }
  }
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Issue not found | Invalid issue number | Verify issue exists |
| Auth error | gh not authenticated | Run `gh auth login` |
| Repo not found | Invalid repo path | Check owner/repo format |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Issue not found |
| 4 | Not authenticated |

## Use Cases

1. **Before assignment** - Check issue details and current state
2. **Status check** - Get current labels and assignees
3. **Progress tracking** - Get comments count and linked PRs
4. **Context gathering** - Full issue body for agent handoff

## Related Operations

- [op-create-issue.md](op-create-issue.md) - Create new issues
- [op-set-issue-labels.md](op-set-issue-labels.md) - Update labels after review
