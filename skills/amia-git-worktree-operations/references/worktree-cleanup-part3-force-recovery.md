# Worktree Cleanup Part 3: Force Removal and Recovery

## Table of Contents

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

---

## 3.5 Force Removal Scenarios and Their Risks

### When Force Removal is Needed

Use `--force` only when:
1. Normal removal fails despite worktree being clean
2. Worktree is corrupted beyond repair
3. Emergency disk space recovery needed
4. Worktree directory was partially deleted

### Force Removal Command

```bash
git worktree remove --force /tmp/worktrees/pr-123
```

### Risks of Force Removal

| Risk | Description | Mitigation |
|------|-------------|------------|
| Lost work | Uncommitted changes deleted | Verify status first |
| Orphaned branches | Branch may still exist | Clean up branches separately |
| Stale metadata | May leave .git/worktrees entries | Run `git worktree prune` |
| Process disruption | Running processes lose files | Check for running processes |

### Safe Force Removal Procedure

**Step 1: Document current state**
```bash
cd /tmp/worktrees/pr-123 2>/dev/null && git status
git worktree list
```

**Step 2: Create backup if possible**
```bash
cp -r /tmp/worktrees/pr-123 /tmp/backup-pr-123
```

**Step 3: Force remove**
```bash
cd /tmp  # Navigate away
git worktree remove --force /tmp/worktrees/pr-123
```

**Step 4: Prune and verify**
```bash
git worktree prune
git worktree list
```

### Double-Force Removal

For extremely stubborn worktrees:
```bash
# Remove worktree directory manually
rm -rf /tmp/worktrees/pr-123

# Prune the stale entry
git worktree prune

# Verify
git worktree list
```

---

## 3.6 Pruning Stale Worktree Entries

### What is Pruning?

Pruning removes worktree metadata entries from `.git/worktrees/` when the actual worktree directory no longer exists.

### When Pruning is Needed

- Worktree directory was manually deleted (rm -rf)
- Worktree directory was moved or renamed
- System crash left inconsistent state
- Disk was reformatted or unmounted

### Dry Run Pruning

See what would be pruned without making changes:
```bash
git worktree prune --dry-run
```

**Example output:**
```
Removing worktrees/pr-123: gitdir file points to non-existent location
Removing worktrees/pr-456: gitdir file points to non-existent location
```

### Execute Pruning

```bash
git worktree prune
```

### Verbose Pruning

See details during pruning:
```bash
git worktree prune --verbose
```

### Automated Prune Schedule

Consider adding to git hooks or cron:
```bash
# In main repo's post-checkout hook
git worktree prune 2>/dev/null || true
```

### Verifying Prune Results

```bash
# Before prune
ls /path/to/main-repo/.git/worktrees/
# Shows: pr-123  pr-456  pr-789

# After prune (assuming pr-123 and pr-456 were stale)
ls /path/to/main-repo/.git/worktrees/
# Shows: pr-789
```

---

## 3.7 Disk Space Recovery After Cleanup

### Understanding Worktree Disk Usage

Each worktree uses:
- **Working files:** Full copy of tracked files
- **Index:** Staging area (~small)
- **Metadata:** In `.git/worktrees/` (~very small)

**Not duplicated:**
- Git objects (shared with main repo)
- Pack files (shared)
- Refs (shared)

### Estimating Space Recovery

```bash
# Size of worktree directory
du -sh /tmp/worktrees/pr-123

# Size of all worktrees
du -sh /tmp/worktrees/*
```

### Space Recovery After Removal

After removing worktrees, the following is recovered:
- Worktree directory size (full working files)
- Metadata in `.git/worktrees/<name>/`

**Not immediately recovered:**
- Unreachable objects (need `git gc`)
- Loose objects from worktree commits

### Running Garbage Collection

After removing multiple worktrees:
```bash
cd /path/to/main-repo
git gc --prune=now
```

### Aggressive Cleanup

For maximum space recovery:
```bash
cd /path/to/main-repo

# Remove all stale worktree entries
git worktree prune

# Expire all reflogs
git reflog expire --expire=now --all

# Aggressive garbage collection
git gc --aggressive --prune=now
```

### Monitoring Disk Usage

```bash
# Git database size
du -sh /path/to/main-repo/.git

# Worktrees metadata size
du -sh /path/to/main-repo/.git/worktrees

# All worktree directories
du -sh /tmp/worktrees/*/
```

### Cleanup Script

```bash
#!/bin/bash
# cleanup_all_worktrees.sh

MAIN_REPO="/path/to/main-repo"
WORKTREE_BASE="/tmp/worktrees"

cd "$MAIN_REPO"

# List current worktrees
echo "Current worktrees:"
git worktree list

# Remove each worktree (interactively)
for wt in "$WORKTREE_BASE"/*/; do
    if [ -d "$wt" ]; then
        read -p "Remove worktree $wt? [y/N] " response
        if [ "$response" = "y" ]; then
            git worktree remove "$wt" || git worktree remove --force "$wt"
        fi
    fi
done

# Prune stale entries
git worktree prune --verbose

# Run garbage collection
echo "Running garbage collection..."
git gc --prune=now

echo "Cleanup complete!"
```

---

Back to [worktree-cleanup.md](worktree-cleanup.md) | Previous: [worktree-cleanup-part2-removal-procedures.md](worktree-cleanup-part2-removal-procedures.md)
