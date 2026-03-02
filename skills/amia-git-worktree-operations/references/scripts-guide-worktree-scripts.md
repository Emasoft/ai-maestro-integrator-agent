# Worktree Scripts Reference

## Table of Contents

1. [worktree_create.py](#worktree_createpy) - Creating new worktrees
   - Purpose and usage syntax
   - Required and optional arguments
   - Examples with explanations
   - Exit codes
2. [worktree_list.py](#worktree_listpy) - Listing and filtering worktrees
   - Purpose and usage syntax
   - Filter options
   - Examples with explanations
   - Exit codes
3. [worktree_remove.py](#worktree_removepy) - Safely removing worktrees
   - Purpose and usage syntax
   - Safety checks
   - Examples with explanations
   - Exit codes

---

## worktree_create.py

### Purpose

Creates a new git worktree with automatic registry registration and optional port allocation.

### Usage Syntax

```bash
python scripts/worktree_create.py --purpose <PURPOSE> --identifier <ID> --branch <BRANCH> [OPTIONS]
```

### Required Arguments

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

### Optional Arguments

- **--ports** - Automatically allocate development server ports
  - Default services: web (8000-8099), api (9000-9099), db (5432-5532)
  - Ports are guaranteed unique across all active worktrees

### Examples with Explanations

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

### Exit Codes

- **0** - Success, worktree created and registered
- **1** - Invalid arguments or missing required parameters
- **2** - Worktree with same name already exists
- **3** - Branch does not exist and could not be created
- **4** - Registry file is corrupted or unwritable
- **5** - Insufficient available ports for allocation

---

## worktree_list.py

### Purpose

Lists all registered worktrees with filtering, sorting, and status information.

### Usage Syntax

```bash
python scripts/worktree_list.py [OPTIONS]
```

### Optional Arguments

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

### Examples with Explanations

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

### Exit Codes

- **0** - Success, list displayed
- **1** - Invalid filter arguments
- **2** - Registry file not found or unreadable
- **3** - Validation found orphaned entries (with --validate flag)

---

## worktree_remove.py

### Purpose

Safely removes a git worktree and cleans up its registry entry and port allocations.

### Usage Syntax

```bash
python scripts/worktree_remove.py <WORKTREE_NAME> [OPTIONS]
```

### Required Arguments

- **WORKTREE_NAME** - Name of the worktree to remove
  - Must match exactly with registered name
  - Case-sensitive
  - Examples: `review-GH-42`, `feature-auth-system`

### Optional Arguments

- **--force** - Skip safety checks and confirmations
  - Removes worktree even if it has uncommitted changes
  - Removes worktree even if marked as incomplete
  - Use with extreme caution

- **--dry-run** - Show what would be removed without actually removing
  - Displays planned actions
  - Does not modify filesystem or registry
  - Useful for verification before destructive operations

- **--all-completed** - Remove all worktrees marked as completed
  - Batch operation
  - Requires confirmation unless --force is also specified
  - Releases all ports from removed worktrees

### Examples with Explanations

**Example 1: Safe removal with confirmation**

```bash
python scripts/worktree_remove.py review-GH-42
```

**Interaction:**
```
Worktree: review-GH-42
Path: /repo/worktrees/review-GH-42
Branch: feature/auth
Status: Active (not marked as completed)
Allocated ports: web:8001, api:9001

Checks:
✓ No uncommitted changes
✗ Not marked as completed

Warning: This worktree is not marked as completed.
Are you sure you want to remove it? [y/N]:
```

**What happens when you type 'y':**
1. Removes directory: `/repo/worktrees/review-GH-42/`
2. Deletes registry entry for `review-GH-42`
3. Releases ports 8001 and 9001 back to the pool
4. Updates `git worktree list` internal tracking

**When to use:** Standard cleanup after finishing work on a branch.

---

**Example 2: Force removal without confirmation**

```bash
python scripts/worktree_remove.py feature-broken-experiment --force
```

**What this does:**
1. Skips all safety checks
2. Removes worktree immediately without prompts
3. Cleans up registry and ports
4. Does not validate completion status or uncommitted changes

**When to use:** Removing abandoned experiments or broken worktrees that cannot be committed.

**Warning:** Uncommitted work will be permanently lost.

---

**Example 3: Dry run to preview removal**

```bash
python scripts/worktree_remove.py review-GH-42 --dry-run
```

**Output:**
```
[DRY RUN] Would perform these actions:

1. Remove directory: /repo/worktrees/review-GH-42/
   - Size: 45 MB
   - Files: 1,234

2. Delete registry entry: review-GH-42
   - Purpose: review
   - Identifier: GH-42

3. Release ports:
   - web: 8001
   - api: 9001

4. Update git worktree list

No changes were made (dry run mode).
```

**When to use:** Verifying what will be removed before actually removing it.

---

**Example 4: Batch remove all completed worktrees**

```bash
python scripts/worktree_remove.py --all-completed
```

**Interaction:**
```
Found 3 completed worktrees:
- review-GH-42 (completed 2 days ago)
- bugfix-memory-leak (completed 5 days ago)
- feature-old-api (completed 14 days ago)

This will remove 3 worktrees and release 6 ports.
Continue? [y/N]:
```

**What happens when you type 'y':**
1. Removes all three worktree directories
2. Deletes all three registry entries
3. Releases all six allocated ports
4. Displays summary of removed worktrees

**When to use:** Periodic cleanup of finished work.

---

**Example 5: Batch force remove (no confirmation)**

```bash
python scripts/worktree_remove.py --all-completed --force
```

**What this does:**
1. Finds all worktrees with `completed: true`
2. Removes them immediately without any prompts
3. Displays summary of removed worktrees

**When to use:** Automated cleanup scripts or CI/CD cleanup stages.

---

### Safety Checks Performed (unless --force)

1. **Uncommitted changes check** - Prevents accidental data loss
2. **Completion status check** - Warns if removing incomplete work
3. **Directory existence check** - Validates worktree still exists
4. **Registry consistency check** - Ensures registry matches filesystem
5. **Port release validation** - Confirms no services still running

### Exit Codes

- **0** - Success, worktree removed
- **1** - Worktree name not found in registry
- **2** - User cancelled confirmation prompt
- **3** - Safety check failed (uncommitted changes without --force)
- **4** - Registry file is corrupted or unwritable
- **5** - Directory removal failed (permissions or filesystem error)
