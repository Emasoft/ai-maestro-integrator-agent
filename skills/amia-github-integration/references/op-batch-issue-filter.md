---
name: op-batch-issue-filter
description: "Filter GitHub issues by multiple criteria for batch operations"
procedure: support-skill
workflow-instruction: support
---

# Operation: Batch Issue Filter


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Define filter criteria](#step-1-define-filter-criteria)
  - [Step 2: Build filter command](#step-2-build-filter-command)
  - [Step 3: Apply date filtering](#step-3-apply-date-filtering)
  - [Step 4: Extract issue numbers](#step-4-extract-issue-numbers)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Common Filter Patterns](#common-filter-patterns)
  - [Stale issues (no update in 30 days)](#stale-issues-no-update-in-30-days)
  - [Unassigned high-priority bugs](#unassigned-high-priority-bugs)
  - [Issues without labels](#issues-without-labels)
- [Error Handling](#error-handling)
  - [No issues match filter](#no-issues-match-filter)
  - [Invalid label name](#invalid-label-name)
- [Verification](#verification)

## Purpose

Filter GitHub issues using multiple criteria (labels, state, assignee, date) to build a target set for batch operations.

## When to Use

- Before any batch operation to identify target issues
- When generating reports on issue subsets
- When auditing issues by multiple dimensions

## Prerequisites

1. GitHub CLI authenticated (`gh auth status`)
2. Read access to repository issues

## Procedure

### Step 1: Define filter criteria

Determine which combination of filters to apply:
- Labels (one or multiple)
- State (open/closed/all)
- Assignee
- Date range (created/updated)
- Milestone

### Step 2: Build filter command

```bash
# Single label filter
gh issue list --label "bug" --state open

# Multiple labels (AND logic)
gh issue list --label "bug" --label "priority:high" --state open

# With assignee
gh issue list --label "bug" --assignee "@me" --state open

# With milestone
gh issue list --label "bug" --milestone "v1.0" --state open
```

### Step 3: Apply date filtering

```bash
# Issues created after date
gh issue list --state all --json number,createdAt --jq '.[] | select(.createdAt > "2025-01-01")'

# Issues not updated in 30 days
gh issue list --state open --json number,updatedAt --jq '.[] | select(.updatedAt < (now - 2592000 | strftime("%Y-%m-%d")))'
```

### Step 4: Extract issue numbers

```bash
# Get just the numbers for batch operations
gh issue list --label "bug" --state open --json number --jq '.[].number'
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| labels | string[] | no | Labels to filter by (AND logic) |
| state | string | no | Issue state: open/closed/all |
| assignee | string | no | Assignee username or @me |
| milestone | string | no | Milestone name |
| created_after | date | no | Filter by creation date |
| updated_before | date | no | Filter by last update |

## Output

| Field | Type | Description |
|-------|------|-------------|
| issue_numbers | number[] | List of matching issue numbers |
| issue_count | number | Total count of matching issues |
| filter_applied | object | Summary of filters used |

## Example Output

```json
{
  "issue_numbers": [12, 15, 23, 45, 67],
  "issue_count": 5,
  "filter_applied": {
    "labels": ["bug", "priority:high"],
    "state": "open",
    "assignee": null,
    "milestone": null
  }
}
```

## Common Filter Patterns

### Stale issues (no update in 30 days)

```bash
gh issue list --state open --json number,updatedAt | \
  jq --arg cutoff "$(date -v-30d +%Y-%m-%d)" '.[] | select(.updatedAt < $cutoff) | .number'
```

### Unassigned high-priority bugs

```bash
gh issue list --label "bug" --label "priority:high" --state open --json number,assignees | \
  jq '.[] | select(.assignees | length == 0) | .number'
```

### Issues without labels

```bash
gh issue list --state open --json number,labels | \
  jq '.[] | select(.labels | length == 0) | .number'
```

## Error Handling

### No issues match filter

**Cause**: Filter criteria too restrictive or no matching issues exist.

**Solution**: Broaden filter criteria or verify expected issues exist.

### Invalid label name

**Cause**: Label name doesn't exist in repository.

**Solution**: List available labels with `gh label list` and verify spelling.

## Verification

Validate filter results before batch operations:

```bash
# Show summary of matching issues
gh issue list --label "bug" --state open --json number,title,labels | jq 'length'
```
