# Worktree Automation Scripts Guide - Part 1: Core Scripts

**Related Documents:**
- [Main Index](scripts-guide.md)
- [Part 2: Management Scripts](scripts-guide-part2-management-scripts.md)
- [Part 3: Port Scripts](scripts-guide-part3-port-scripts.md)
- [Part 4: Common Workflows](scripts-guide-part4-workflows.md)
- [Part 5: Troubleshooting](scripts-guide-part5-troubleshooting.md)

---

## Table of Contents

- [Script Reference: Core Scripts](#script-reference-core-scripts)
  - [worktree_create.py](#worktree_createpy)
    - [Purpose](#purpose)
    - [Usage Syntax](#usage-syntax)
    - [Required Arguments](#required-arguments)
    - [Optional Arguments](#optional-arguments)
    - [Examples with Explanations](#examples-with-explanations)
    - [Exit Codes](#exit-codes)
  - [worktree_list.py](#worktree_listpy)
    - [Purpose](#purpose-1)
    - [Usage Syntax](#usage-syntax-1)
    - [Optional Arguments](#optional-arguments-1)
    - [Examples with Explanations](#examples-with-explanations-1)
    - [Exit Codes](#exit-codes-1)

---

## Script Reference: Core Scripts

This section covers the two most frequently used scripts:
- **worktree_create.py** - Create new worktrees with registration and port allocation
- **worktree_list.py** - List and filter existing worktrees

---

### worktree_create.py

#### Purpose

Creates a new git worktree with automatic registry registration and optional port allocation.

#### Usage Syntax

```bash
python scripts/worktree_create.py --purpose <PURPOSE> --identifier <ID> --branch <BRANCH> [OPTIONS]
```

#### Required Arguments

- **--purpose** - The reason for creating this worktree. Valid values:
  - `review` - Code review or PR testing
  - `feature` - New feature development
  - `bugfix` - Bug fix work
  - `hotfix` - Emergency production fix
  - `experiment` - Experimental/research work
  - `refactor` - Code refactoring
  - `docs` - Documentation updates

- **--identifier** - Unique identifier for this worktree. Examples:
  - GitHub issue: `GH-42`
  - Jira ticket: `PROJ-123`
  - Feature name: `auth-system`
  - CVE number: `CVE-2024-001`

- **--branch** - Git branch to checkout in this worktree. Can be:
  - Existing branch: `feature/authentication`
  - New branch: `bugfix/memory-leak` (will be created)
  - Tag: `v1.2.3`
  - Commit SHA: `abc123def456`

#### Optional Arguments

- **--ports** - Automatically allocate development server ports
  - Default services: web (8000-8099), api (9000-9099), db (5432-5532)
  - Ports are guaranteed unique across all active worktrees

#### Examples with Explanations

**Example 1: Create review worktree for GitHub PR**

```bash
python scripts/worktree_create.py --purpose review --identifier GH-42 --branch feature/auth
```

**What this does:**
1. Creates directory: `worktrees/review-GH-42/`
2. Checks out branch: `feature/auth`
3. Creates registry entry with purpose `review`, identifier `GH-42`
4. Sets completion status to `false`

**When to use:** You need to review someone's pull request without disrupting your current work.

---

**Example 2: Create feature worktree with port allocation**

```bash
python scripts/worktree_create.py --purpose feature --identifier auth-system --branch feature/authentication --ports
```

**What this does:**
1. Creates directory: `worktrees/feature-auth-system/`
2. Checks out branch: `feature/authentication`
3. Allocates ports automatically:
   - Web server: 8001 (if 8000 already taken)
   - API server: 9001
   - Database: 5433
4. Registers ports in registry under this worktree

**When to use:** Starting new feature development that requires running multiple services simultaneously.

---

**Example 3: Create hotfix worktree from production tag**

```bash
python scripts/worktree_create.py --purpose hotfix --identifier CVE-2024-001 --branch v2.1.3
```

**What this does:**
1. Creates directory: `worktrees/hotfix-CVE-2024-001/`
2. Checks out tag: `v2.1.3` (detached HEAD state)
3. Registers as hotfix purpose
4. Marks as urgent in metadata

**When to use:** Emergency security patch needed on production version.

---

**Example 4: Create experiment worktree for research**

```bash
python scripts/worktree_create.py --purpose experiment --identifier async-rewrite --branch experiment/async-refactor
```

**What this does:**
1. Creates directory: `worktrees/experiment-async-rewrite/`
2. Creates new branch: `experiment/async-refactor` (if doesn't exist)
3. Marks as experimental in registry
4. No port allocation (typically not needed for experiments)

**When to use:** Testing architectural changes without affecting main codebase.

---

#### Exit Codes

- **0** - Success, worktree created and registered
- **1** - Invalid arguments or missing required parameters
- **2** - Worktree with same name already exists
- **3** - Branch does not exist and could not be created
- **4** - Registry file is corrupted or unwritable
- **5** - Insufficient available ports for allocation

---

### worktree_list.py

#### Purpose

Lists all registered worktrees with filtering, sorting, and status information.

#### Usage Syntax

```bash
python scripts/worktree_list.py [OPTIONS]
```

#### Optional Arguments

- **--purpose** - Filter by purpose type
  - Values: `review`, `feature`, `bugfix`, `hotfix`, `experiment`, `refactor`, `docs`
  - Example: `--purpose review` shows only review worktrees

- **--status** - Filter by completion status
  - Values: `active`, `completed`, `all`
  - `active` - Only worktrees with `completed: false`
  - `completed` - Only worktrees with `completed: true`
  - `all` - Show all worktrees regardless of status
  - Default: `active`

- **--ports** - Show only worktrees with allocated ports
  - No value needed, presence of flag enables filter
  - Useful for finding worktrees running services

- **--json** - Output in JSON format instead of human-readable table
  - Useful for scripting and automation
  - Outputs valid JSON to stdout

- **--validate** - Check if each worktree directory still exists
  - Reports orphaned registry entries (directory deleted but registry not updated)
  - Does not modify registry, only reports issues

#### Examples with Explanations

**Example 1: List all active worktrees (default)**

```bash
python scripts/worktree_list.py
```

**Output:**
```
┌─────────────────────────┬─────────────────────────────┬─────────┬────────────┬───────────┐
│ Name                    │ Path                        │ Branch  │ Purpose    │ Completed │
├─────────────────────────┼─────────────────────────────┼─────────┼────────────┼───────────┤
│ review-GH-42            │ /repo/worktrees/review-GH-42│ feat/au │ review     │ No        │
│ feature-auth-system     │ /repo/worktrees/feature-aut │ feat/au │ feature    │ No        │
│ bugfix-memory-leak      │ /repo/worktrees/bugfix-memo │ bugfix/ │ bugfix     │ No        │
└─────────────────────────┴─────────────────────────────┴─────────┴────────────┴───────────┘
```

**When to use:** Quick overview of all ongoing work.

---

**Example 2: Find all review worktrees**

```bash
python scripts/worktree_list.py --purpose review
```

**Output:**
```
┌─────────────────────────┬─────────────────────────────┬─────────┬─────────┬───────────┐
│ Name                    │ Path                        │ Branch  │ Purpose │ Completed │
├─────────────────────────┼─────────────────────────────┼─────────┼─────────┼───────────┤
│ review-GH-42            │ /repo/worktrees/review-GH-42│ feat/au │ review  │ No        │
│ review-GH-87            │ /repo/worktrees/review-GH-87│ bugfix/ │ review  │ No        │
└─────────────────────────┴─────────────────────────────┴─────────┴─────────┴───────────┘
```

**When to use:** Finding worktrees created for code review purposes only.

---

**Example 3: List worktrees with allocated ports**

```bash
python scripts/worktree_list.py --ports
```

**Output:**
```
┌─────────────────────────┬─────────┬──────────────────┬───────────┐
│ Name                    │ Purpose │ Allocated Ports  │ Completed │
├─────────────────────────┼─────────┼──────────────────┼───────────┤
│ feature-auth-system     │ feature │ web:8001         │ No        │
│                         │         │ api:9001         │           │
│ review-GH-42            │ review  │ web:8002         │ No        │
└─────────────────────────┴─────────┴──────────────────┴───────────┘
```

**When to use:** Identifying which worktrees have running services and their ports.

---

**Example 4: JSON output for scripting**

```bash
python scripts/worktree_list.py --status active --json
```

**Output:**
```json
[
  {
    "name": "review-GH-42",
    "path": "/repo/worktrees/review-GH-42",
    "branch": "feature/auth",
    "purpose": "review",
    "identifier": "GH-42",
    "completed": false,
    "created_at": "2024-01-15T10:30:00",
    "ports": {
      "web": 8001,
      "api": 9001
    }
  }
]
```

**When to use:** Integrating worktree data into other automation scripts or dashboards.

---

**Example 5: Validate worktree directories exist**

```bash
python scripts/worktree_list.py --validate
```

**Output:**
```
✓ review-GH-42: Directory exists
✓ feature-auth-system: Directory exists
✗ bugfix-old-issue: Directory not found (orphaned registry entry)

Summary: 2 valid, 1 orphaned
```

**When to use:** After disk cleanup or before running registry validation to check for stale entries.

---

#### Exit Codes

- **0** - Success, list displayed
- **1** - Invalid filter arguments
- **2** - Registry file not found or unreadable
- **3** - Validation found orphaned entries (with --validate flag)

---

**End of Part 1: Core Scripts**

**Next:** [Part 2: Management Scripts](scripts-guide-part2-management-scripts.md) - Removal and validation scripts
