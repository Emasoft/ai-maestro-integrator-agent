# Removing Worktrees - Part 1: Preparation and Basic Commands

## Table of Contents
1. [When you need to understand worktree removal → Overview](#overview)
2. [Before removing any worktree → Pre-Removal Checklist](#pre-removal-checklist)
   - 2.1 [Check for Uncommitted Work](#step-1-check-for-uncommitted-work)
   - 2.2 [Check Pull Request Status](#step-2-check-pull-request-status)
   - 2.3 [Check for Running Processes](#step-3-check-for-running-processes)
   - 2.4 [Check Registry Entry](#step-4-check-registry-entry)
   - 2.5 [Complete Checklist Template](#complete-checklist-template)
3. [When you need to delete a worktree → Removal Commands](#removal-commands)
   - 3.1 [Basic Removal (Standard)](#basic-removal-standard)
   - 3.2 [Force Removal](#force-removal)
   - 3.3 [Pruning Stale Entries](#pruning-stale-entries)
   - 3.4 [Dry Run (Preview Only)](#dry-run-preview-only)
4. [When removal fails → Handling Removal Failures](#handling-removal-failures)
   - 4.1 [Error: contains modified or untracked files](#error-contains-modified-or-untracked-files)
   - 4.2 [Error: is not a working tree](#error-is-not-a-working-tree)
   - 4.3 [Error: locked](#error-locked)
   - 4.4 [Error: Permission denied](#error-permission-denied)

**Related Parts:**
- [Part 2: Post-Removal and Automation](removing-worktrees-part2-post-removal.md)
- [Part 3: Advanced Operations](removing-worktrees-part3-advanced.md)
- [Index: All Removal Topics](removing-worktrees-index.md)

---

## Overview

**What is Worktree Removal?**
Worktree removal is the process of deleting a git worktree directory and its associated git metadata. A worktree is a separate working directory that shares the same git repository but can have a different branch checked out.

**When to Remove a Worktree:**
- Pull request has been merged or closed
- Review or testing is complete
- Feature branch work is finished
- Worktree is no longer needed
- Freeing up disk space

**Why Follow This Process:**
- Prevents data loss from uncommitted work
- Releases system resources (ports, processes)
- Maintains registry integrity
- Ensures clean git state
- Avoids orphaned directories

---

## Pre-Removal Checklist

**CRITICAL:** Complete ALL checklist items before removing a worktree. Skipping steps can cause data loss.

### Step 1: Check for Uncommitted Work

**What is uncommitted work?**
Uncommitted work is any code changes you made but haven't saved to git history with `git commit`.

**How to check:**
```bash
# Navigate to the worktree directory
cd "${PROJECT_ROOT}/review-GH-42"

# Check git status
git status
```

**What to look for:**
- "Changes not staged for commit" (red text) = uncommitted modifications
- "Changes to be committed" (green text) = staged but not committed
- "Untracked files" (red text) = new files not added to git
- "nothing to commit, working tree clean" = SAFE TO REMOVE

**If uncommitted work exists:**

**Option A - Commit the work:**
```bash
git add .
git commit -m "Final changes before removing worktree"
git push origin feature-branch-name
```

**Option B - Stash the work (save for later):**
```bash
# Save all changes temporarily
git stash push -m "Work from review-GH-42 worktree"

# Verify stash was created
git stash list
# Should show: stash@{0}: On branch-name: Work from review-GH-42 worktree
```

**Option C - Discard the work (PERMANENT):**
```bash
# WARNING: This deletes all uncommitted changes forever
git reset --hard HEAD
git clean -fd
```

### Step 2: Check Pull Request Status

**What is PR status?**
The current state of the GitHub pull request associated with this worktree's branch.

**How to check:**
```bash
# View PR status for current branch
gh pr status

# Or check specific PR
gh pr view 42
```

**Safe removal conditions:**
- PR is merged ✓
- PR is closed (declined) ✓
- PR is draft and you want to abandon it ✓

**DO NOT remove if:**
- PR is open and active ✗
- PR needs more commits ✗
- PR is awaiting review ✗

### Step 3: Check for Running Processes

**What are running processes?**
Programs or servers that were started inside this worktree directory and are still active.

**How to check:**
```bash
# Find processes using this directory
lsof +D "${PROJECT_ROOT}/review-GH-42"

# Check for development servers on allocated ports
# (Check registry for port assignments)
lsof -i :3000  # Example: React dev server
lsof -i :8000  # Example: Python server
```

**If processes are found:**
```bash
# Stop gracefully first (Ctrl+C in terminal where it's running)
# Or kill by process ID
kill <PID>

# Force kill if unresponsive
kill -9 <PID>
```

### Step 4: Check Registry Entry

**What is the registry?**
A JSON file tracking all active worktrees, their ports, branches, and assigned agents. Located at `design/worktree-registry.json`.

**How to check:**
```bash
# View registry entry for this worktree
cat design/worktree-registry.json | grep -A 10 "review-GH-42"
```

**Example registry entry:**
```json
{
  "worktree_id": "review-GH-42",
  "path": "${PROJECT_ROOT}/review-GH-42",
  "branch": "feature/new-api",
  "pr_number": 42,
  "assigned_agent": "code-reviewer-1",
  "ports": [3000, 8000],
  "created_at": "2025-12-30T10:00:00Z",
  "status": "active"
}
```

**Before removal, note:**
- Allocated ports (need to be released)
- Assigned agent (needs reassignment if active)
- Any dependencies on other worktrees

### Complete Checklist Template

```markdown
## Pre-Removal Checklist for: review-GH-42

- [ ] **Uncommitted Work**: None (verified with `git status`)
- [ ] **Stash Created**: No (or Yes, stash@{0})
- [ ] **PR Status**: Merged (or Closed/Abandoned)
- [ ] **Running Processes**: None found
- [ ] **Ports Released**: 3000, 8000 released
- [ ] **Registry Reviewed**: Entry identified
- [ ] **Agent Notified**: code-reviewer-1 reassigned
- [ ] **Dependencies Checked**: No other worktrees depend on this

✓ **Safe to remove**: YES
```

---

## Removal Commands

### Basic Removal (Standard)

**When to use:**
- All checklist items completed
- Worktree is clean (no uncommitted work)
- Normal removal scenario

**Command:**
```bash
# Syntax: git worktree remove <path>
git worktree remove ../review-GH-42
```

**What happens:**
1. Git checks if worktree is clean
2. Removes worktree directory and all files
3. Removes git metadata for this worktree
4. Updates main repository's worktree list

**Expected output:**
```
# No output = successful removal
```

**Full path example:**
```bash
# From main repository directory
cd "${PROJECT_ROOT}"

# Remove by relative path
git worktree remove ../review-GH-42

# Or by absolute path
git worktree remove "${PROJECT_ROOT}/review-GH-42"
```

### Force Removal

**When to use:**
- Worktree has uncommitted changes you want to DISCARD
- Emergency cleanup
- Corrupted worktree that can't be cleaned normally

**WARNING:** Force removal PERMANENTLY DELETES all uncommitted work.

**Command:**
```bash
git worktree remove --force ../review-GH-42
```

**Alternative (short form):**
```bash
git worktree remove -f ../review-GH-42
```

**What --force does:**
- Bypasses uncommitted work check
- Deletes worktree even if not clean
- No confirmation prompt (PERMANENT)

**Example scenario:**
```bash
# Check worktree has uncommitted work
cd review-GH-42
git status
# Output: Changes not staged for commit: modified: src/api.js

# Decide to force remove
cd ..
git worktree remove --force review-GH-42
# Worktree and all uncommitted changes are gone forever
```

### Pruning Stale Entries

**What is a stale entry?**
A stale entry is when git thinks a worktree exists, but the directory was manually deleted or moved without using `git worktree remove`.

**How stale entries happen:**
- Someone deleted worktree folder directly (rm -rf)
- Disk cleanup tool removed the directory
- Directory moved to trash/recycle bin
- File system corruption

**Symptoms:**
```bash
git worktree list
# Shows worktree that doesn't actually exist
# ${PROJECT_ROOT}/review-GH-42  <branch-name>  [missing]
```

**Command to clean up:**
```bash
git worktree prune
```

**What prune does:**
1. Scans all registered worktrees
2. Checks if directories actually exist
3. Removes git metadata for missing worktrees
4. No effect on existing worktrees

**Verbose output:**
```bash
git worktree prune --verbose
# Output:
# Removing worktrees/review-GH-42: gitdir file points to non-existent location
```

**When to run prune:**
- After manual directory deletions
- When `git worktree list` shows [missing]
- During cleanup operations
- Before creating new worktrees with same name

### Dry Run (Preview Only)

**What is dry run?**
Dry run shows what WOULD be removed without actually removing anything. Used for verification.

**Command:**
```bash
git worktree remove --dry-run ../review-GH-42
```

**Example output:**
```
# Would remove worktree '${PROJECT_ROOT}/review-GH-42'
```

**When to use dry run:**
- Testing removal before executing
- Verifying path is correct
- Checking if worktree is recognized by git
- Training/learning git worktree commands

---

## Handling Removal Failures

**What is a removal failure?**
A removal failure occurs when `git worktree remove` cannot complete due to uncommitted changes, locked files, or git metadata corruption.

**Common failure messages and solutions:**

### Error: "contains modified or untracked files"

```bash
fatal: 'review-GH-42' contains modified or untracked files, use --force to delete it
```

**Cause:** Worktree has uncommitted work.

**Solutions:**
1. Commit the work (see [Step 1: Check for Uncommitted Work](#step-1-check-for-uncommitted-work))
2. Stash the work: `git stash push -m "Work from worktree"`
3. Force remove (DESTROYS uncommitted work): `git worktree remove --force <path>`

### Error: "is not a working tree"

```bash
fatal: 'review-GH-42' is not a working tree
```

**Cause:** Path doesn't exist or isn't recognized as a worktree.

**Solutions:**
1. Verify path with `git worktree list`
2. Run `git worktree prune` to clean stale entries
3. Manually delete directory if it exists: `rm -rf <path>`

### Error: "locked"

```bash
fatal: working tree 'review-GH-42' is locked
```

**Cause:** Worktree was explicitly locked to prevent removal.

**Solutions:**
```bash
# Unlock first, then remove
git worktree unlock ../review-GH-42
git worktree remove ../review-GH-42
```

### Error: Permission denied

```bash
error: unable to remove directory: Permission denied
```

**Cause:** Running processes or OS file locks.

**Solutions:**
1. Stop all processes using the directory (see [Step 3: Check for Running Processes](#step-3-check-for-running-processes))
2. Close any editors/IDEs with files open in that directory
3. Wait a moment and retry

---

**Continue to:** [Part 2: Post-Removal and Automation](removing-worktrees-part2-post-removal.md)

**Return to:** [Worktree Management Overview](../SKILL.md)
