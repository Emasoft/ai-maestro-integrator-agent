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

Entry point for all GitHub integration tasks. Routes to specialized skills based on task type (PRs, Projects V2, Kanban, worktrees, API ops, multi-user). Also handles batch operations spanning multiple areas.

## Prerequisites

- GitHub CLI 2.14+ installed (`gh --version`)
- GitHub CLI authenticated (`gh auth status`)
- Write permissions on target repository
- For setup details, see `references/prerequisites-and-setup.md`

## Instructions

1. Verify GitHub CLI: `gh --version` (must be 2.14+).
2. Confirm auth: `gh auth status`. If not authenticated, run `gh auth login`.
3. Identify task type using the routing table below:
   - **Pull Requests** --> use skill `amia-github-pr-workflow`
   - **Projects V2 sync** --> use skill `amia-github-projects-sync`
   - **Kanban board ops** --> use skill `amia-kanban-orchestration`
   - **Git worktrees** --> use skill `amia-git-worktree-operations`
   - **Direct API ops** --> see `references/api-operations.md`
   - **Multi-user identities** --> see `references/multi-user-workflow.md`
4. For cross-area batch operations (bulk labels, bulk close), use `references/batch-operations.md`.
5. Always preview before batch changes: `gh issue list --label X --state open`.
6. Execute the operation, then verify: `gh issue view <N>` or `gh pr status`.
7. On errors, consult the error table in `references/detailed-guide.md` or `references/troubleshooting.md`.

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

**Setup and Auth:**

- `references/prerequisites-and-setup.md` -- GitHub CLI installation and authentication
- `references/multi-user-workflow.md` -- Managing multiple GitHub identities
- `references/single-account-workflow.md` -- Single account setup

**Operations:**

- `references/api-operations.md` -- REST/GraphQL API operations, rate limits, quality gates
- `references/batch-operations.md` -- Bulk filtering, label ops, batch updates
- `references/automation-scripts.md` -- Python scripts for sync, bulk labels, monitoring, reports
- `references/projects-v2-operations.md` -- Projects V2 specific operations
- `references/pull-request-management.md` -- PR management details
- `references/issue-management.md` -- Issue lifecycle management

**Guides and Troubleshooting:**

- `references/detailed-guide.md` -- Decision tree, error handling, extended examples
- `references/troubleshooting.md` -- Common issues and solutions
- `references/core-concepts.md` -- Core concepts overview
- `references/implementation-guide.md` -- Full implementation guide

**Templates:**

- `references/template-bug-report.md` -- Bug report template
- `references/template-pull-request.md` -- PR template
- `references/template-docs-issue.md` -- Documentation issue template

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

### Example: Bulk add label to open bug issues

```bash
# Preview affected issues
gh issue list --label "bug" --state open --json number,title \
  --jq '.[] | "\(.number): \(.title)"'

# Apply label
gh issue list --label "bug" --state open --json number \
  --jq '.[].number' | xargs -I {} gh issue edit {} --add-label "priority:critical"

# Verify
gh issue view 15 --json labels --jq '.labels[].name'
```

---

**Skill Version:** 2.0.0 | **Last Updated:** 2026-02-05

## Resources

- `references/account-strategy-decision-guide.md`
- `references/api-operations.md`
- `references/automation-scripts.md`
- `references/batch-operations.md`
- `references/core-concepts.md`
- ...and 35 more in `references/`
