---
name: amia-git-worktree-operations
description: "Use when processing parallel PRs. Trigger with git worktree or parallel development requests. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
agent: amia-main
tags: "git, worktree, parallel-development, pr-workflow, isolation"
metadata:
  version: 1.0.0
  author: Emasoft
  requires: "git >= 2.15, python >= 3.9"
context: fork
user-invocable: false
---

# Git Worktree Operations Skill

## Overview

Manage git worktrees for parallel PR processing with isolated branch directories sharing a single repository database.

## Prerequisites

- Git 2.15+ installed (`git --version`)
- Python 3.9+ for running scripts
- Sufficient disk space for multiple worktree directories

## Instructions

1. Verify no other git operations are running
2. Fetch and create worktree: `python scripts/amia_create_worktree.py --pr <number> --base-path /tmp/worktrees`
3. Work ONLY within the worktree directory (absolute isolation)
4. Commit and push: `python scripts/amia_worktree_commit_push.py --worktree-path <path> --message "<msg>"`
5. Remove worktree: `python scripts/amia_cleanup_worktree.py --worktree-path <path>`

### Checklist

Copy this checklist and track your progress:

- [ ] Verify git version 2.15+ and no concurrent git ops
- [ ] Create worktree at designated path
- [ ] All file operations strictly inside worktree only
- [ ] Verify isolation: `python scripts/amia_verify_worktree_isolation.py --worktree-path <path>`
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

See `references/` directory for all reference documents.

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See the detailed guide in Resources for common error scenarios.

## Examples

### Process Three PRs in Parallel

```bash
# Create worktrees
python scripts/amia_create_worktree.py --pr 101 --base-path /tmp/worktrees
python scripts/amia_create_worktree.py --pr 102 --base-path /tmp/worktrees
python scripts/amia_create_worktree.py --pr 103 --base-path /tmp/worktrees

# Assign each to a subagent, work in isolation, then cleanup
python scripts/amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-101
```

## Resources

See `references/` directory — 107 reference documents. Full guide: [detailed-guide](references/detailed-guide.md):
  - When to Use Worktrees
  - When NOT to Use Worktrees
  - Critical Constraints
  - Decision Tree
  - Script Usage Examples
  - Error Handling
    - Problem: "fatal: branch is already checked out"
    - Problem: "worktree is dirty, cannot remove"
    - Problem: Files appearing in main repo after worktree work
    - Problem: "fatal: unable to create new worktree"
    - Problem: Git operations hanging or failing
  - Safety Warning: Destructive Operations
    - Before Any Destructive Operation
    - Safe Worktree Removal Checklist
  - Emergency Recovery
  - Quick Reference Card
