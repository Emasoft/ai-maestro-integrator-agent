---
name: amia-github-issue-operations
description: Use when managing GitHub Issues including creation, labels, milestones, assignees, and comments using gh CLI. Trigger with create issue, set labels, assign milestone.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: "1.0.0"
  author: Emasoft
  category: github
  tags: "github, issues, labels, milestones, project-management"
  requires_tools: "gh, jq"
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Issue Operations Skill

## Overview

Complete GitHub Issue management for orchestrator agents. Enables programmatic issue creation, labeling, milestone tracking, assignee management, and comment posting via `gh` CLI.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Write access to target repository
- `jq` available for JSON processing

## Instructions

1. Verify prerequisites: `gh --version` and `gh auth status`
2. Select the script for your operation (see Script Table below)
3. Execute with required arguments (all scripts need `--repo owner/repo`)
4. Check JSON output for `"error": false` (success) or `"error": true` (failure)
5. Use `--output-file <path>` in automated workflows to minimize token usage

### Script Table

| Script | Purpose | Key Args |
|--------|---------|----------|
| `amia_get_issue_context.py` | Get issue metadata | `--issue N` |
| `amia_create_issue.py` | Create new issue | `--title "..."` |
| `amia_set_issue_labels.py` | Add/remove/set labels | `--add`, `--remove`, `--set` |
| `amia_set_issue_milestone.py` | Assign milestone | `--milestone "..."` |
| `amia_post_issue_comment.py` | Post comment | `--body "..."`, `--marker` |

### Checklist

Copy this checklist and track your progress:

- [ ] gh CLI installed and authenticated
- [ ] Write access to target repository verified
- [ ] Correct script selected for operation
- [ ] Required arguments provided (all need `--repo`)
- [ ] JSON output checked for success/error
- [ ] Exit code handled (0=ok, 1=bad args, 2=not found, 3=API, 4=no auth, 5=idempotent skip)

## Output

| Type | Format | Key Fields |
|------|--------|------------|
| Success | JSON | Operation-specific (`number`, `url`, `labels`, etc.) |
| Error | JSON | `error: true`, `message`, `code` |

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

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
- `references/detailed-guide.md` — Full examples, decision tree, error codes, troubleshooting

**Template Parts:**

- `references/issue-templates-part1-bug-reports.md` — Bug report templates
- `references/issue-templates-part2-feature-requests.md` — Feature request templates
- `references/issue-templates-part3-tasks.md` — Task templates
- `references/issue-templates-part4-programmatic.md` — Programmatic template usage
- `references/milestone-tracking-part1-creating.md` — Creating milestones
- `references/milestone-tracking-part2-assigning.md` — Assigning issues to milestones
- `references/milestone-tracking-part3-progress-closing.md` — Progress tracking and closing



## Error Handling

If a script fails, check the exit code and stderr output. Common issues:

- **Exit 1**: Invalid parameters or missing arguments
- **Exit 2-4**: GitHub API errors (auth, not found, rate limit)

See `references/detailed-guide.md` for detailed error scenarios.

## Resources

- `references/detailed-guide.md`
- `references/issue-templates-part1-bug-reports.md`
- `references/issue-templates-part2-feature-requests.md`
- `references/issue-templates-part3-tasks.md`
- `references/issue-templates-part4-programmatic.md`
- `references/issue-templates.md`
- `references/label-management.md`
- `references/milestone-tracking-part1-creating.md`
- ...and 8 more in `references/`

## Examples

### Create issue with labels

```bash
./scripts/amia_create_issue.py \
  --repo owner/repo \
  --title "Implement feature X" \
  --labels "feature,P2" \
  --assignee "dev1"
# Returns: {"number": 124, "url": "https://github.com/owner/repo/issues/124"}
```
