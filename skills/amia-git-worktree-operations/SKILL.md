---
name: amia-git-worktree-operations
description: "Use when processing parallel PRs. Trigger with git worktree or parallel development requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  agent: amia-main
  tags: "git, worktree, parallel-development, pr-workflow, isolation"
  requires: "git >= 2.15, python >= 3.9"
context: fork
user-invocable: false
---

# Git Worktree Operations Skill

## Overview

Manage git worktrees for parallel PR processing. Worktrees let you work on multiple branches simultaneously in separate directories while sharing a single repository database.

## Prerequisites

- Git 2.15+ installed (`git --version`)
- Python 3.9+ for running scripts
- Sufficient disk space for multiple worktree directories
- Write access to a directory outside the main repository

## Instructions

1. Verify no other git operations are running
2. Fetch the PR branch: `git fetch origin pull/<PR>/head:<branch>`
3. Create worktree: `python scripts/amia_create_worktree.py --pr <number> --base-path /tmp/worktrees`
4. Work ONLY within the worktree directory (absolute isolation)
5. Commit and push: `python scripts/amia_worktree_commit_push.py --worktree-path <path> --message "<msg>"`
6. Verify all changes pushed before cleanup
7. Remove worktree: `python scripts/amia_cleanup_worktree.py --worktree-path <path>`

### Checklist

Copy this checklist and track your progress:

- [ ] Verify git version 2.15+ and no concurrent git ops
- [ ] Fetch PR branch from remote
- [ ] Create worktree at designated path
- [ ] All file operations strictly inside worktree only
- [ ] Periodically verify isolation: `python scripts/amia_verify_worktree_isolation.py --worktree-path <path>`
- [ ] Commit and push changes
- [ ] Verify no uncommitted files remain
- [ ] Cleanup worktree after PR completion

## Output

| Output Type | Description |
|-------------|-------------|
| Worktree Directory | Checked-out PR branch at specified path |
| Worktree List | JSON listing active worktrees with paths and branches |
| Verification Report | Isolation check status and any boundary violations |
| Commit/Push Confirmation | Success/failure with commit hash or remote status |
| Cleanup Report | Removal confirmation with warnings if uncommitted changes exist |

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

**Core:**

- `references/worktree-fundamentals.md` — Worktree concepts, shared git model, prerequisites
- `references/detailed-guide.md` — Constraints, decision tree, error handling, safety

**Workflows:**

- `references/parallel-pr-workflow.md` — Parallel PR processing (parts 1-4 in same folder)
- `references/quick-start-workflows.md` — Common workflow shortcuts

**Operations:**

- `references/creating-worktrees.md` — Creation procedures (parts 1-6 in same folder)
- `references/worktree-operations.md` — Listing, switching, locking, syncing
- `references/worktree-cleanup.md` — Safe removal, pruning, disk recovery
- `references/worktree-verification.md` — Isolation checks, boundary detection
- `references/removing-worktrees.md` — Removal and post-removal

**Scripts and Testing:**

- `references/scripts-guide.md` — All script usage and workflows
- `references/testing-worktree-isolation.md` — Test types, CI/CD, database testing
- `references/docker-worktree-testing.md` — Docker setup and best practices

**Infrastructure:**

- `references/port-allocation.md` — Port allocation for worktree services
- `references/port-management.md` — Port registry and conflict resolution
- `references/registry-system.md` — Registry schema and validation

**Other:**

- `references/quick-reference.md` — Quick command reference
- `references/troubleshooting.md` — Common issues and solutions
- `references/cross-platform-support.md` — Platform-specific notes
- `references/merge-safeguards.md` — Merge validation
- `references/worktree-naming-conventions.md` — Naming standards



## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

### Example 1: Process Three PRs in Parallel

```bash
# Create worktrees
python scripts/amia_create_worktree.py --pr 101 --base-path /tmp/worktrees
python scripts/amia_create_worktree.py --pr 102 --base-path /tmp/worktrees
python scripts/amia_create_worktree.py --pr 103 --base-path /tmp/worktrees

# Assign each to a subagent, work in isolation, then cleanup
python scripts/amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-101
```
## Resources

- `references/creating-worktrees-part1-standard-flow.md`
- `references/creating-worktrees-part2-purpose-patterns.md`
- `references/creating-worktrees-part3-port-allocation.md`
- `references/creating-worktrees-part4-environment-setup.md`
- `references/creating-worktrees-part5-commands-checklist.md`
- ...and 102 more in `references/`
