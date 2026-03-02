# Registry System - Part 2: Operations

## Table of Contents

- [Registry Operations](#registry-operations)
  - [Create Entry](#create-entry)
  - [Update Status](#update-status)
  - [Remove Entry](#remove-entry)
  - [Query by Purpose](#query-by-purpose)
  - [Query by Issue](#query-by-issue)

---

## Registry Operations

### Create Entry

**When:** Creating a new worktree

**Steps:**
1. Generate unique ID from naming convention template
2. Validate ID doesn't already exist
3. Allocate ports from appropriate ranges
4. Create entry with `status: "active"`
5. Write updated registry to disk
6. Return entry object to caller

**Example:**
```python
entry = {
    "id": "review-GH-42",
    "path": "../review-GH-42",
    "branch": "feature/new-auth",
    "created": "2025-12-31T10:00:00Z",
    "purpose": "review",
    "issue": "GH-42",
    "port_allocations": [8080, 5432],
    "status": "active"
}
registry["worktrees"].append(entry)
save_registry(registry)
```

### Update Status

**When:** Changing worktree state (active → locked, active → pending-removal)

**Steps:**
1. Find entry by ID
2. Validate new status is allowed (see status transition rules)
3. Update `status` field
4. Write updated registry to disk

**Example:**
```python
entry = find_entry_by_id("review-GH-42")
entry["status"] = "locked"
save_registry(registry)
```

**Status transition rules:**
- `active` → `locked` ✓ (allowed)
- `active` → `pending-removal` ✓ (allowed)
- `locked` → `active` ✓ (allowed)
- `locked` → `pending-removal` ✓ (allowed)
- `pending-removal` → any other status ✗ (not allowed, must remove entry)

### Remove Entry

**When:** Deleting a worktree

**Steps:**
1. Find entry by ID
2. Release allocated ports (make them available for reuse)
3. Remove entry from `worktrees` array
4. Write updated registry to disk

**Example:**
```python
entry = find_entry_by_id("review-GH-42")
release_ports(entry["port_allocations"])
registry["worktrees"].remove(entry)
save_registry(registry)
```

**Important:** Always remove registry entry AFTER successfully deleting the worktree directory. If directory deletion fails, keep the entry to avoid orphaned records.

### Query by Purpose

**When:** Finding all worktrees of a specific type

**Steps:**
1. Filter `worktrees` array by `purpose` field
2. Return matching entries

**Example:**
```python
review_worktrees = [wt for wt in registry["worktrees"] if wt["purpose"] == "review"]
```

### Query by Issue

**When:** Finding worktree associated with a GitHub issue

**Steps:**
1. Filter `worktrees` array by `issue` field
2. Return matching entry (should be unique)

**Example:**
```python
worktree = next((wt for wt in registry["worktrees"] if wt["issue"] == "GH-42"), None)
```
