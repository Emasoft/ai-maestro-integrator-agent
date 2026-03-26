# Operation: Add Issue Comment

## Table of Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command: Basic Comment](#command-basic-comment)
- [Command: With Marker (Idempotent)](#command-with-marker-idempotent)
- [GraphQL Mutation](#graphql-mutation)
- [Output](#output)
- [Comment Templates](#comment-templates)
  - [Status Update](#status-update)
- [Status Update](#status-update)
  - [Progress](#progress)
  - [Blockers](#blockers)
  - [Next Steps](#next-steps)
  - [Blocker Report](#blocker-report)
- [Blocker Reported](#blocker-reported)
  - [Blocker Description](#blocker-description)
  - [Impact](#impact)
  - [Needed Action](#needed-action)
  - [Completion Notice](#completion-notice)
- [Task Completed](#task-completed)
  - [Summary](#summary)
  - [PR Link](#pr-link)
  - [Notes](#notes)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-add-issue-comment |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Projects Sync |
| **Agent** | api-coordinator |

## Purpose

Add a comment to a GitHub Issue for status updates, progress tracking, or coordination notes.

## Preconditions

- Issue exists
- User has write access to the repository

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `issue_number` | int | Yes | Issue to comment on |
| `body` | string | Yes | Comment body (Markdown) |
| `marker` | string | No | Unique marker for idempotent comments |

## Procedure

1. Check if marker exists (if provided) to avoid duplicates
2. Format the comment body with Markdown
3. Post the comment to the issue
4. Return comment ID and URL

## Command: Basic Comment

```bash
gh issue comment 42 --repo owner/repo --body "## Status Update
Work in progress. Estimated completion: 2 hours."
```

## Command: With Marker (Idempotent)

Using the amia script for idempotent comments:

```bash
./scripts/amia_post_issue_comment.py \
  --repo owner/repo \
  --issue 42 \
  --body "## Status Update
Work in progress." \
  --marker "status-update-2024-01-15"
```

If the marker already exists in a comment, no duplicate is created.

## GraphQL Mutation

```graphql
mutation {
  addComment(
    input: {
      subjectId: "I_kwDO..."  # Issue node ID
      body: "## Status Update\nWork in progress."
    }
  ) {
    commentEdge {
      node {
        id
        url
      }
    }
  }
}
```

## Output

```json
{
  "comment_id": 12345,
  "url": "https://github.com/owner/repo/issues/42#issuecomment-12345",
  "created": true
}
```

If marker exists (no duplicate created):

```json
{
  "comment_id": null,
  "created": false,
  "reason": "Marker 'status-update-2024-01-15' already exists"
}
```

## Comment Templates

### Status Update

```markdown
## Status Update

**Date:** 2024-01-15
**Agent:** implementer-1

### Progress
- [x] Completed task A
- [x] Completed task B
- [ ] In progress: task C

### Blockers
None

### Next Steps
Complete task C, then submit PR.
```

### Blocker Report

```markdown
## Blocker Reported

**Date:** 2024-01-15
**Agent:** implementer-1
**Previous Status:** In Progress

### Blocker Description
Missing AWS credentials for staging deployment.

### Impact
Cannot complete integration testing.

### Needed Action
DevOps team to provision credentials.
```

### Completion Notice

```markdown
## Task Completed

**Date:** 2024-01-15
**Agent:** implementer-1

### Summary
Implemented authentication module with all acceptance criteria met.

### PR Link
#50

### Notes
Ready for review.
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Issue not found | Invalid issue number | Verify issue exists |
| Permission denied | No write access | Check repository permissions |
| Rate limit | Too many API calls | Wait for rate limit reset |

## Best Practices

1. Use structured Markdown for readability
2. Include date and agent name for tracking
3. Use markers for idempotent status updates
4. Link related PRs and issues
5. Keep comments focused and concise

## Related Operations

- [op-link-pr-to-issue.md](op-link-pr-to-issue.md) - Link PR after comment
- [op-update-item-status.md](op-update-item-status.md) - Update status after comment
