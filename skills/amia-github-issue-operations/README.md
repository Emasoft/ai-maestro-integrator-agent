# GitHub Issue Operations Skill

Comprehensive GitHub Issue management using `gh` CLI - create issues, manage labels, assign milestones, and post comments programmatically.

## When to Use

- Creating issues from automated orchestrator workflows
- Querying issue metadata and context
- Managing issue labels and categorization
- Tracking progress via milestones
- Posting automated status updates or comments

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Write access to target repository
- `jq` available for JSON processing

## Quick Reference

| Script | Purpose |
|--------|---------|
| `amia_get_issue_context.py` | Get issue metadata (title, state, labels, assignees, milestone) |
| `amia_create_issue.py` | Create new issue with optional labels/assignee |
| `amia_set_issue_labels.py` | Add, remove, or set labels (supports `--auto-create`) |
| `amia_set_issue_milestone.py` | Assign issue to milestone |
| `amia_post_issue_comment.py` | Post comment (supports idempotent markers) |

## Key Features

- **Idempotent comments**: Use `--marker` flag to prevent duplicate comments
- **Auto-create labels**: `--auto-create` flag creates missing labels automatically
- **Auto-create milestones**: `--create-if-missing` flag for milestone assignment
- **Standardized exit codes**: Consistent error handling across all scripts
- **JSON output**: All scripts return structured JSON for easy parsing

## Reference Documents

- [Label Management](references/label-management.md) - Label conventions, priorities, auto-creation
- [Issue Templates](references/issue-templates.md) - Bug reports, feature requests, tasks
- [Milestone Tracking](references/milestone-tracking.md) - Milestones, progress, due dates

## Full Documentation

See [SKILL.md](SKILL.md) for complete usage examples, decision trees, and troubleshooting.
