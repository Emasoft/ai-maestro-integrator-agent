# Worktree Automation Scripts Guide - Part 2: Management Scripts

**Related Documents:**
- [Main Index](scripts-guide.md)
- [Part 1: Core Scripts](scripts-guide-part1-core-scripts.md)
- [Part 3: Port Scripts](scripts-guide-part3-port-scripts.md)
- [Part 4: Common Workflows](scripts-guide-part4-workflows.md)
- [Part 5: Troubleshooting](scripts-guide-part5-troubleshooting.md)

---

## Table of Contents

- [Script Reference: Management Scripts](#script-reference-management-scripts)
  - [worktree_remove.py](#worktree_removepy)
    - [Purpose](#purpose)
    - [Usage Syntax](#usage-syntax)
    - [Required Arguments](#required-arguments)
    - [Optional Arguments](#optional-arguments)
    - [Examples with Explanations](#examples-with-explanations)
    - [Safety Checks Performed (unless --force)](#safety-checks-performed-unless---force)
    - [Exit Codes](#exit-codes)
  - [registry_validate.py](#registry_validatepy)
    - [Purpose](#purpose-1)
    - [Usage Syntax](#usage-syntax-1)
    - [Optional Arguments](#optional-arguments-1)
    - [Examples with Explanations](#examples-with-explanations-1)
    - [Validation Checks Performed](#validation-checks-performed)
    - [Exit Codes](#exit-codes-1)

---

## Script Reference: Management Scripts

This section covers scripts for worktree lifecycle management:
- **worktree_remove.py** - Safely remove worktrees with cleanup
- **registry_validate.py** - Validate and fix registry inconsistencies

---

### worktree_remove.py

#### Purpose

Safely removes a git worktree and cleans up its registry entry and port allocations.

#### Usage Syntax

```bash
python scripts/worktree_remove.py <WORKTREE_NAME> [OPTIONS]
```

#### Required Arguments

- **WORKTREE_NAME** - Name of the worktree to remove
  - Must match exactly with registered name
  - Case-sensitive
  - Examples: `review-GH-42`, `feature-auth-system`

#### Optional Arguments

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

#### Examples with Explanations

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

#### Safety Checks Performed (unless --force)

1. **Uncommitted changes check** - Prevents accidental data loss
2. **Completion status check** - Warns if removing incomplete work
3. **Directory existence check** - Validates worktree still exists
4. **Registry consistency check** - Ensures registry matches filesystem
5. **Port release validation** - Confirms no services still running

#### Exit Codes

- **0** - Success, worktree removed
- **1** - Worktree name not found in registry
- **2** - User cancelled confirmation prompt
- **3** - Safety check failed (uncommitted changes without --force)
- **4** - Registry file is corrupted or unwritable
- **5** - Directory removal failed (permissions or filesystem error)

---

### registry_validate.py

#### Purpose

Validates the integrity of the worktree registry file and optionally fixes detected inconsistencies.

#### Usage Syntax

```bash
python scripts/registry_validate.py [OPTIONS]
```

#### Optional Arguments

- **--fix** - Automatically fix detected issues
  - Creates backup before modifications
  - Removes orphaned entries (registry entries with no corresponding directory)
  - Adds missing entries (worktree directories with no registry entry)
  - Releases ports allocated to non-existent worktrees
  - Resolves port conflicts (same port assigned to multiple worktrees)

- **--verbose** - Show detailed validation information
  - Displays every check performed
  - Shows file paths being validated
  - Reports metadata consistency checks
  - Useful for debugging registry corruption

#### Examples with Explanations

**Example 1: Validation only (report mode)**

```bash
python scripts/registry_validate.py
```

**Output:**
```
Worktree Registry Validation Report
====================================

Checking registry file: .claude/worktree-registry.json
✓ Registry file exists
✓ Valid JSON format
✓ Schema version: 1.0

Checking worktree entries:
✓ review-GH-42: Directory exists, ports valid
✓ feature-auth-system: Directory exists, ports valid
✗ bugfix-old-issue: Directory not found (orphaned entry)

Checking port allocations:
✓ Port 8001: Allocated to review-GH-42 (valid)
✓ Port 9001: Allocated to review-GH-42 (valid)
✗ Port 8002: Allocated to deleted-worktree (orphaned allocation)

Summary:
- Total worktrees: 3
- Valid worktrees: 2
- Orphaned entries: 1
- Port allocations: 3
- Orphaned ports: 1

Issues found: 2
Run with --fix to automatically correct these issues.
```

**When to use:** Regular maintenance check to ensure registry health.

---

**Example 2: Automatic fixing with backup**

```bash
python scripts/registry_validate.py --fix
```

**Output:**
```
Worktree Registry Validation Report
====================================

Creating backup: .claude/worktree-registry.json.backup.2024-01-15-103000

Checking and fixing issues:

Issue 1: Orphaned entry 'bugfix-old-issue'
   Action: Removing from registry
   ✓ Removed entry
   ✓ Released ports: none

Issue 2: Orphaned port allocation 8002
   Action: Releasing port
   ✓ Port 8002 released from pool

Issue 3: Missing registry entry for 'experiment-new-idea'
   Action: Creating entry from worktree directory
   ✓ Added entry with detected metadata
   ✓ Branch: experiment/new-idea
   ✓ Purpose: experiment (inferred from name)
   ✓ No ports allocated

Summary of changes:
- Entries removed: 1
- Entries added: 1
- Ports released: 1
- Backup saved: .claude/worktree-registry.json.backup.2024-01-15-103000

Registry is now consistent.
```

**When to use:** After manual filesystem operations or when validation reports issues.

---

**Example 3: Verbose validation for debugging**

```bash
python scripts/registry_validate.py --verbose
```

**Output:**
```
[VERBOSE] Loading registry from: .claude/worktree-registry.json
[VERBOSE] Registry file size: 2,345 bytes
[VERBOSE] Parsing JSON... OK
[VERBOSE] Schema version: 1.0

[VERBOSE] Validating worktree: review-GH-42
[VERBOSE]   Checking directory: /repo/worktrees/review-GH-42
[VERBOSE]   Directory exists: YES
[VERBOSE]   Checking .git file: /repo/worktrees/review-GH-42/.git
[VERBOSE]   Valid git worktree: YES
[VERBOSE]   Checking metadata:
[VERBOSE]     - purpose: review (valid)
[VERBOSE]     - identifier: GH-42 (valid)
[VERBOSE]     - branch: feature/auth (valid)
[VERBOSE]     - created_at: 2024-01-15T10:30:00 (valid ISO format)
[VERBOSE]     - completed: false (valid boolean)
[VERBOSE]   Checking port allocations:
[VERBOSE]     - web: 8001 (in valid range, not conflicted)
[VERBOSE]     - api: 9001 (in valid range, not conflicted)
[VERBOSE]   Result: VALID

[VERBOSE] Validating port allocations:
[VERBOSE]   Port 8001:
[VERBOSE]     - Allocated to: review-GH-42
[VERBOSE]     - Worktree exists: YES
[VERBOSE]     - Result: VALID

[Complete verbose output continues for all entries...]
```

**When to use:** Investigating registry corruption or unexpected behavior.

---

**Example 4: Fix with verbose output**

```bash
python scripts/registry_validate.py --fix --verbose
```

**Output:**
```
[VERBOSE] Creating backup...
[VERBOSE]   Source: .claude/worktree-registry.json
[VERBOSE]   Destination: .claude/worktree-registry.json.backup.2024-01-15-103000
[VERBOSE]   Backup created: 2,345 bytes copied

[VERBOSE] Scanning for issues...
[VERBOSE] Found orphaned entry: bugfix-old-issue
[VERBOSE]   Directory checked: /repo/worktrees/bugfix-old-issue
[VERBOSE]   Directory exists: NO
[VERBOSE]   Action: Mark for removal

[VERBOSE] Applying fixes...
[VERBOSE]   Removing entry: bugfix-old-issue
[VERBOSE]   Checking for allocated ports...
[VERBOSE]   No ports to release
[VERBOSE]   Entry removed

[VERBOSE] Writing updated registry...
[VERBOSE]   Writing to: .claude/worktree-registry.json
[VERBOSE]   Bytes written: 2,123
[VERBOSE]   Write successful

[Complete verbose output continues...]
```

**When to use:** Debugging fix operations that don't work as expected.

---

#### Validation Checks Performed

1. **Registry file existence and format**
   - File exists at `.claude/worktree-registry.json`
   - Valid JSON syntax
   - Correct schema structure

2. **Worktree entry validation**
   - Directory exists at registered path
   - Directory is a valid git worktree
   - All required metadata fields present
   - Metadata values are valid types and formats

3. **Port allocation validation**
   - Ports are in valid ranges
   - No duplicate port allocations
   - All allocated ports have corresponding worktrees
   - Worktrees reference correct ports

4. **Cross-reference validation**
   - Every worktree directory has a registry entry
   - Every registry entry has a corresponding directory
   - Port allocations match worktree entries

5. **Metadata consistency**
   - Timestamps are valid ISO 8601 format
   - Purpose values are from allowed set
   - Completed status is boolean
   - Identifiers are non-empty strings

#### Exit Codes

- **0** - Success, registry is valid (or was fixed successfully)
- **1** - Validation failed, issues found (without --fix)
- **2** - Registry file not found or unreadable
- **3** - Registry file is corrupted beyond repair
- **4** - Fix operation failed (with --fix)

---

**End of Part 2: Management Scripts**

**Next:** [Part 3: Port Scripts](scripts-guide-part3-port-scripts.md) - Port allocation and status scripts
