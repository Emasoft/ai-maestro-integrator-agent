# GitHub Issue Operations — Detailed Guide

## Contents

- [Decision Tree](#decision-tree)
- [Script Reference Table](#script-reference-table)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Exit Codes](#exit-codes)
- [Integration with Integrator Agent](#integration-with-integrator-agent)

## Decision Tree

```
Need to work with GitHub Issues?
|
+---> Need issue information?
|     Use: amia_get_issue_context.py
|     Returns: title, body, state, labels, assignees, milestone, comments count, linked PRs
|
+---> Need to create a new issue?
|     Use: amia_create_issue.py
|     Requires: --title, optional: --body, --labels, --assignee
|     Returns: issue number and URL
|
+---> Need to manage labels?
|     Adding labels? -> amia_set_issue_labels.py --add "label1,label2"
|     Removing labels? -> amia_set_issue_labels.py --remove "label1"
|     Setting exact labels? -> amia_set_issue_labels.py --set "label1,label2"
|     Note: Auto-creates missing labels if they don't exist
|
+---> Need to assign to milestone?
|     Use: amia_set_issue_milestone.py
|     Option: --create-if-missing to auto-create milestone
|
+---> Need to post a comment?
      Use: amia_post_issue_comment.py
      Option: --marker for idempotent comments (won't duplicate)
```

## Script Reference Table

| Script | Purpose | Required Args | Optional Args | Output |
|--------|---------|---------------|---------------|--------|
| `amia_get_issue_context.py` | Get issue metadata | `--repo`, `--issue` | `--include-comments` | JSON with issue details |
| `amia_create_issue.py` | Create new issue | `--repo`, `--title` | `--body`, `--labels`, `--assignee`, `--milestone` | JSON with number, URL |
| `amia_set_issue_labels.py` | Manage labels | `--repo`, `--issue` | `--add`, `--remove`, `--set`, `--auto-create` | JSON with updated labels |
| `amia_set_issue_milestone.py` | Assign milestone | `--repo`, `--issue`, `--milestone` | `--create-if-missing` | JSON with milestone info |
| `amia_post_issue_comment.py` | Post comment | `--repo`, `--issue`, `--body` | `--marker` | JSON with comment ID, URL |

## Examples

### Get Issue Context

```bash
./scripts/amia_get_issue_context.py --repo owner/repo --issue 123

# Output:
{
  "number": 123,
  "title": "Bug: Application crashes on startup",
  "state": "open",
  "labels": ["bug", "P1"],
  "assignees": ["developer1"],
  "milestone": "v2.0",
  "comments_count": 5,
  "linked_prs": [456, 789]
}
```

### Create Issue

```bash
./scripts/amia_create_issue.py \
  --repo owner/repo \
  --title "Implement new feature X" \
  --body "## Description\nFeature details here" \
  --labels "feature,P2" \
  --assignee "developer1"

# Output:
{
  "number": 124,
  "url": "https://github.com/owner/repo/issues/124"
}
```

### Manage Labels

```bash
# Add labels (auto-creates if missing)
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
```

### Assign Milestone

```bash
# Assign to existing milestone
./scripts/amia_set_issue_milestone.py \
  --repo owner/repo \
  --issue 123 \
  --milestone "v2.0"

# Create milestone if it doesn't exist
./scripts/amia_set_issue_milestone.py \
  --repo owner/repo \
  --issue 123 \
  --milestone "v3.0" \
  --create-if-missing
```

### Post Idempotent Comment

```bash
./scripts/amia_post_issue_comment.py \
  --repo owner/repo \
  --issue 123 \
  --body "## Status Update\nTask completed successfully." \
  --marker "status-update-2024-01-15"

# Output:
{
  "comment_id": 12345,
  "url": "https://github.com/owner/repo/issues/123#issuecomment-12345",
  "created": true  # false if marker already existed
}
```

## Error Handling

All scripts return JSON with an `error` field on failure:

```json
{
  "error": true,
  "message": "Issue not found: 999",
  "code": "ISSUE_NOT_FOUND"
}
```

Common error codes:

- `AUTH_REQUIRED`: gh CLI not authenticated
- `REPO_NOT_FOUND`: Repository doesn't exist or no access
- `ISSUE_NOT_FOUND`: Issue number doesn't exist
- `LABEL_CREATE_FAILED`: Failed to create label
- `MILESTONE_NOT_FOUND`: Milestone doesn't exist (without --create-if-missing)
- `PERMISSION_DENIED`: Insufficient permissions

### Troubleshooting

**"gh: command not found"** — Install gh CLI: `brew install gh` (macOS), `sudo apt install gh` (Debian/Ubuntu), `sudo dnf install gh` (Fedora).

**"not logged into any GitHub hosts"** — Run `gh auth login`.

**Labels not being created** — Ensure you have write access (at least "triage" permission).

**Milestone assignment fails silently** — Check milestone exists or use `--create-if-missing`.

**Duplicate comments being posted** — Use the `--marker` flag with a unique identifier.

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Invalid parameters | Missing required args, bad format |
| 2 | Resource not found | Issue, repo, milestone, or labels not found |
| 3 | API error | Network, rate limit, timeout |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | Comment with marker already exists |
| 6 | Not mergeable | N/A for these scripts |

Note: `amia_post_issue_comment.py` returns exit code 5 when a comment with the specified `--marker` already exists. The JSON output will have `"created": false`.

## Integration with Integrator Agent

This skill integrates with the Integrator Agent workflow:

1. **Task Creation:** When orchestrator receives a new task, use `amia_create_issue.py` to create a tracking issue
2. **Progress Updates:** Use `amia_post_issue_comment.py` with markers to post status updates
3. **Completion:** Use `amia_set_issue_labels.py` to mark issues as completed
4. **Milestone Tracking:** Use `amia_set_issue_milestone.py` to organize work into releases

See the main Integrator Agent documentation for workflow integration details.

## Reference Document Listings (moved from SKILL.md)

**Operations:**

- `references/op-get-issue-context.md` — Get issue metadata and context
- `references/op-create-issue.md` — Create new issues
- `references/op-set-issue-labels.md` — Add, remove, or set labels
- `references/op-set-issue-milestone.md` — Assign milestones
- `references/op-post-issue-comment.md` — Post comments with idempotency

**Guides:**

- `references/label-management.md` — Label creation, naming, priorities, categories
- `references/issue-templates.md` — Bug report, feature request, task templates
- `references/milestone-tracking.md` — Milestone creation, assignment, progress

**Template Parts:**

- `references/issue-templates-part1-bug-reports.md` — Bug report templates
- `references/issue-templates-part2-feature-requests.md` — Feature request templates
- `references/issue-templates-part3-tasks.md` — Task templates
- `references/issue-templates-part4-programmatic.md` — Programmatic template usage
- `references/milestone-tracking-part1-creating.md` — Creating milestones
- `references/milestone-tracking-part2-assigning.md` — Assigning issues to milestones
- `references/milestone-tracking-part3-progress-closing.md` — Progress tracking and closing

**Resources:**

- `references/issue-templates-part1-bug-reports.md`
- `references/issue-templates-part2-feature-requests.md`
- `references/issue-templates-part3-tasks.md`
- `references/issue-templates-part4-programmatic.md`
- `references/issue-templates.md`
- `references/label-management.md`
- `references/milestone-tracking-part1-creating.md`
- ...and 8 more in `references/`
