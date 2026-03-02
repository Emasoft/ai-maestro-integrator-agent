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
workflow-instruction: "support"
procedure: "support-skill"
user-invocable: false
---

# Git Worktree Operations Skill

## Overview

This skill teaches you how to use git worktrees for parallel PR processing. Git worktrees allow you to work on multiple branches simultaneously in separate directories while sharing a single git repository database.

## Prerequisites

Before using this skill, ensure:
1. Git version 2.15 or higher is installed (`git --version`)
2. Python 3.9 or higher is available for running scripts
3. Sufficient disk space for multiple worktree directories
4. Write access to a directory outside the main repository for worktree paths

## Instructions

### When to Use This Skill

Use git worktrees when you need to:

1. **Work on multiple PRs concurrently** without switching branches
2. **Maintain complete isolation** between different changes
3. **Delegate PR tasks to subagents** where each operates in its own directory
4. **Review PRs locally** while continuing development on another branch
5. **Run long-running tests** on one branch while developing on another

### When NOT to Use This Skill

Do NOT use worktrees when:

1. You only work on one branch at a time
2. The repository is very large and disk space is limited
3. You need to share uncommitted changes between "checkouts"
4. You are working with submodules (additional complexity)

### Checklist

Copy this checklist and track your progress:

- [ ] Verify git version is 2.15+ (`git --version`)
- [ ] Check no other git operations are currently running
- [ ] Fetch PR branch from remote: `git fetch origin pull/<PR>/head:<branch>`
- [ ] Create worktree: `python scripts/amia_create_worktree.py --pr <number> --base-path /tmp/worktrees`
- [ ] Verify worktree creation succeeded
- [ ] Work ONLY within the worktree directory (no file ops outside)
- [ ] Periodically verify isolation: `python scripts/amia_verify_worktree_isolation.py --worktree-path <path>`
- [ ] Commit changes within worktree
- [ ] Push to remote: `python scripts/amia_worktree_commit_push.py --worktree-path <path> --message "<msg>"`
- [ ] Verify all changes are pushed before cleanup
- [ ] Verify no uncommitted files remain
- [ ] Cleanup worktree: `python scripts/amia_cleanup_worktree.py --worktree-path <path>`

---

## CRITICAL Constraints for Worktree Usage

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

---

## Decision Tree for Worktree Operations

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

---

## Reference Documents

### 1. Worktree Fundamentals

For understanding what worktrees are and how they work, see [worktree-fundamentals.md](references/worktree-fundamentals.md):

**Contents:**
- 1.1 What is a git worktree and why it exists
- 1.2 Worktree vs clone vs checkout - choosing the right approach
- 1.3 The shared git directory model explained
- 1.4 When worktrees provide measurable benefits
- 1.5 Common misconceptions about worktrees
- 1.6 Prerequisites and git version requirements

### 2. Parallel PR Workflow

For implementing parallel PR processing with worktrees, see [parallel-pr-workflow.md](references/parallel-pr-workflow.md):

**Contents:**
- 2.1 Creating Worktrees for Multiple Simultaneous PRs
- 2.2 Isolation Requirements and Enforcement Rules
- 2.3 Working Directory Management for Subagents
- 2.4 Path Validation Rules and Common Violations
- 2.5 Handling Concurrent Git Operation Limitations
- 2.6 Example Workflow: Processing 3 PRs in Parallel
- 2.7 Error Recovery When Isolation is Violated

### 3. Worktree Cleanup

For safely removing worktrees after PR completion, see [worktree-cleanup.md](references/worktree-cleanup.md):

**Contents:**
- 3.1 When to clean up worktrees (timing and triggers)
- 3.2 Verifying no uncommitted changes exist
- 3.3 Safe removal procedure step-by-step
- 3.4 Handling stuck worktrees and lock files
- 3.5 Force removal scenarios and their risks
- 3.6 Pruning stale worktree entries
- 3.7 Disk space recovery after cleanup

### 4. Worktree Verification

For verifying worktree integrity and isolation, see [worktree-verification.md](references/worktree-verification.md):

**Contents:**
- 4.1 Pre-cleanup verification checklist
- 4.2 Detecting files written outside worktree boundaries
- 4.3 Branch state verification procedures
- 4.4 Remote sync verification steps
- 4.5 Automated verification script usage
- 4.6 Manual verification when scripts fail
- 4.7 Reporting isolation violations

---

## Scripts Reference

This skill includes Python scripts for common worktree operations:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `amia_create_worktree.py` | Create worktree for a PR | Starting work on a new PR |
| `amia_list_worktrees.py` | List all active worktrees | Before creating new worktree, status check |
| `amia_cleanup_worktree.py` | Safely remove a worktree | After PR is merged/closed |
| `amia_verify_worktree_isolation.py` | Check for isolation violations | Before committing, periodically |
| `amia_worktree_commit_push.py` | Commit and push changes | Ready to update remote |

### Script Usage Examples

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

---

## Examples

### Example 1: Create Worktree for a Single PR

```bash
# Create worktree for PR #123
python scripts/amia_create_worktree.py --pr 123 --base-path /tmp/worktrees

# Navigate to worktree and work
cd /tmp/worktrees/pr-123
# Make changes, commit, push

# Clean up when done
python scripts/amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-123
```

### Example 2: Process Three PRs in Parallel

```bash
# Create worktrees for each PR
python scripts/amia_create_worktree.py --pr 101 --base-path /tmp/worktrees
python scripts/amia_create_worktree.py --pr 102 --base-path /tmp/worktrees
python scripts/amia_create_worktree.py --pr 103 --base-path /tmp/worktrees

# Assign each worktree to a different subagent
# Each agent works in isolation in its own directory

# Verify isolation periodically
python scripts/amia_verify_worktree_isolation.py --worktree-path /tmp/worktrees/pr-101
```

