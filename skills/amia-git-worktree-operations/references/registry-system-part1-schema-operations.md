# Registry System: Schema and Operations

## Table of Contents

1. [When you need to understand the registry system → Overview](#overview)
2. [If you need to find the registry file → Registry Location](#registry-location)
3. [When you need to understand registry structure → Registry Schema](#registry-schema)
   - [If you need to see a complete example → Full Schema Example](#full-schema-example)
   - [When you need to understand entry fields → Worktree Entry Fields](#worktree-entry-fields)
   - [If you need to know valid purpose types → Purpose Categories](#purpose-categories)
   - [When you need to understand status meanings → Status Values](#status-values)
   - [If you need to configure port ranges → Port Ranges Section](#port-ranges-section)
   - [When you need to understand naming templates → Naming Convention Section](#naming-convention-section)
4. [When you need to modify the registry → Registry Operations](#registry-operations)
   - [If you're adding a new worktree → Create Entry](#create-entry)
   - [When you need to change worktree state → Update Status](#update-status)
   - [If you're deleting a worktree → Remove Entry](#remove-entry)
   - [When you need to find worktrees by type → Query by Purpose](#query-by-purpose)
   - [If you need to find worktree by issue → Query by Issue](#query-by-issue)
5. [When you need validation and cleanup → Related Part](#related-part)

---

## Overview

The **registry system** is a centralized JSON database that tracks all active and historical git worktrees in a project. Its purpose is to:

- **Prevent conflicts** - Avoid duplicate worktrees, port collisions, and naming conflicts
- **Enable discovery** - Find existing worktrees by purpose, issue number, or branch
- **Track resources** - Monitor port allocations, disk usage, and worktree status
- **Automate cleanup** - Detect and remove stale or abandoned worktrees
- **Enforce conventions** - Apply consistent naming patterns across all worktrees

Without a registry, managing multiple worktrees becomes chaotic. The registry provides a single source of truth for all worktree metadata.

---

## Registry Location

The registry file is stored at:

```
design/worktrees/registry.json
```

**Path explanation:**

- `design/` - Hidden directory containing AMOA orchestrator metadata
- `worktrees/` - Subdirectory dedicated to worktree management
- `registry.json` - JSON file containing all worktree records

**Why this location:**

- Lives in the main repository (not in worktrees themselves)
- Survives worktree deletion
- Accessible from any worktree via relative path
- Excluded from git tracking via `.gitignore`

---

## Registry Schema

The registry uses a structured JSON format with multiple sections:

### Full Schema Example

```json
{
  "worktrees": [
    {
      "id": "review-GH-42",
      "path": "../review-GH-42",
      "branch": "feature/new-auth",
      "created": "2025-12-31T10:00:00Z",
      "purpose": "review",
      "issue": "GH-42",
      "port_allocations": [8080, 5432],
      "status": "active"
    },
    {
      "id": "feature-user-profiles",
      "path": "../feature-user-profiles",
      "branch": "feature/user-profiles",
      "created": "2025-12-30T14:30:00Z",
      "purpose": "feature",
      "issue": null,
      "port_allocations": [8081, 5433],
      "status": "active"
    },
    {
      "id": "bugfix-GH-88-login",
      "path": "../bugfix-GH-88-login",
      "branch": "bugfix/fix-login-timeout",
      "created": "2025-12-29T09:15:00Z",
      "purpose": "bugfix",
      "issue": "GH-88",
      "port_allocations": [8082],
      "status": "locked"
    }
  ],
  "port_ranges": {
    "web": [8080, 8099],
    "database": [5432, 5439],
    "testing": [9000, 9099]
  },
  "naming_convention": {
    "review": "../review-{issue}",
    "feature": "../feature-{name}",
    "bugfix": "../bugfix-{issue}-{desc}",
    "test": "../test-{type}-{target}"
  }
}
```

### Worktree Entry Fields

Each worktree entry contains these fields:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | string | Yes | Unique identifier for this worktree | `"review-GH-42"` |
| `path` | string | Yes | Relative path from main repo to worktree | `"../review-GH-42"` |
| `branch` | string | Yes | Git branch checked out in this worktree | `"feature/new-auth"` |
| `created` | string | Yes | ISO 8601 timestamp of creation | `"2025-12-31T10:00:00Z"` |
| `purpose` | string | Yes | Purpose category (see below) | `"review"` |
| `issue` | string\|null | No | GitHub issue number if applicable | `"GH-42"` or `null` |
| `port_allocations` | array | No | List of allocated ports | `[8080, 5432]` |
| `status` | string | Yes | Current status (see below) | `"active"` |

### Purpose Categories

The `purpose` field must be one of these values:

- **`review`** - Code review or PR testing
- **`feature`** - New feature development
- **`bugfix`** - Bug fix work
- **`test`** - Experimental testing or validation
- **`hotfix`** - Emergency production fix
- **`refactor`** - Code refactoring work

### Status Values

The `status` field indicates the worktree's current state:

| Status | Meaning | Actions Allowed |
|--------|---------|-----------------|
| `active` | Normal working state | Read, write, commit, push |
| `locked` | Temporarily locked (testing, CI running) | Read-only access |
| `pending-removal` | Marked for deletion | No modifications |

### Port Ranges Section

The `port_ranges` object defines allowed port allocations by category:

```json
{
  "port_ranges": {
    "web": [8080, 8099],
    "database": [5432, 5439],
    "testing": [9000, 9099]
  }
}
```

**How it works:**

- Each category defines a range: `[start_port, end_port]`
- When creating a worktree, the system allocates the next available port in the appropriate range
- Prevents port conflicts between worktrees

### Naming Convention Section

The `naming_convention` object defines path templates for each purpose:

```json
{
  "naming_convention": {
    "review": "../review-{issue}",
    "feature": "../feature-{name}",
    "bugfix": "../bugfix-{issue}-{desc}",
    "test": "../test-{type}-{target}"
  }
}
```

**Template variables:**

- `{issue}` - GitHub issue number (e.g., `GH-42`)
- `{name}` - Feature or branch name
- `{desc}` - Short description (kebab-case)
- `{type}` - Test type (unit, integration, e2e)
- `{target}` - What is being tested

**Example expansions:**

- `../review-{issue}` + `GH-42` → `../review-GH-42`
- `../feature-{name}` + `user-profiles` → `../feature-user-profiles`
- `../bugfix-{issue}-{desc}` + `GH-88` + `login` → `../bugfix-GH-88-login`

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

---

## Related Part

For validation rules, automatic cleanup, and troubleshooting:

- [Registry System Part 2: Validation and Cleanup](./registry-system-part2-validation-cleanup.md)
  - When you need to enforce registry rules → Validation Rules
  - If you need to check ID uniqueness → Unique IDs validation
  - When you need to validate paths → Valid Paths validation
  - If you're checking port conflicts → No Port Conflicts validation
  - When you need to clean stale entries → Automatic Cleanup
  - If you encounter registry problems → Troubleshooting

---

## Related References

- [Worktree Creation Process](./creating-worktrees.md) - How worktrees are created and registered
- [Port Allocation Strategy](./port-allocation.md) - How ports are assigned and managed
- [Naming Conventions](./worktree-naming-conventions.md) - Rules for worktree IDs and paths
