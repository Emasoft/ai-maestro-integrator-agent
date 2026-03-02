# Worktree Operations Part 7: Troubleshooting

## Table of Contents
1. [Cannot Remove Worktree (Locked)](#problem-1-cannot-remove-worktree-locked)
2. [Worktree Path Already Exists](#problem-2-worktree-path-already-exists)
3. [Cannot Rebase (Uncommitted Changes)](#problem-3-cannot-rebase-uncommitted-changes)
4. [Force Push Rejected (--force-with-lease)](#problem-4-force-push-rejected---force-with-lease)
5. [Worktree List Shows Deleted Directory](#problem-5-worktree-list-shows-deleted-directory)
6. [Cannot Move Worktree (Path Does Not Exist)](#problem-6-cannot-move-worktree-path-does-not-exist)
7. [Rebase Conflicts Too Complex](#problem-7-rebase-conflicts-too-complex)
8. [Forgot Which Worktree Contains Which Work](#problem-8-forgot-which-worktree-contains-which-work)
9. [Disk Space Running Low](#problem-9-disk-space-running-low)
10. [Branch Not Tracking Remote](#problem-10-branch-not-tracking-remote)

---

## Troubleshooting

### Problem 1: Cannot Remove Worktree (Locked)

**Error**:
```
fatal: 'review-GH-42' is locked
```

**Solution**:
```bash
# Unlock first
git worktree unlock ../review-GH-42

# Then remove
git worktree remove ../review-GH-42
```

---

### Problem 2: Worktree Path Already Exists

**Error When Creating**:
```
fatal: '/Users/username/review-GH-42' already exists
```

**Solution 1: Remove Existing Directory**:
```bash
# If directory is empty or unwanted
rm -rf ../review-GH-42
git worktree add ../review-GH-42 review/issue-42
```

**Solution 2: Use Different Path**:
```bash
git worktree add ../review-GH-42-v2 review/issue-42
```

---

### Problem 3: Cannot Rebase (Uncommitted Changes)

**Error**:
```
error: cannot rebase: You have unstaged changes.
error: Please commit or stash them.
```

**Solution**:
```bash
# Option A: Commit changes
git add .
git commit -m "WIP before rebase"
git rebase origin/main

# Option B: Stash changes
git stash push -m "Changes before rebase"
git rebase origin/main
git stash pop  # After successful rebase
```

---

### Problem 4: Force Push Rejected (--force-with-lease)

**Error**:
```
 ! [rejected]        review/issue-42 -> review/issue-42 (stale info)
error: failed to push some refs
```

**What Happened**: Someone else pushed to the branch since your last fetch.

**Solution**:
```bash
# Step 1: Fetch latest
git fetch origin

# Step 2: Check what changed
git log HEAD..origin/review/issue-42

# Step 3: Rebase on remote branch
git rebase origin/review/issue-42

# Step 4: Try force push again
git push --force-with-lease origin review/issue-42
```

---

### Problem 5: Worktree List Shows Deleted Directory

**Symptom**:
```bash
git worktree list
```

**Output**:
```
/Users/username/myproject        a1b2c3d [main]
/Users/username/review-GH-42     e4f5g6h [review/issue-42] (prunable)
```

**What Happened**: Worktree directory was manually deleted without using `git worktree remove`.

**Solution**:
```bash
# Remove stale metadata
git worktree prune

# Verify it's gone
git worktree list
```

---

### Problem 6: Cannot Move Worktree (Path Does Not Exist)

**Error**:
```
fatal: '/Users/username/old-path' is not a working tree
```

**Solution**:
```bash
# Step 1: Verify actual path
git worktree list

# Step 2: Use correct path from output
git worktree move /correct/path/from/list /new/destination
```

---

### Problem 7: Rebase Conflicts Too Complex

**Symptom**: Too many conflicts to resolve manually.

**Solution 1: Abort and Merge Instead**:
```bash
# Abort the rebase
git rebase --abort

# Use merge instead
git merge origin/main

# Push normally (no force needed with merge)
git push origin review/issue-42
```

**Solution 2: Interactive Rebase**:
```bash
# Abort current rebase
git rebase --abort

# Start interactive rebase
git rebase -i origin/main

# In editor, mark problematic commits as 'drop' or 'squash'
# This reduces the number of commits to reapply
```

---

### Problem 8: Forgot Which Worktree Contains Which Work

**Solution: Search All Worktrees**:
```bash
# Create helper script ~/bin/search-worktrees.sh
#!/bin/bash
PATTERN="$1"
WORKTREES=$(git worktree list --porcelain | grep '^worktree' | cut -d' ' -f2)

for worktree in $WORKTREES; do
    echo "Searching $worktree..."
    cd "$worktree"
    git log --all --oneline --grep="$PATTERN"
    git status --short
    echo "---"
done
```

**Usage**:
```bash
search-worktrees.sh "authentication"
```

---

### Problem 9: Disk Space Running Low

**Solution: Find Large Worktrees**:
```bash
# Check size of each worktree
git worktree list --porcelain | grep '^worktree' | cut -d' ' -f2 | while read wt; do
    du -sh "$wt"
done | sort -h
```

**Remove Old Worktrees**:
```bash
# List by modification time
git worktree list --porcelain | grep '^worktree' | cut -d' ' -f2 | while read wt; do
    stat -f "%Sm %N" -t "%Y-%m-%d" "$wt"
done | sort
```

---

### Problem 10: Branch Not Tracking Remote

**Symptom**:
```bash
git status
```

**Output**:
```
On branch review/issue-42
nothing to commit, working tree clean
```

**No mention of remote tracking.**

**Solution: Set Upstream**:
```bash
git branch --set-upstream-to=origin/review/issue-42
```

**Verify**:
```bash
git status
```

**Output**:
```
On branch review/issue-42
Your branch is up to date with 'origin/review/issue-42'.
```

---

## End of Part 7

This is the final part of the worktree operations reference.

For a complete overview, see [worktree-operations.md](worktree-operations.md).