---

## Output

| Output Type | Description |
|-------------|-------------|
| **Worktree Directory** | New directory created at specified path containing checked-out PR branch |
| **Worktree List** | JSON or text output listing all active worktrees with paths and branch names |
| **Verification Report** | Status of isolation checks showing any files written outside worktree boundaries |
| **Commit Confirmation** | Success/failure message with commit hash after committing changes |
| **Push Confirmation** | Success/failure message indicating remote branch update status |
| **Cleanup Report** | Confirmation of worktree removal with any warnings about uncommitted changes |
| **Error Messages** | Diagnostic output when operations fail (branch conflicts, lock files, etc.) |
| **Isolation Violations** | List of files that were written outside the designated worktree path |

---

## Error Handling

### Problem: "fatal: branch is already checked out"

**Cause:** Attempting to checkout a branch that exists in another worktree.

**Solution:** See [worktree-fundamentals.md](references/worktree-fundamentals.md) section 1.5 for branch constraint details.
- **Contents:** What is a git worktree and why it exists, Worktree vs clone vs checkout - choosing the right approach, The shared git directory model explained, When worktrees provide measurable benefits, Common misconceptions about worktrees, Prerequisites and git version requirements

### Problem: "worktree is dirty, cannot remove"

**Cause:** Attempting to remove a worktree with uncommitted changes.

**Solution:** See [worktree-cleanup.md](references/worktree-cleanup.md) section 3.2 for handling uncommitted changes.
- **Contents:** When to clean up worktrees (timing and triggers), Verifying no uncommitted changes exist, Safe removal procedure step-by-step, Handling stuck worktrees and lock files, Force removal scenarios and their risks, Pruning stale worktree entries, Disk space recovery after cleanup

### Problem: Files appearing in main repo after worktree work

**Cause:** Isolation violation - files were written outside the worktree.

**Solution:** See [worktree-verification.md](references/worktree-verification.md) section 4.2 for detection and remediation.
- **Contents:** Pre-cleanup verification checklist, Detecting files written outside worktree boundaries, Branch state verification procedures, Remote sync verification steps, Automated verification script usage, Manual verification when scripts fail, Reporting isolation violations

### Problem: "fatal: unable to create new worktree"

**Cause:** Lock file exists or path already in use.

**Solution:** See [worktree-cleanup.md](references/worktree-cleanup.md) section 3.4 for handling stuck worktrees.
- **Contents:** When to clean up worktrees (timing and triggers), Verifying no uncommitted changes exist, Safe removal procedure step-by-step, Handling stuck worktrees and lock files, Force removal scenarios and their risks, Pruning stale worktree entries, Disk space recovery after cleanup

### Problem: Git operations hanging or failing

**Cause:** Concurrent git operations in multiple worktrees.

**Solution:** See [parallel-pr-workflow.md](references/parallel-pr-workflow.md) section 2.5 for serialization strategies.

**Contents:** Part 1: Creating Worktrees and Isolation, 2.5 Handling Concurrent Git Operation Limitations, Problematic concurrent operations (commit, fetch, push conflicts), Safe concurrent operations (status, diff, log, file mods)

---

## Resources

- [references/worktree-fundamentals.md](references/worktree-fundamentals.md) - What worktrees are and how they work
  - **Contents:** What is a git worktree and why it exists, Worktree vs clone vs checkout - choosing the right approach, The shared git directory model explained, When worktrees provide measurable benefits, Common misconceptions about worktrees, Prerequisites and git version requirements
- [references/parallel-pr-workflow.md](references/parallel-pr-workflow.md) - Processing multiple PRs simultaneously
  - **Contents:**
    - Creating Worktrees for Multiple Simultaneous PRs
    - Isolation Requirements and Enforcement Rules
    - Handling Concurrent Git Operation Limitations
    - Example Workflow: Processing 3 PRs in Parallel
- [references/worktree-cleanup.md](references/worktree-cleanup.md) - Safe worktree removal procedures
  - **Contents:** When to clean up worktrees (timing and triggers), Verifying no uncommitted changes exist, Safe removal procedure step-by-step, Handling stuck worktrees and lock files, Force removal scenarios and their risks, Pruning stale worktree entries, Disk space recovery after cleanup
- [references/worktree-verification.md](references/worktree-verification.md) - Isolation and integrity checks
  - **Contents:** Pre-cleanup verification checklist, Detecting files written outside worktree boundaries, Branch state verification procedures, Remote sync verification steps, Automated verification script usage, Manual verification when scripts fail, Reporting isolation violations

---

## SAFETY WARNING: Destructive Operations

### IRREVERSIBLE Operations

The following git worktree operations are **IRREVERSIBLE** and can cause data loss:

| Operation | Risk | Alternative |
|-----------|------|-------------|
| `git worktree remove --force` | Deletes worktree even with uncommitted changes | Use `git worktree remove` (no --force) first |
| `rm -rf <worktree-path>` | Bypasses git's safety checks, corrupts worktree list | Always use `git worktree remove` |
| `git worktree prune` | Removes stale worktree entries | Verify with `git worktree list` first |

### BEFORE ANY DESTRUCTIVE OPERATION

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

### Emergency Recovery

If worktree was removed with uncommitted changes:

```bash
# Check git reflog for recent commits
git reflog

# Recover lost commits
git cherry-pick <commit-hash>

# Check for dangling commits
git fsck --lost-found
```

---

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
