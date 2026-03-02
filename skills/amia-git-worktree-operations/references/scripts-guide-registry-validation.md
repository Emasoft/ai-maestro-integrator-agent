# Registry Validation Reference

## Table of Contents

1. [registry_validate.py](#registry_validatepy) - Validating and fixing registry
   - Purpose and usage syntax
   - Optional arguments
   - Examples with explanations
   - Validation checks performed
   - Exit codes

---

## registry_validate.py

### Purpose

Validates the integrity of the worktree registry file and optionally fixes detected inconsistencies.

### Usage Syntax

```bash
python scripts/registry_validate.py [OPTIONS]
```

### Optional Arguments

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

### Examples with Explanations

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

### Validation Checks Performed

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

### Exit Codes

- **0** - Success, registry is valid (or was fixed successfully)
- **1** - Validation failed, issues found (without --fix)
- **2** - Registry file not found or unreadable
- **3** - Registry file is corrupted beyond repair
- **4** - Fix operation failed (with --fix)
