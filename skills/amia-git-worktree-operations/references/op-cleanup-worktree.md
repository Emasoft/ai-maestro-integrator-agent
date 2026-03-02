---
name: op-cleanup-worktree
description: "Safely remove a git worktree after PR completion"
procedure: support-skill
workflow-instruction: support
---

# Operation: Cleanup Worktree


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify worktree exists](#step-1-verify-worktree-exists)
  - [Step 2: Check for uncommitted changes](#step-2-check-for-uncommitted-changes)
  - [Step 3: Check for unpushed commits](#step-3-check-for-unpushed-commits)
  - [Step 4: Navigate out of worktree](#step-4-navigate-out-of-worktree)
  - [Step 5: Remove worktree](#step-5-remove-worktree)
  - [Step 6: Verify removal](#step-6-verify-removal)
  - [Step 7: Prune stale entries (optional)](#step-7-prune-stale-entries-optional)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Safe Removal Checklist](#safe-removal-checklist)
- [Force Removal](#force-removal)
- [Error Handling](#error-handling)
  - [Worktree is dirty](#worktree-is-dirty)
  - [Cannot remove: still checked out](#cannot-remove-still-checked-out)
  - [Lock file present](#lock-file-present)
  - [Directory still exists after removal](#directory-still-exists-after-removal)
- [Complete Cleanup Script](#complete-cleanup-script)
- [Verification](#verification)

## Purpose

Safely remove a git worktree after the PR work is complete, ensuring no uncommitted changes are lost.

## When to Use

- After PR has been merged
- After PR has been closed
- When worktree is no longer needed
- During cleanup of stale worktrees

## Prerequisites

1. Worktree path is known
2. All changes have been committed and pushed
3. Verification that worktree can be safely removed

## Procedure

### Step 1: Verify worktree exists

```bash
WORKTREE_PATH="/tmp/worktrees/pr-123"

# Check in worktree list
if ! git worktree list | grep -q "$WORKTREE_PATH"; then
  echo "Worktree not found in list: $WORKTREE_PATH"
  exit 1
fi

echo "Worktree found: $WORKTREE_PATH"
```

### Step 2: Check for uncommitted changes

```bash
cd "$WORKTREE_PATH"

# Check git status
UNCOMMITTED=$(git status --porcelain)

if [ -n "$UNCOMMITTED" ]; then
  echo "WARNING: Uncommitted changes exist:"
  echo "$UNCOMMITTED"
  echo ""
  echo "Options:"
  echo "  1. Commit and push changes first"
  echo "  2. Stash changes: git stash"
  echo "  3. Discard changes: git checkout -- . (DESTRUCTIVE)"
  echo "  4. Force remove (will lose changes)"
  exit 1
fi

echo "No uncommitted changes"
```

### Step 3: Check for unpushed commits

```bash
BRANCH=$(git branch --show-current)
UNPUSHED=$(git log "origin/$BRANCH..HEAD" --oneline 2>/dev/null)

if [ -n "$UNPUSHED" ]; then
  echo "WARNING: Unpushed commits exist:"
  echo "$UNPUSHED"
  echo ""
  echo "Push before removing: git push origin $BRANCH"
  exit 1
fi

echo "All commits pushed"
```

### Step 4: Navigate out of worktree

```bash
# Must not be inside worktree when removing
cd "$(git worktree list | head -1 | awk '{print $1}')"
echo "Moved to main repo"
```

### Step 5: Remove worktree

```bash
# Safe remove (will fail if dirty)
git worktree remove "$WORKTREE_PATH"

if [ $? -eq 0 ]; then
  echo "Worktree removed successfully"
else
  echo "ERROR: Failed to remove worktree"
  echo "Try: git worktree remove --force $WORKTREE_PATH"
  exit 1
fi
```

### Step 6: Verify removal

```bash
# Check worktree list
if git worktree list | grep -q "$WORKTREE_PATH"; then
  echo "WARNING: Worktree still in list"
else
  echo "Worktree removed from list"
fi

# Check directory
if [ -d "$WORKTREE_PATH" ]; then
  echo "WARNING: Directory still exists"
else
  echo "Directory removed"
fi
```

### Step 7: Prune stale entries (optional)

```bash
# Clean up any stale worktree entries
git worktree prune

echo "Pruned stale worktree entries"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| worktree_path | string | yes | Path to worktree to remove |
| force | boolean | no | Force removal even with uncommitted changes |
| prune | boolean | no | Run prune after removal (default: true) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether removal succeeded |
| path | string | Path that was removed |
| had_uncommitted | boolean | Whether there were uncommitted changes |
| force_used | boolean | Whether force flag was used |

## Example Output

```json
{
  "success": true,
  "path": "/tmp/worktrees/pr-123",
  "had_uncommitted": false,
  "force_used": false
}
```

## Safe Removal Checklist

Before removing, verify:

- [ ] No uncommitted changes (`git status` is clean)
- [ ] No unpushed commits (`git log origin/branch..HEAD` is empty)
- [ ] Not currently inside the worktree
- [ ] No other processes using the worktree

## Force Removal

**Use only when:**
- Worktree is corrupted
- Changes are intentionally being discarded
- User has explicitly approved

```bash
# Force remove (DESTRUCTIVE)
git worktree remove --force "$WORKTREE_PATH"
```

**Warning**: Force removal will delete uncommitted changes permanently.

## Error Handling

### Worktree is dirty

**Cause**: Uncommitted changes exist.

**Solution**: Commit, stash, or discard changes first.

### Cannot remove: still checked out

**Cause**: Working directory is inside worktree.

**Solution**: cd to main repo first.

### Lock file present

**Cause**: Git operation in progress.

**Solution**: Wait for operation to complete.

### Directory still exists after removal

**Cause**: Partial removal or permission issue.

**Solution**: Manually remove directory after verifying it's safe.

## Complete Cleanup Script

```bash
#!/bin/bash
# cleanup_worktree.sh

WORKTREE_PATH="$1"
FORCE="${2:-false}"

if [ -z "$WORKTREE_PATH" ]; then
  echo "Usage: cleanup_worktree.sh <worktree_path> [force=false]"
  exit 1
fi

echo "=== Worktree Cleanup ==="
echo "Path: $WORKTREE_PATH"

# Verify exists
if ! git worktree list | grep -q "$WORKTREE_PATH"; then
  echo "ERROR: Worktree not found"
  exit 1
fi

# Check for uncommitted
if [ -d "$WORKTREE_PATH" ]; then
  cd "$WORKTREE_PATH"
  if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes:"
    git status --short

    if [ "$FORCE" != "true" ]; then
      echo ""
      echo "Cannot remove: uncommitted changes exist"
      echo "Use force=true to remove anyway (DESTRUCTIVE)"
      exit 1
    else
      echo "Force flag set - proceeding despite uncommitted changes"
    fi
  fi

  # Check unpushed
  BRANCH=$(git branch --show-current)
  if [ -n "$(git log origin/$BRANCH..HEAD --oneline 2>/dev/null)" ]; then
    echo "Unpushed commits exist"
    if [ "$FORCE" != "true" ]; then
      echo "Push commits first or use force=true"
      exit 1
    fi
  fi
fi

# Move out of worktree
cd "$(git worktree list | head -1 | awk '{print $1}')"

# Remove
if [ "$FORCE" = "true" ]; then
  git worktree remove --force "$WORKTREE_PATH"
else
  git worktree remove "$WORKTREE_PATH"
fi

if [ $? -eq 0 ]; then
  echo "Worktree removed"
  git worktree prune
  echo "Stale entries pruned"
else
  echo "ERROR: Removal failed"
  exit 1
fi
```

## Verification

After cleanup:

```bash
# Verify worktree is gone
git worktree list | grep -v "$WORKTREE_PATH" && echo "Not in list"

# Verify directory is gone
[ ! -d "$WORKTREE_PATH" ] && echo "Directory removed"

# Check disk space recovered
df -h /tmp
```
