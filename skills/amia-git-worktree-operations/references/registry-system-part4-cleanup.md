# Registry System - Part 4: Automatic Cleanup and Troubleshooting

## Table of Contents

- [Automatic Cleanup](#automatic-cleanup)
  - [What is a Stale Entry?](#what-is-a-stale-entry)
  - [Stale Detection Algorithm](#stale-detection-algorithm)
  - [Cleanup Process](#cleanup-process)
  - [Manual Cleanup Override](#manual-cleanup-override)
- [Troubleshooting](#troubleshooting)
  - [Registry File Corrupted](#registry-file-corrupted)
  - [Port Already in Use (but not in registry)](#port-already-in-use-but-not-in-registry)
  - [Duplicate IDs After Manual Edit](#duplicate-ids-after-manual-edit)
  - [Worktree Exists but Not in Registry](#worktree-exists-but-not-in-registry)
- [Related References](#related-references)

---

## Automatic Cleanup

The registry system includes automatic detection and cleanup of stale entries.

### What is a Stale Entry?

A worktree entry is considered **stale** if any of these conditions are met:

1. **Directory missing** - Path doesn't exist on filesystem
2. **Branch deleted** - Git branch no longer exists (locally or remotely)
3. **Status pending-removal for >7 days** - Entry marked for deletion but not removed
4. **Created >90 days ago with no recent activity** - Old worktree with no commits/changes

### Stale Detection Algorithm

```python
def detect_stale_entries(registry):
    stale_entries = []
    now = datetime.now()

    for entry in registry["worktrees"]:
        # Check 1: Directory missing
        if not os.path.exists(entry["path"]):
            stale_entries.append({
                "entry": entry,
                "reason": "directory_missing"
            })
            continue

        # Check 2: Branch deleted
        if not branch_exists(entry["branch"]):
            stale_entries.append({
                "entry": entry,
                "reason": "branch_deleted"
            })
            continue

        # Check 3: Pending removal too long
        if entry["status"] == "pending-removal":
            created = datetime.fromisoformat(entry["created"])
            age_days = (now - created).days
            if age_days > 7:
                stale_entries.append({
                    "entry": entry,
                    "reason": "pending_removal_expired"
                })
                continue

        # Check 4: Old with no activity
        created = datetime.fromisoformat(entry["created"])
        age_days = (now - created).days
        if age_days > 90:
            last_commit = get_last_commit_time(entry["path"])
            if (now - last_commit).days > 30:
                stale_entries.append({
                    "entry": entry,
                    "reason": "abandoned"
                })

    return stale_entries
```

### Cleanup Process

**Automatic cleanup runs:**

- On every worktree create/remove operation (cleanup others)
- On demand via `amia cleanup-worktrees` command
- Daily via cron/scheduled task (optional)

**Cleanup steps:**

1. Detect stale entries using algorithm above
2. For each stale entry:
   - Log reason for staleness
   - If `directory_missing`, remove registry entry immediately
   - If other reason, mark as `pending-removal` and notify user
3. After 7 days in `pending-removal`, force remove

**Example output:**

```
Stale worktree cleanup:
  - review-GH-42: Directory missing → Removed from registry
  - feature-old-ui: Abandoned (90+ days, no activity) → Marked for removal
  - bugfix-GH-15: Branch deleted → Marked for removal
```

### Manual Cleanup Override

Users can force cleanup of specific entries:

```bash
amia remove-worktree review-GH-42 --force
```

This bypasses the 7-day pending-removal period and removes immediately.

---

## Troubleshooting

### Registry File Corrupted

**Symptom:** JSON parse errors when reading registry

**Solution:**

1. Restore from backup: `design/worktrees/registry.json.backup`
2. If no backup, rebuild registry:

   ```bash
   amia rebuild-registry --scan-worktrees
   ```

   This scans filesystem and rebuilds registry from actual worktrees

### Port Already in Use (but not in registry)

**Symptom:** Port allocation fails but registry shows port as available

**Solution:**

1. Check actual port usage: `lsof -i :8080`
2. If port used by non-worktree process, update port ranges to exclude it
3. If port used by unregistered worktree, register it:

   ```bash
   amia register-existing ../path/to/worktree
   ```

### Duplicate IDs After Manual Edit

**Symptom:** Registry validation fails with "duplicate ID" error

**Solution:**

1. Open `design/worktrees/registry.json` in editor
2. Find duplicate `id` values
3. Rename one of them to make unique (follow naming convention)
4. Validate: `amia validate-registry`

### Worktree Exists but Not in Registry

**Symptom:** Git worktree shows in `git worktree list` but not in AMIA registry

**Solution:**

```bash
amia register-existing ../path/to/worktree --purpose review --issue GH-42
```

This adds existing worktree to registry without recreating it.

---

## Related References

Before using the registry system, understand these concepts:

- [Worktree Creation Process](./creating-worktrees.md) - How worktrees are created and registered
- [Port Allocation Strategy](./port-allocation.md) - How ports are assigned and managed
- [Naming Conventions](./worktree-naming-conventions.md) - Rules for worktree IDs and paths
- [Worktree Removal](./removing-worktrees-index.md) - When and how worktrees are removed
