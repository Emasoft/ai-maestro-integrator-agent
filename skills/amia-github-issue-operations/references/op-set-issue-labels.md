# Operation: Set Issue Labels

## Table of Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Output](#output)
- [Label Auto-Creation](#label-auto-creation)
  - [Default Colors by Category](#default-colors-by-category)
- [Standard Label Categories](#standard-label-categories)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Best Practices](#best-practices)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-set-issue-labels |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Issue Operations |
| **Agent** | api-coordinator |

## Purpose

Add, remove, or set labels on a GitHub Issue. Supports auto-creating missing labels.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- Issue exists in the repository
- User has write access (triage permission for labels)

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `issue_number` | int | Yes | Issue to update |
| `add` | string | No | Comma-separated labels to add |
| `remove` | string | No | Comma-separated labels to remove |
| `set` | string | No | Exact labels to set (replaces all) |
| `auto_create` | bool | No | Auto-create missing labels |

## Procedure

1. Validate at least one operation is specified
2. If auto_create, check and create missing labels
3. Perform label operation (add/remove/set)
4. Return updated label list

## Command

```bash
# Add labels
./scripts/amia_set_issue_labels.py \
  --repo owner/repo \
  --issue 123 \
  --add "in-progress,ai-review" \
  --auto-create

# Remove labels
./scripts/amia_set_issue_labels.py \
  --repo owner/repo \
  --issue 123 \
  --remove "backlog"

# Set exact labels (replaces all existing)
./scripts/amia_set_issue_labels.py \
  --repo owner/repo \
  --issue 123 \
  --set "bug,P1,in-progress"
```

## Alternative: Direct gh CLI

```bash
# Add labels
gh issue edit 123 --repo owner/repo --add-label "in-progress,ai-review"

# Remove labels
gh issue edit 123 --repo owner/repo --remove-label "backlog"
```

## Output

```json
{
  "issue_number": 123,
  "labels_added": ["in-progress", "ai-review"],
  "labels_removed": [],
  "current_labels": ["bug", "P1", "in-progress", "ai-review"]
}
```

## Label Auto-Creation

When `--auto-create` is specified and a label doesn't exist:

```bash
# Default colors by category
gh label create "in-progress" --color "FEF2C0" --description "Work in progress"
gh label create "ai-review" --color "C2E0C6" --description "Ready for AI review"
```

### Default Colors by Category

| Category | Color | Example Labels |
|----------|-------|----------------|
| Priority | Red shades | P0 (#FF0000), P1 (#FF6B6B) |
| Status | Yellow/Green | in-progress (#FEF2C0), done (#0E8A16) |
| Type | Blue shades | bug (#D73A4A), feature (#0075CA) |
| Component | Purple | api (#7057FF), ui (#FBCA04) |

## Standard Label Categories

| Category | Format | Examples |
|----------|--------|----------|
| Priority | `P0` - `P4` | P0 (critical), P1 (high), P2 (normal) |
| Type | `type:*` | type:bug, type:feature, type:task |
| Status | `status:*` | status:ready, status:in-progress |
| Component | `component:*` | component:api, component:ui |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Issue not found | Invalid issue number | Verify issue exists |
| Label not found | Label doesn't exist | Use `--auto-create` flag |
| Permission denied | No triage access | Check repository permissions |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Issue not found |
| 4 | Not authenticated |

## Best Practices

1. Use kebab-case for label names
2. Use category prefixes (type:, status:, component:)
3. Keep label count manageable (< 10 per issue)
4. Use `--set` sparingly (removes all existing labels)
5. Auto-create labels for consistency across repos

## Related Operations

- [op-get-issue-context.md](op-get-issue-context.md) - Check current labels
- [op-create-issue.md](op-create-issue.md) - Set labels at creation
