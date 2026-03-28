---
name: amia-github-integration
description: "Use when integrating GitHub Projects. Trigger with GitHub sync, label setup, or PR workflow requests."
license: Apache-2.0
compatibility: Requires GitHub CLI version 2.14 or higher, GitHub account with write permissions to target repositories, and basic Git knowledge. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Integration Dispatcher

## Overview

Routes GitHub integration tasks to specialized skills (PRs, Projects V2, Kanban, worktrees, API, multi-user, batch).

## Prerequisites

- GitHub CLI 2.14+ authenticated (`gh auth status`)
- Write permissions on target repository
- Setup details: `references/prerequisites-and-setup.md`

## Instructions

1. Confirm auth: `gh auth status` (CLI 2.14+ required).
2. Route by task type:
   - **PRs** --> `amia-github-pr-workflow`
   - **Projects V2** --> `amia-github-projects-sync`
   - **Kanban** --> `amia-kanban-orchestration`
   - **Worktrees** --> `amia-git-worktree-operations`
   - **API ops** --> `references/api-operations.md`
   - **Multi-user** --> `references/multi-user-workflow.md`
3. Batch ops: preview first (`gh issue list --repo "$OWNER/$REPO" --label X --state open`), then execute.
4. Verify result: `gh issue view <N> --repo "$OWNER/$REPO"` or `gh pr status --repo "$OWNER/$REPO"`.
5. On errors: see `references/detailed-guide.md`.

### Checklist

Copy this checklist and track your progress:

- [ ] GitHub CLI 2.14+ installed
- [ ] `gh auth status` confirms authentication
- [ ] Task type identified (PR / Projects V2 / Kanban / Worktree / API / Multi-User / Batch)
- [ ] Routed to correct specialized skill or reference
- [ ] Batch ops: dry-run preview completed before execution
- [ ] Operation executed and result verified

## Output

| Operation | Output |
|-----------|--------|
| Routing | Name of specialized skill to invoke |
| Batch ops | Summary of affected items and changes applied |
| Automation scripts | JSON/Markdown reports via `--output-file` |
| Verification | `gh` CLI confirmation of current state |

> **Output discipline:** All scripts support `--output-file <path>`. Use it in automated workflows to minimize token consumption.

## Reference Documents

See `references/` directory for all reference documents. Index in `references/detailed-guide.md`.

## Error Handling

Non-zero exit codes on failure; check stderr and `references/detailed-guide.md`.

## Examples

### Example: Bulk add label to open bug issues

```bash
# All gh commands MUST specify --repo since the integrator works across multiple repos
# Preview affected issues
gh issue list --repo "$OWNER/$REPO" --label "bug" --state open --json number,title \
  --jq '.[] | "\(.number): \(.title)"'

# Apply label
gh issue list --repo "$OWNER/$REPO" --label "bug" --state open --json number \
  --jq '.[].number' | xargs -I {} gh issue edit {} --repo "$OWNER/$REPO" --add-label "priority:critical"

# Verify
gh issue view 15 --repo "$OWNER/$REPO" --json labels --jq '.labels[].name'
```

---

**Skill Version:** 2.0.0 | **Last Updated:** 2026-02-05

## Resources

See `references/` directory (40+ documents).
