---
name: op-verify-worktree-isolation
description: "Check for isolation violations in a git worktree"
procedure: support-skill
workflow-instruction: support
---

# Operation: Verify Worktree Isolation


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify paths](#step-1-identify-paths)
  - [Step 2: Check main repo for unexpected changes](#step-2-check-main-repo-for-unexpected-changes)
  - [Step 3: Check for files modified in both locations](#step-3-check-for-files-modified-in-both-locations)
  - [Step 4: Check for files outside worktree](#step-4-check-for-files-outside-worktree)
  - [Step 5: Verify worktree integrity](#step-5-verify-worktree-integrity)
  - [Step 6: Generate isolation report](#step-6-generate-isolation-report)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Isolation Violations](#isolation-violations)
- [Error Handling](#error-handling)
  - [Worktree path doesn't exist](#worktree-path-doesnt-exist)
  - [Cannot determine main repo](#cannot-determine-main-repo)
  - [Conflicts detected](#conflicts-detected)
- [Complete Verification Script](#complete-verification-script)
- [Verification](#verification)

## Purpose

Verify that all file operations have remained within the designated worktree boundaries, detecting any isolation violations that could cause merge conflicts or data corruption.

## When to Use

- Periodically during worktree work
- Before committing changes
- Before cleaning up a worktree
- When suspicious of accidental writes outside worktree

## Prerequisites

1. Worktree path is known
2. Main repository path is known
3. Access to both directories

## Procedure

### Step 1: Identify paths

```bash
WORKTREE_PATH="/tmp/worktrees/pr-123"
MAIN_REPO=$(git -C "$WORKTREE_PATH" worktree list | head -1 | awk '{print $1}')

echo "Worktree: $WORKTREE_PATH"
echo "Main repo: $MAIN_REPO"
```

### Step 2: Check main repo for unexpected changes

```bash
# Go to main repo
cd "$MAIN_REPO"

# Check for uncommitted changes
MAIN_STATUS=$(git status --porcelain)

if [ -n "$MAIN_STATUS" ]; then
  echo "WARNING: Main repo has uncommitted changes:"
  echo "$MAIN_STATUS"
  ISOLATION_VIOLATION=true
else
  echo "Main repo is clean"
  ISOLATION_VIOLATION=false
fi
```

### Step 3: Check for files modified in both locations

```bash
# Get modified files in worktree
cd "$WORKTREE_PATH"
WT_MODIFIED=$(git status --porcelain | awk '{print $2}')

# Check if any of these exist as modified in main
cd "$MAIN_REPO"
for file in $WT_MODIFIED; do
  if git status --porcelain "$file" 2>/dev/null | grep -q .; then
    echo "CONFLICT: $file modified in both worktree and main"
    ISOLATION_VIOLATION=true
  fi
done
```

### Step 4: Check for files outside worktree

```bash
# Check if any recent file operations touched main repo
# This requires tracking (audit log or inotify)

# Alternative: Check mtime of files in main repo
cd "$MAIN_REPO"
RECENT_MAIN=$(find . -type f -mmin -60 -not -path "./.git/*" 2>/dev/null)

if [ -n "$RECENT_MAIN" ]; then
  echo "Recently modified in main repo:"
  echo "$RECENT_MAIN"
fi
```

### Step 5: Verify worktree integrity

```bash
cd "$WORKTREE_PATH"

# Check .git file points to correct location
if [ -f ".git" ]; then
  GIT_DIR=$(cat .git | grep gitdir | cut -d: -f2 | tr -d ' ')
  echo ".git points to: $GIT_DIR"

  if [ -d "$GIT_DIR" ]; then
    echo "Git directory exists: OK"
  else
    echo "ERROR: Git directory missing"
    ISOLATION_VIOLATION=true
  fi
else
  echo "ERROR: .git file missing - not a valid worktree"
  ISOLATION_VIOLATION=true
fi
```

### Step 6: Generate isolation report

```bash
if [ "$ISOLATION_VIOLATION" = true ]; then
  RESULT="VIOLATION_DETECTED"
else
  RESULT="ISOLATED"
fi

cat << EOF
{
  "worktree_path": "$WORKTREE_PATH",
  "main_repo": "$MAIN_REPO",
  "isolation_status": "$RESULT",
  "main_repo_clean": $([ -z "$MAIN_STATUS" ] && echo true || echo false),
  "conflicts_found": $([ "$ISOLATION_VIOLATION" = true ] && echo true || echo false)
}
EOF
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| worktree_path | string | yes | Path to worktree to verify |
| main_repo | string | no | Path to main repo (auto-detected if not provided) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| worktree_path | string | Verified worktree path |
| main_repo | string | Main repository path |
| isolation_status | string | ISOLATED or VIOLATION_DETECTED |
| main_repo_clean | boolean | Whether main repo has no changes |
| conflicts_found | boolean | Whether file conflicts were detected |
| violations | string[] | List of specific violations |

## Example Output

```json
{
  "worktree_path": "/tmp/worktrees/pr-123",
  "main_repo": "/Users/dev/project",
  "isolation_status": "ISOLATED",
  "main_repo_clean": true,
  "conflicts_found": false,
  "violations": []
}
```

## Isolation Violations

| Type | Description | Severity |
|------|-------------|----------|
| Main repo modified | Files changed in main repo during worktree work | High |
| File conflict | Same file modified in both locations | Critical |
| Worktree corruption | .git file missing or invalid | Critical |
| External writes | Files written outside worktree | High |

## Error Handling

### Worktree path doesn't exist

**Cause**: Worktree was deleted or path is wrong.

**Solution**: Verify path, check if worktree was removed.

### Cannot determine main repo

**Cause**: Worktree not properly linked.

**Solution**: Check worktree integrity, may need to recreate.

### Conflicts detected

**Cause**: Files modified in multiple locations.

**Solution**: Determine which changes are correct, resolve manually.

## Complete Verification Script

```bash
#!/bin/bash
# verify_worktree_isolation.sh

WORKTREE_PATH="$1"

if [ -z "$WORKTREE_PATH" ]; then
  echo "Usage: verify_worktree_isolation.sh <worktree_path>"
  exit 1
fi

echo "=== Worktree Isolation Verification ==="
echo "Worktree: $WORKTREE_PATH"

# Verify worktree exists
if [ ! -d "$WORKTREE_PATH" ]; then
  echo "ERROR: Worktree path doesn't exist"
  exit 1
fi

# Get main repo
MAIN_REPO=$(git -C "$WORKTREE_PATH" worktree list | head -1 | awk '{print $1}')
echo "Main repo: $MAIN_REPO"

VIOLATIONS=()

# Check main repo status
cd "$MAIN_REPO"
MAIN_STATUS=$(git status --porcelain)
if [ -n "$MAIN_STATUS" ]; then
  echo "WARNING: Main repo has changes"
  VIOLATIONS+=("Main repo has uncommitted changes")
fi

# Check worktree .git
if [ ! -f "$WORKTREE_PATH/.git" ]; then
  echo "ERROR: Invalid worktree structure"
  VIOLATIONS+=("Missing .git file")
fi

# Summary
echo ""
if [ ${#VIOLATIONS[@]} -eq 0 ]; then
  echo "STATUS: ISOLATED"
  echo "No isolation violations detected"
  exit 0
else
  echo "STATUS: VIOLATION_DETECTED"
  echo "Violations found:"
  for v in "${VIOLATIONS[@]}"; do
    echo "  - $v"
  done
  exit 1
fi
```

## Verification

Run verification before critical operations:

```bash
# Before commit
./verify_worktree_isolation.sh /tmp/worktrees/pr-123 && git commit

# Before push
./verify_worktree_isolation.sh /tmp/worktrees/pr-123 && git push

# Before cleanup
./verify_worktree_isolation.sh /tmp/worktrees/pr-123 && git worktree remove /tmp/worktrees/pr-123
```
