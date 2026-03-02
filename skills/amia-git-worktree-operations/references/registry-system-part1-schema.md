# Registry System - Part 1: Schema and Location

## Table of Contents

- [Overview](#overview)
- [Registry Location](#registry-location)
- [Registry Schema](#registry-schema)
  - [Full Schema Example](#full-schema-example)
  - [Worktree Entry Fields](#worktree-entry-fields)
  - [Purpose Categories](#purpose-categories)
  - [Status Values](#status-values)
  - [Port Ranges Section](#port-ranges-section)
  - [Naming Convention Section](#naming-convention-section)

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
