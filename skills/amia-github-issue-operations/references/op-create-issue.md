# Operation: Create Issue

## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Output](#output)
- [Issue Body Templates](#issue-body-templates)
  - [Feature Request](#feature-request)
- [Description](#description)
- [Motivation](#motivation)
- [Acceptance Criteria](#acceptance-criteria)
- [Technical Notes](#technical-notes)
  - [Bug Report](#bug-report)
- [Description](#description)
- [Steps to Reproduce](#steps-to-reproduce)
- [Expected Behavior](#expected-behavior)
- [Actual Behavior](#actual-behavior)
- [Environment](#environment)
  - [Task](#task)
- [Description](#description)
- [Requirements](#requirements)
- [Dependencies](#dependencies)
- [Acceptance Criteria](#acceptance-criteria)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Auto-Create Labels](#auto-create-labels)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-create-issue |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Issue Operations |
| **Agent** | api-coordinator |

## Purpose

Create a new GitHub Issue with title, body, labels, and assignee.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- User has write access to the repository
- Required labels exist (or will be auto-created)

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `title` | string | Yes | Issue title |
| `body` | string | No | Issue body (Markdown) |
| `labels` | string | No | Comma-separated labels |
| `assignee` | string | No | GitHub username to assign |
| `milestone` | string | No | Milestone title |

## Procedure

1. Validate required parameters
2. Create issue using gh CLI
3. Apply labels and assignee
4. Return issue number and URL

## Command

```bash
./scripts/amia_create_issue.py \
  --repo owner/repo \
  --title "Implement new feature X" \
  --body "## Description\nFeature details here" \
  --labels "feature,P2" \
  --assignee "developer1"
```

## Alternative: Direct gh CLI

```bash
gh issue create \
  --repo owner/repo \
  --title "Implement new feature X" \
  --body "## Description
Feature details here" \
  --label "feature,P2" \
  --assignee "developer1"
```

## Output

```json
{
  "number": 124,
  "url": "https://github.com/owner/repo/issues/124"
}
```

## Issue Body Templates

### Feature Request

```markdown
## Description
<What the feature does>

## Motivation
<Why this feature is needed>

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Technical Notes
<Implementation hints>
```

### Bug Report

```markdown
## Description
<What is happening>

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
<What should happen>

## Actual Behavior
<What actually happens>

## Environment
- OS:
- Version:
```

### Task

```markdown
## Description
<Task description>

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Dependencies
blockedBy: []
blocks: []

## Acceptance Criteria
- [ ] Criteria 1
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Repo not found | Invalid repository | Check owner/repo format |
| Permission denied | No write access | Verify repository permissions |
| Label not found | Label doesn't exist | Use auto-create or create labels first |
| Invalid assignee | User not found | Verify username exists |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Resource not found |
| 4 | Not authenticated |

## Auto-Create Labels

If labels don't exist, they can be auto-created:

```bash
# Check if label exists
gh label list --repo owner/repo | grep "feature"

# Create if missing
gh label create "feature" --repo owner/repo --color "0E8A16" --description "New feature"
```

## Related Operations

- [op-get-issue-context.md](op-get-issue-context.md) - Verify created issue
- [op-set-issue-labels.md](op-set-issue-labels.md) - Update labels later
- [op-set-issue-milestone.md](op-set-issue-milestone.md) - Assign to milestone
