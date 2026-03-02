# Operation: Set Issue Milestone


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Output](#output)
- [Creating Milestones](#creating-milestones)
- [Milestone Conventions](#milestone-conventions)
- [Remove Milestone](#remove-milestone)
- [Query Milestone Progress](#query-milestone-progress)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Best Practices](#best-practices)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-set-issue-milestone |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Issue Operations |
| **Agent** | api-coordinator |

## Purpose

Assign a GitHub Issue to a milestone for release tracking and progress monitoring.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- Issue exists in the repository
- Milestone exists (or will be created with `--create-if-missing`)
- User has write access

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `issue_number` | int | Yes | Issue to update |
| `milestone` | string | Yes | Milestone title |
| `create_if_missing` | bool | No | Create milestone if it doesn't exist |

## Procedure

1. Check if milestone exists
2. If not and `--create-if-missing`, create it
3. Assign issue to milestone
4. Return milestone info

## Command

```bash
# Assign to existing milestone
./scripts/amia_set_issue_milestone.py \
  --repo owner/repo \
  --issue 123 \
  --milestone "v2.0"

# Create milestone if missing
./scripts/amia_set_issue_milestone.py \
  --repo owner/repo \
  --issue 123 \
  --milestone "v3.0" \
  --create-if-missing
```

## Alternative: Direct gh CLI

```bash
gh issue edit 123 --repo owner/repo --milestone "v2.0"
```

## Output

```json
{
  "issue_number": 123,
  "milestone": "v2.0",
  "milestone_url": "https://github.com/owner/repo/milestone/5",
  "created_milestone": false
}
```

If milestone was created:
```json
{
  "issue_number": 123,
  "milestone": "v3.0",
  "milestone_url": "https://github.com/owner/repo/milestone/6",
  "created_milestone": true
}
```

## Creating Milestones

```bash
# Create milestone with due date
gh api repos/owner/repo/milestones -f title="v3.0" -f description="Version 3.0 release" -f due_on="2024-03-01T00:00:00Z"

# List milestones
gh api repos/owner/repo/milestones | jq '.[].title'
```

## Milestone Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| Version | `v2.0`, `v2.1.0` | Release milestones |
| Sprint | `Sprint 5`, `2024-W15` | Sprint tracking |
| Quarter | `Q1-2024` | Quarterly planning |
| Phase | `Phase 1: Foundation` | Project phases |

## Remove Milestone

To remove an issue from its milestone:

```bash
gh issue edit 123 --repo owner/repo --milestone ""
```

## Query Milestone Progress

```bash
# Get milestone with progress
gh api repos/owner/repo/milestones | jq '.[] | {title, open_issues, closed_issues, due_on}'
```

Output:
```json
{
  "title": "v2.0",
  "open_issues": 5,
  "closed_issues": 12,
  "due_on": "2024-02-01T00:00:00Z"
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Milestone not found | Doesn't exist | Use `--create-if-missing` or create manually |
| Issue not found | Invalid issue number | Verify issue exists |
| Permission denied | No write access | Check repository permissions |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Resource not found |
| 4 | Not authenticated |

## Best Practices

1. Use semantic versioning for release milestones
2. Set due dates for tracking
3. Keep milestone names short but descriptive
4. Close milestones when all issues are done
5. Use milestone description for goals/scope

## Related Operations

- [op-create-issue.md](op-create-issue.md) - Set milestone at creation
- [op-get-issue-context.md](op-get-issue-context.md) - Check current milestone
