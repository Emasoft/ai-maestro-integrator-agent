# Registry System: Validation and Cleanup

## Table of Contents

1. [When you need schema and operations → Related Part](#related-part)
2. [When you need to enforce registry rules → Validation Rules](#validation-rules)
   - [If you need to check ID uniqueness → 1. Unique IDs](#1-unique-ids)
   - [When you need to validate paths → 2. Valid Paths](#2-valid-paths)
   - [If you're checking port conflicts → 3. No Port Conflicts](#3-no-port-conflicts)
   - [When you need to validate status → 4. Valid Status Values](#4-valid-status-values)
   - [If you're verifying required fields → 5. Required Fields Present](#5-required-fields-present)
3. [When you need to clean stale entries → Automatic Cleanup](#automatic-cleanup)
   - [If you need to identify stale entries → What is a Stale Entry?](#what-is-a-stale-entry)
   - [When you need the detection logic → Stale Detection Algorithm](#stale-detection-algorithm)
   - [If you need to run cleanup → Cleanup Process](#cleanup-process)
   - [When you need to force cleanup → Manual Cleanup Override](#manual-cleanup-override)
4. [If you encounter registry problems → Troubleshooting](#troubleshooting)
5. [When you need additional context → Related References](#related-references)

---

## Related Part

For registry schema, location, and operations:

- [Registry System Part 1: Schema and Operations](./registry-system-part1-schema-operations.md)
  - When you need to understand the registry system → Overview
  - If you need to find the registry file → Registry Location
  - When you need to understand registry structure → Registry Schema
  - When you need to modify the registry → Registry Operations

---

## Validation Rules

All registry operations must enforce these validation rules:

### 1. Unique IDs

**Rule:** Each `id` must be unique across all entries

**Check:**

```python
def validate_unique_id(registry, new_id):
    existing_ids = [wt["id"] for wt in registry["worktrees"]]
    if new_id in existing_ids:
        raise ValueError(f"Worktree ID '{new_id}' already exists")
```

**Why:** Prevents confusion and ensures each worktree can be uniquely identified

### 2. Valid Paths

**Rule:** Each `path` must:

- Be relative (start with `../`)
- Not already exist in registry
- Not point inside main repository
- Follow naming convention for the purpose

**Check:**

```python
def validate_path(registry, path, purpose):
    # Check path is relative
    if not path.startswith("../"):
        raise ValueError("Path must be relative (start with '../')")

    # Check path doesn't exist
    existing_paths = [wt["path"] for wt in registry["worktrees"]]
    if path in existing_paths:
        raise ValueError(f"Path '{path}' already in use")

    # Check follows naming convention
    template = registry["naming_convention"][purpose]
    # ... validate against template
```

**Why:** Prevents path conflicts and maintains consistent directory structure

### 3. No Port Conflicts

**Rule:** Each port can only be allocated to one worktree at a time

**Check:**

```python
def validate_ports(registry, new_ports):
    allocated_ports = []
    for wt in registry["worktrees"]:
        if wt["status"] != "pending-removal":
            allocated_ports.extend(wt["port_allocations"])

    conflicts = set(new_ports) & set(allocated_ports)
    if conflicts:
        raise ValueError(f"Ports already allocated: {conflicts}")
```

**Why:** Prevents service conflicts when running multiple worktrees simultaneously

### 4. Valid Status Values

**Rule:** `status` must be one of: `active`, `locked`, `pending-removal`

**Check:**

```python
VALID_STATUSES = ["active", "locked", "pending-removal"]

def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}")
```

**Why:** Ensures consistent state management across the system

### 5. Required Fields Present

**Rule:** All required fields must be present in every entry

**Check:**

```python
REQUIRED_FIELDS = ["id", "path", "branch", "created", "purpose", "status"]

def validate_required_fields(entry):
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
```

**Why:** Ensures registry integrity and prevents incomplete records

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
- On demand via `eia cleanup-worktrees` command
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
eia remove-worktree review-GH-42 --force
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
   eia rebuild-registry --scan-worktrees
   ```

   This scans filesystem and rebuilds registry from actual worktrees

### Port Already in Use (but not in registry)

**Symptom:** Port allocation fails but registry shows port as available

**Solution:**

1. Check actual port usage: `lsof -i :8080`
2. If port used by non-worktree process, update port ranges to exclude it
3. If port used by unregistered worktree, register it:

   ```bash
   eia register-existing ../path/to/worktree
   ```

### Duplicate IDs After Manual Edit

**Symptom:** Registry validation fails with "duplicate ID" error

**Solution:**

1. Open `design/worktrees/registry.json` in editor
2. Find duplicate `id` values
3. Rename one of them to make unique (follow naming convention)
4. Validate: `eia validate-registry`

### Worktree Exists but Not in Registry

**Symptom:** Git worktree shows in `git worktree list` but not in AMIA registry

**Solution:**

```bash
eia register-existing ../path/to/worktree --purpose review --issue GH-42
```

This adds existing worktree to registry without recreating it.

---

## Related References

Before using the registry system, understand these concepts:

- [Registry System Part 1: Schema](./registry-system-part1-schema.md) - Schema, location, and structure
- [Worktree Creation Process](./creating-worktrees.md) - How worktrees are created and registered
- [Port Allocation Strategy](./port-allocation.md) - How ports are assigned and managed
- [Naming Conventions](./worktree-naming-conventions.md) - Rules for worktree IDs and paths
- [Worktree Removal](./removing-worktrees-index.md) - When and how worktrees are removed
