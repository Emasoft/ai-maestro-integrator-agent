---
name: op-batch-label-add
description: "Bulk add labels to multiple GitHub issues at once"
procedure: support-skill
workflow-instruction: support
---

# Operation: Batch Label Add


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: List target issues](#step-1-list-target-issues)
  - [Step 2: Preview changes (dry-run)](#step-2-preview-changes-dry-run)
  - [Step 3: Execute batch add](#step-3-execute-batch-add)
  - [Step 4: Verify changes](#step-4-verify-changes)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Error Handling](#error-handling)
  - [Label does not exist](#label-does-not-exist)
  - [Permission denied](#permission-denied)
- [Verification](#verification)

## Purpose

Add one or more labels to multiple GitHub issues in a single operation.

## When to Use

- Adding a new label category to all issues matching certain criteria
- Applying priority labels to a batch of related issues
- Adding milestone or sprint labels to multiple issues

## Prerequisites

1. GitHub CLI authenticated (`gh auth status`)
2. Write access to repository issues
3. Target labels must exist in repository

## Procedure

### Step 1: List target issues

```bash
# Get issue numbers matching criteria
gh issue list --label "feature" --state open --json number --jq '.[].number'
```

### Step 2: Preview changes (dry-run)

```bash
# Preview which issues will be modified
gh issue list --label "feature" --state open --json number,title --jq '.[] | "\(.number): \(.title)"'
```

### Step 3: Execute batch add

```bash
# Add label to all matching issues
gh issue list --label "feature" --state open --json number --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "priority:high"
```

### Step 4: Verify changes

```bash
# Confirm labels were added
gh issue list --label "priority:high" --state open --json number,labels
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter_label | string | yes | Label to filter issues by |
| filter_state | string | no | Issue state (open/closed/all) |
| add_labels | string[] | yes | Labels to add to matching issues |

## Output

| Field | Type | Description |
|-------|------|-------------|
| issues_modified | number | Count of issues modified |
| labels_added | string[] | Labels that were added |
| errors | string[] | Any issues that failed to update |

## Example Output

```json
{
  "issues_modified": 12,
  "labels_added": ["priority:high"],
  "errors": []
}
```

## Error Handling

### Label does not exist

**Cause**: Attempting to add a label that doesn't exist in repository.

**Solution**: Create the label first with `gh label create "label-name" --color "FF0000"`.

### Permission denied

**Cause**: User lacks write access to issues.

**Solution**: Verify repository permissions with `gh repo view --json viewerPermission`.

## Verification

After execution, verify success:

```bash
# Count issues with new label
gh issue list --label "priority:high" --state all --json number | jq 'length'
```
