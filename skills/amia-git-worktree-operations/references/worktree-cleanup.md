# Worktree Cleanup

## Table of Contents

- 3.1 When to clean up worktrees (timing and triggers)
- 3.2 Verifying no uncommitted changes exist
- 3.3 Safe removal procedure step-by-step
- 3.4 Handling stuck worktrees and lock files
- 3.5 Force removal scenarios and their risks
- 3.6 Pruning stale worktree entries
- 3.7 Disk space recovery after cleanup

---

## Overview

This document covers the complete worktree cleanup process. Content is split into three parts for easier reference:

---

## Part 1: Timing and Verification

**File:** [worktree-cleanup-part1-timing-verification.md](worktree-cleanup-part1-timing-verification.md)

**Contents:**
- 3.1 When to Clean Up Worktrees (Timing and Triggers)
  - 3.1.1 Cleanup triggers (PR merged, closed, abandoned, branch deleted)
  - 3.1.2 Timing considerations (immediate, soon, delay)
  - 3.1.3 Pre-cleanup checklist
- 3.2 Verifying No Uncommitted Changes Exist
  - 3.2.1 Quick status check with `git status --porcelain`
  - 3.2.2 Status code meanings (??, M, A, D)
  - 3.2.3 Comprehensive change detection script
  - 3.2.4 What to do with uncommitted changes (commit, discard, stash, patch)

**Use this part when:** You need to determine IF a worktree should be cleaned up and verify it's safe to remove.

---

## Part 2: Removal Procedures

**File:** [worktree-cleanup-part2-removal-procedures.md](worktree-cleanup-part2-removal-procedures.md)

**Contents:**
- 3.3 Safe Removal Procedure Step-by-Step
  - 3.3.1 Step 1: Navigate away from worktree
  - 3.3.2 Step 2: Verify worktree status
  - 3.3.3 Step 3: Check for uncommitted changes
  - 3.3.4 Step 4: Verify commits are pushed
  - 3.3.5 Step 5: Remove the worktree
  - 3.3.6 Step 6: Verify removal
  - 3.3.7 Step 7: Optionally delete the branch
  - 3.3.8 One-liner for clean worktrees
- 3.4 Handling Stuck Worktrees and Lock Files
  - 3.4.1 Common stuck worktree scenarios
  - 3.4.2 Fixing lock file issues
  - 3.4.3 Fixing missing directory issues
  - 3.4.4 Fixing corrupted worktree metadata
  - 3.4.5 Handling intentionally locked worktrees

**Use this part when:** You're ready to remove a worktree or encountering issues during removal.

---

## Part 3: Force Removal and Recovery

**File:** [worktree-cleanup-part3-force-recovery.md](worktree-cleanup-part3-force-recovery.md)

**Contents:**
- 3.5 Force Removal Scenarios and Their Risks
  - 3.5.1 When force removal is needed
  - 3.5.2 Force removal command
  - 3.5.3 Risks of force removal
  - 3.5.4 Safe force removal procedure
  - 3.5.5 Double-force removal for stubborn worktrees
- 3.6 Pruning Stale Worktree Entries
  - 3.6.1 What is pruning
  - 3.6.2 When pruning is needed
  - 3.6.3 Dry run and execute pruning
  - 3.6.4 Verifying prune results
- 3.7 Disk Space Recovery After Cleanup
  - 3.7.1 Understanding worktree disk usage
  - 3.7.2 Estimating space recovery
  - 3.7.3 Running garbage collection
  - 3.7.4 Aggressive cleanup
  - 3.7.5 Monitoring disk usage
  - 3.7.6 Cleanup script

**Use this part when:** Normal removal fails or you need to recover disk space after cleanup.

---

## Quick Reference

### Safe Removal Command
```bash
git worktree remove /tmp/worktrees/pr-123
```

### Force Removal Command
```bash
git worktree remove --force /tmp/worktrees/pr-123
```

### Prune Stale Entries
```bash
git worktree prune
```

### Full Cleanup Sequence
```bash
cd /path/to/main-repo
git worktree remove /tmp/worktrees/pr-123
git worktree prune
git gc --prune=now
```

---

## Summary

Safe worktree cleanup requires:

1. **Timing:** Clean up when PR is merged/closed
2. **Verification:** Ensure no uncommitted changes
3. **Procedure:** Use `git worktree remove` command
4. **Recovery:** Handle stuck worktrees with locks/prune
5. **Space:** Run gc for full disk space recovery

Continue to [worktree-verification.md](worktree-verification.md) for verification procedures before cleanup.
