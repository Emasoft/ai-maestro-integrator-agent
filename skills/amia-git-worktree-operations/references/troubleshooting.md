# Git Worktree Troubleshooting

Common issues and solutions when working with git worktrees.

---

## Table of Contents

- 1. Creation Issues
  - 1.1 If worktree creation fails with "already checked out"
  - 1.2 If worktree path already exists
  - 1.3 If remote branch not found
- 2. Isolation Violations
  - 2.1 If agent writes to wrong worktree
  - 2.2 If main repo is contaminated
- 3. Git Operation Errors
  - 3.1 If concurrent operations cause lock conflicts
  - 3.2 If push fails with non-fast-forward
- 4. Cleanup Issues
  - 4.1 If worktree removal fails
  - 4.2 If orphaned worktree references remain
- 5. Recovery Procedures
  - 5.1 When to force-remove worktrees
  - 5.2 When to recreate from scratch

---

## 1. Creation Issues

### 1.1 If worktree creation fails with "already checked out"

**Error**: `fatal: 'branch-name' is already checked out at '/path/to/repo'`

**Cause**: The branch is checked out in another worktree or the main repo.

**Solution**:
```bash
# Option 1: Use a different branch name
git worktree add /tmp/worktrees/pr-123 -b pr-123-work origin/pr-123

# Option 2: Find and remove the existing checkout
git worktree list
git worktree remove /path/to/existing/worktree
```

### 1.2 If worktree path already exists

**Error**: `fatal: '/tmp/worktrees/pr-123' already exists`

**Solution**:
```bash
# Remove the directory if it's not a valid worktree
rm -rf /tmp/worktrees/pr-123

# Or if it's a worktree, remove it properly
git worktree remove /tmp/worktrees/pr-123 --force
```

### 1.3 If remote branch not found

**Error**: `fatal: invalid reference: origin/feature-branch`

**Solution**:
```bash
# Fetch all remote branches
git fetch origin --all

# Or fetch the specific PR
git fetch origin pull/123/head:pr-123
```

---

## 2. Isolation Violations

### 2.1 If agent writes to wrong worktree

**Detection**:
```bash
# Check git status in all worktrees
for wt in /tmp/worktrees/*; do
  echo "=== $wt ===" && git -C "$wt" status --short
done
```

**Recovery**:
```bash
# Save changes
cd /wrong/worktree
git diff > /tmp/misplaced-changes.patch

# Discard changes in wrong location
git checkout -- .

# Apply to correct worktree
cd /correct/worktree
git apply /tmp/misplaced-changes.patch
```

### 2.2 If main repo is contaminated

**Detection**:
```bash
cd /path/to/main-repo
git status
```

**Recovery**:
```bash
# Stash or save changes
git stash

# Or discard if unwanted
git checkout -- .
git clean -fd
```

---

## 3. Git Operation Errors

### 3.1 If concurrent operations cause lock conflicts

**Error**: `fatal: Unable to create '/path/.git/index.lock': File exists.`

**Cause**: Multiple agents running git operations simultaneously.

**Solution**:
```bash
# Wait for other operations to complete, then remove stale lock
rm -f /path/to/repo/.git/index.lock

# Prevent future conflicts: serialize git operations through orchestrator
```

### 3.2 If push fails with non-fast-forward

**Error**: `! [rejected] ... (non-fast-forward)`

**Cause**: Remote has changes not in local branch.

**Solution**:
```bash
git fetch origin
git rebase origin/target-branch
git push
```

---

## 4. Cleanup Issues

### 4.1 If worktree removal fails

**Error**: Various locking or dirty-tree errors

**Solution**:
```bash
# Force removal
git worktree remove /tmp/worktrees/pr-123 --force

# If that fails, prune manually
rm -rf /tmp/worktrees/pr-123
git worktree prune
```

### 4.2 If orphaned worktree references remain

**Detection**:
```bash
git worktree list  # Shows worktrees that don't exist on disk
```

**Solution**:
```bash
git worktree prune
```

---

## 5. Recovery Procedures

### 5.1 When to force-remove worktrees

Force removal is acceptable when:
- Worktree directory is corrupted
- Changes have been saved elsewhere
- PR has been closed/merged
- Clean restart is needed

### 5.2 When to recreate from scratch

Recreate the worktree when:
1. Corruption is detected
2. Base branch has diverged significantly
3. After force-removal

```bash
# Clean removal
git worktree remove /tmp/worktrees/pr-123 --force 2>/dev/null || rm -rf /tmp/worktrees/pr-123
git worktree prune

# Fresh creation
git fetch origin pull/123/head:pr-123-new
git worktree add /tmp/worktrees/pr-123 pr-123-new
```

---

## See Also

- [worktree-fundamentals.md](worktree-fundamentals.md) - Basic concepts
- [worktree-cleanup.md](worktree-cleanup.md) - Safe cleanup procedures
- [parallel-pr-workflow.md](parallel-pr-workflow.md) - Multi-PR management
