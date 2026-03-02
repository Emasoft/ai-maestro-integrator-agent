# Operation: Post Issue Comment


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Marker-Based Idempotency](#marker-based-idempotency)
- [Status Update](#status-update)
- [Procedure](#procedure)
- [Command](#command)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Output](#output)
- [Comment Templates](#comment-templates)
  - [Status Update](#status-update)
- [Status Update](#status-update)
  - [Progress](#progress)
  - [Next Steps](#next-steps)
  - [Blocker Report](#blocker-report)
- [Blocker Reported](#blocker-reported)
  - [Description](#description)
  - [Impact](#impact)
  - [Needed](#needed)
  - [Completion Notice](#completion-notice)
- [Task Completed](#task-completed)
  - [Summary](#summary)
  - [PR](#pr)
  - [Notes](#notes)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Best Practices](#best-practices)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-post-issue-comment |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Issue Operations |
| **Agent** | api-coordinator |

## Purpose

Post a comment to a GitHub Issue with support for idempotent comments using markers.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- Issue exists in the repository
- User has write access

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `issue_number` | int | Yes | Issue to comment on |
| `body` | string | Yes | Comment body (Markdown) |
| `marker` | string | No | Unique marker for idempotent posting |

## Marker-Based Idempotency

When `--marker` is provided:
1. Script checks existing comments for the marker
2. If marker found, no duplicate is created
3. If not found, comment is posted with marker embedded

Marker format in comment:
```markdown
<!-- marker: status-update-2024-01-15 -->
## Status Update
...
```

## Procedure

1. If marker provided, check for existing marker in comments
2. If marker exists, return without posting
3. Format comment body (add marker if provided)
4. Post comment to issue
5. Return comment ID and URL

## Command

```bash
# Simple comment
./scripts/amia_post_issue_comment.py \
  --repo owner/repo \
  --issue 123 \
  --body "## Status Update
Work in progress. Estimated completion: 2 hours."

# Idempotent comment with marker
./scripts/amia_post_issue_comment.py \
  --repo owner/repo \
  --issue 123 \
  --body "## Status Update
Task completed successfully." \
  --marker "status-update-2024-01-15"
```

## Alternative: Direct gh CLI

```bash
gh issue comment 123 --repo owner/repo --body "## Status Update
Work in progress."
```

## Output

Comment created:
```json
{
  "comment_id": 12345,
  "url": "https://github.com/owner/repo/issues/123#issuecomment-12345",
  "created": true
}
```

Marker already exists (no duplicate):
```json
{
  "comment_id": null,
  "url": null,
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

### Next Steps
Complete task C, then submit PR.
```

### Blocker Report

```markdown
## Blocker Reported

**Date:** 2024-01-15
**Previous Status:** In Progress

### Description
Missing AWS credentials for staging deployment.

### Impact
Cannot complete integration testing.

### Needed
DevOps team to provision credentials.
```

### Completion Notice

```markdown
## Task Completed

**Date:** 2024-01-15
**Agent:** implementer-1

### Summary
Implemented authentication module.

### PR
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

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (comment created) |
| 2 | Issue not found |
| 4 | Not authenticated |
| 5 | Marker already exists (idempotency skip) |

**Note:** Exit code 5 is not an error - it means the operation was successfully skipped due to idempotency.

## Best Practices

1. Use markers for automated status updates
2. Include date and agent name
3. Use Markdown headers for structure
4. Keep comments focused and concise
5. Link related PRs and issues
6. Use markers with timestamps for unique identification

## Related Operations

- [op-get-issue-context.md](op-get-issue-context.md) - Check existing comments
- [op-set-issue-labels.md](op-set-issue-labels.md) - Update labels with comment
