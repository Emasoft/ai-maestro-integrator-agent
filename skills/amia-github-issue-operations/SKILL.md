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

Programmatic GitHub Issue management (create, label, milestone, assign, comment) via `gh` CLI.

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

See `references/` directory for all reference documents. Start with [detailed-guide](references/detailed-guide.md) for full examples, decision tree, error codes, and troubleshooting.

## Error Handling

Check exit codes on failure: 1=bad args, 2=not found, 3=API error, 4=no auth, 5=idempotent skip. See [detailed-guide](references/detailed-guide.md) for details.

## Resources

All resources are in the `references/` directory.

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
