# Worktree Cleanup Part 2: Removal Procedures

## Table of Contents

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

---

## 3.3 Safe Removal Procedure Step-by-Step

### Complete Safe Removal Procedure

**Step 1: Navigate away from worktree**
```bash
# NEVER be inside the worktree when removing it
cd /tmp
# Or
cd /path/to/main-repo
```

**Step 2: Verify worktree status**
```bash
git worktree list
# Confirm worktree exists and note its path
```

**Step 3: Check for uncommitted changes**
```bash
cd /tmp/worktrees/pr-123
git status
# Must show "nothing to commit, working tree clean"
cd /tmp  # Navigate away again
```

**Step 4: Verify commits are pushed**
```bash
cd /tmp/worktrees/pr-123
git log origin/pr-123..HEAD
# Should show no commits (all pushed)
cd /tmp  # Navigate away again
```

**Step 5: Remove the worktree**
```bash
cd /path/to/main-repo
git worktree remove /tmp/worktrees/pr-123
```

**Step 6: Verify removal**
```bash
git worktree list
# Should no longer show the removed worktree

ls /tmp/worktrees/pr-123
# Should show "No such file or directory"
```

**Step 7: Optionally delete the branch**
```bash
# Only if branch is no longer needed
git branch -d pr-123  # Safe delete (fails if not merged)
# Or
git branch -D pr-123  # Force delete (use with caution)
```

### One-Liner for Clean Worktrees

If you've already verified the worktree is clean:
```bash
git -C /path/to/main-repo worktree remove /tmp/worktrees/pr-123
```

---

## 3.4 Handling Stuck Worktrees and Lock Files

### Common Stuck Worktree Scenarios

**Scenario 1: Lock file exists**
```
fatal: Unable to create '/path/to/repo/.git/worktrees/pr-123/locked': File exists
```

**Scenario 2: Worktree path doesn't exist**
```
fatal: '/tmp/worktrees/pr-123' does not exist
```

**Scenario 3: Stale worktree entry**
```
Worktree in .git/worktrees but directory missing
```

### Fixing Lock File Issues

**Step 1: Check for lock files**
```bash
ls -la /path/to/main-repo/.git/worktrees/pr-123/
# Look for files named 'locked'
```

**Step 2: Check if lock is legitimate**
```bash
cat /path/to/main-repo/.git/worktrees/pr-123/locked
# Shows reason for lock if intentional
```

**Step 3: Remove stale lock**
```bash
# ONLY if no operations are in progress
rm /path/to/main-repo/.git/worktrees/pr-123/locked
```

**Step 4: Retry removal**
```bash
git worktree remove /tmp/worktrees/pr-123
```

### Fixing Missing Directory Issues

If the worktree directory was deleted manually:

```bash
# Prune will clean up entries for missing directories
git worktree prune

# Verify cleanup
git worktree list
```

### Fixing Corrupted Worktree Metadata

```bash
# Check worktree metadata directory
ls /path/to/main-repo/.git/worktrees/

# If worktree dir missing but metadata exists:
git worktree prune

# If metadata is corrupted, remove manually:
rm -rf /path/to/main-repo/.git/worktrees/pr-123
```

### Locked Worktree (Intentional)

Worktrees can be locked to prevent accidental removal:

```bash
# Check if locked
git worktree lock /tmp/worktrees/pr-123

# Unlock before removal
git worktree unlock /tmp/worktrees/pr-123

# Now remove
git worktree remove /tmp/worktrees/pr-123
```

---

Back to [worktree-cleanup.md](worktree-cleanup.md) | Previous: [worktree-cleanup-part1-timing-verification.md](worktree-cleanup-part1-timing-verification.md) | Next: [worktree-cleanup-part3-force-recovery.md](worktree-cleanup-part3-force-recovery.md)
