# Worktree Cleanup Part 1: Timing and Verification

## Table of Contents

- 3.1 When to Clean Up Worktrees (Timing and Triggers)
  - 3.1.1 Cleanup triggers (PR merged, closed, abandoned, branch deleted)
  - 3.1.2 Timing considerations (immediate, soon, delay)
  - 3.1.3 Pre-cleanup checklist
- 3.2 Verifying No Uncommitted Changes Exist
  - 3.2.1 Quick status check with `git status --porcelain`
  - 3.2.2 Status code meanings (??, M, A, D)
  - 3.2.3 Comprehensive change detection script
  - 3.2.4 What to do with uncommitted changes (commit, discard, stash, patch)

---

## 3.1 When to Clean Up Worktrees (Timing and Triggers)

### Cleanup Triggers

Clean up a worktree when ANY of these conditions are met:

| Trigger | Description | Urgency |
|---------|-------------|---------|
| PR merged | Pull request successfully merged to base branch | High |
| PR closed | Pull request closed without merge | High |
| PR abandoned | No activity for extended period | Medium |
| Branch deleted | Remote branch no longer exists | High |
| Task complete | Agent finished all work on the PR | Medium |
| Disk pressure | Running low on disk space | Depends |

### Timing Considerations

**Clean up IMMEDIATELY when:**
- PR is merged and branch deleted on remote
- PR is closed/rejected
- Sensitive data was in the worktree

**Clean up SOON when:**
- Work is complete and pushed
- Agent has moved to different task
- Worktree hasn't been used for days

**Delay cleanup when:**
- PR is pending review (might need changes)
- Tests are still running
- Waiting for CI/CD results

### Pre-Cleanup Checklist

Before initiating cleanup, verify:

```
[ ] All changes are committed
[ ] All commits are pushed to remote
[ ] PR status is final (merged/closed)
[ ] No running processes use worktree files
[ ] No other agents are assigned to this worktree
[ ] Branch can be safely deleted (if applicable)
```

---

## 3.2 Verifying No Uncommitted Changes Exist

### Quick Status Check

```bash
cd /tmp/worktrees/pr-123
git status --porcelain
```

**Interpreting output:**
- Empty output: Clean, safe to remove
- Any output: Has uncommitted changes, do NOT remove

### Status Code Meanings

```
?? file.txt    # Untracked file
 M file.txt    # Modified, not staged
M  file.txt    # Modified, staged
A  file.txt    # New file, staged
D  file.txt    # Deleted, staged
 D file.txt    # Deleted, not staged
```

### Comprehensive Change Detection

```bash
#!/bin/bash
# Check for ALL types of uncommitted changes

WORKTREE="/tmp/worktrees/pr-123"
cd "$WORKTREE"

# Check for uncommitted changes
if ! git diff --quiet; then
    echo "ERROR: Unstaged changes exist"
    exit 1
fi

# Check for staged but uncommitted changes
if ! git diff --cached --quiet; then
    echo "ERROR: Staged changes not committed"
    exit 1
fi

# Check for untracked files
if [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "ERROR: Untracked files exist"
    exit 1
fi

echo "OK: Worktree is clean"
```

### What to Do with Uncommitted Changes

**Option 1: Commit and push them**
```bash
git add -A
git commit -m "Final changes before cleanup"
git push origin pr-123
```

**Option 2: Discard them (if truly unwanted)**
```bash
# WARNING: This permanently discards changes
git checkout -- .
git clean -fd
```

**Option 3: Stash them (if unsure)**
```bash
git stash save "Stashed before worktree cleanup"
# Note: Stash is accessible from main repo
```

**Option 4: Move changes to main repo (rare)**
```bash
# Create patch
git diff > /tmp/changes.patch

# Apply in main repo
cd /path/to/main-repo
git apply /tmp/changes.patch
```

---

Back to [worktree-cleanup.md](worktree-cleanup.md) | Next: [worktree-cleanup-part2-removal-procedures.md](worktree-cleanup-part2-removal-procedures.md)
