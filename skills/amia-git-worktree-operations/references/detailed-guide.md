# Git Worktree Operations — Detailed Guide

## Contents

- [When to Use Worktrees](#when-to-use-worktrees)
- [When NOT to Use Worktrees](#when-not-to-use-worktrees)
- [Critical Constraints](#critical-constraints)
- [Decision Tree](#decision-tree)
- [Script Usage Examples](#script-usage-examples)
- [Error Handling](#error-handling)
- [Safety Warning: Destructive Operations](#safety-warning-destructive-operations)
- [Emergency Recovery](#emergency-recovery)
- [Quick Reference Card](#quick-reference-card)

## When to Use Worktrees

Use git worktrees when you need to:

1. **Work on multiple PRs concurrently** without switching branches
2. **Maintain complete isolation** between different changes
3. **Delegate PR tasks to subagents** where each operates in its own directory
4. **Review PRs locally** while continuing development on another branch
5. **Run long-running tests** on one branch while developing on another

## When NOT to Use Worktrees

Do NOT use worktrees when:

1. You only work on one branch at a time
2. The repository is very large and disk space is limited
3. You need to share uncommitted changes between "checkouts"
4. You are working with submodules (additional complexity)

## Critical Constraints

**CONSTRAINT 1: ABSOLUTE ISOLATION**
Every file write, edit, or creation MUST happen within the assigned worktree directory. Writing files outside your worktree corrupts the isolation model and causes merge conflicts.

**CONSTRAINT 2: NO CONCURRENT GIT OPERATIONS**
Never run git operations (commit, push, fetch, rebase) in multiple worktrees simultaneously. Git's lock mechanisms can deadlock or corrupt the shared repository database.

**CONSTRAINT 3: VERIFY BEFORE CLEANUP**
Before removing a worktree, ALWAYS verify:

- All changes are committed
- All commits are pushed to remote
- No files were accidentally written outside the worktree

**CONSTRAINT 4: ONE BRANCH PER WORKTREE**
A branch can only be checked out in ONE worktree at a time. Attempting to checkout a branch that exists in another worktree will fail.

**CONSTRAINT 5: WORKTREE PATH RULES**

- Worktree paths must be outside the main repository
- Use absolute paths when creating worktrees
- Never nest worktrees inside each other

## Decision Tree

```
START: Need to work on a PR?
│
├─► Is this PR already in a worktree?
│   ├─► YES: Navigate to existing worktree
│   └─► NO: Continue below
│
├─► Is another git operation running?
│   ├─► YES: WAIT until it completes
│   └─► NO: Continue below
│
├─► Create new worktree for PR
│   ├─► Fetch PR branch from remote
│   ├─► Create worktree at designated path
│   └─► Verify worktree creation succeeded
│
├─► Work ONLY within worktree directory
│   ├─► All file operations inside worktree
│   ├─► All script executions from worktree
│   └─► Verify isolation periodically
│
├─► Ready to commit/push?
│   ├─► Verify no other git ops running
│   ├─► Commit changes in worktree
│   └─► Push to remote
│
└─► PR merged/completed?
    ├─► Verify all changes pushed
    ├─► Verify no uncommitted files
    └─► Remove worktree safely
```

## Script Usage Examples

**Creating a worktree for PR #123:**

```bash
python scripts/amia_create_worktree.py --pr 123 --base-path /tmp/worktrees
```

**Listing all worktrees:**

```bash
python scripts/amia_list_worktrees.py --repo-path /path/to/main/repo
```

**Verifying isolation:**

```bash
python scripts/amia_verify_worktree_isolation.py --worktree-path /tmp/worktrees/pr-123
```

**Committing and pushing:**

```bash
python scripts/amia_worktree_commit_push.py --worktree-path /tmp/worktrees/pr-123 --message "Fix issue"
```

**Cleaning up a worktree:**

```bash
python scripts/amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-123
```

## Error Handling

### Problem: "fatal: branch is already checked out"

**Cause:** Attempting to checkout a branch that exists in another worktree.
**Solution:** See `references/worktree-fundamentals.md` section 1.5 for branch constraint details.

### Problem: "worktree is dirty, cannot remove"

**Cause:** Attempting to remove a worktree with uncommitted changes.
**Solution:** See `references/worktree-cleanup.md` section 3.2 for handling uncommitted changes.

### Problem: Files appearing in main repo after worktree work

**Cause:** Isolation violation - files were written outside the worktree.
**Solution:** See `references/worktree-verification.md` section 4.2 for detection and remediation.

### Problem: "fatal: unable to create new worktree"

**Cause:** Lock file exists or path already in use.
**Solution:** See `references/worktree-cleanup.md` section 3.4 for handling stuck worktrees.

### Problem: Git operations hanging or failing

**Cause:** Concurrent git operations in multiple worktrees.
**Solution:** See `references/parallel-pr-workflow.md` section 2.5 for serialization strategies.

## Safety Warning: Destructive Operations

The following git worktree operations are **IRREVERSIBLE** and can cause data loss:

| Operation | Risk | Alternative |
|-----------|------|-------------|
| `git worktree remove --force` | Deletes worktree even with uncommitted changes | Use `git worktree remove` (no --force) first |
| `rm -rf <worktree-path>` | Bypasses git's safety checks, corrupts worktree list | Always use `git worktree remove` |
| `git worktree prune` | Removes stale worktree entries | Verify with `git worktree list` first |

### Before Any Destructive Operation

1. **Verify you have a backup branch**

   ```bash
   git branch -a | grep backup
   # If no backup, create one:
   git branch backup-$(date +%Y%m%d) HEAD
   ```

2. **Confirm with orchestrator** before force operations
   - Never use `--force` flags without explicit approval
   - Document the reason for force operation

3. **Log the operation details**

   ```bash
   echo "$(date): Removing worktree $WORKTREE_PATH - Reason: [REASON]" >> worktree-ops.log
   ```

### Safe Worktree Removal Checklist

- [ ] Run `git status` in worktree to check for uncommitted changes
- [ ] Run `git log origin/branch..HEAD` to check for unpushed commits
- [ ] Verify no other processes are using the worktree
- [ ] Use `git worktree remove <path>` (without --force)
- [ ] If removal fails, investigate why before using --force
- [ ] After removal, verify with `git worktree list`

## Emergency Recovery

If worktree was removed with uncommitted changes:

```bash
# Check git reflog for recent commits
git reflog

# Recover lost commits
git cherry-pick <commit-hash>

# Check for dangling commits
git fsck --lost-found
```

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GIT WORKTREE QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────────┤
│ CREATE:   git worktree add <path> <branch>                          │
│ LIST:     git worktree list                                         │
│ REMOVE:   git worktree remove <path>                                │
│ PRUNE:    git worktree prune                                        │
├─────────────────────────────────────────────────────────────────────┤
│ CRITICAL RULES:                                                      │
│ 1. ONE branch per worktree (enforced by git)                        │
│ 2. ALL file ops inside worktree only                                │
│ 3. NO concurrent git ops across worktrees                           │
│ 4. VERIFY before cleanup                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Content Moved from SKILL.md

### Original Reference Documents Section

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

### Original Resources Section

- `references/creating-worktrees-part1-standard-flow.md`
- `references/creating-worktrees-part2-purpose-patterns.md`
- `references/creating-worktrees-part3-port-allocation.md`
- `references/creating-worktrees-part4-environment-setup.md`
- `references/creating-worktrees-part5-commands-checklist.md`
- ...and 102 more in `references/`

### Original Prerequisites (removed items)

- Write access to a directory outside the main repository
