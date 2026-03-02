---
name: op-check-concurrent-git-ops
description: "Check if other git operations are currently running"
procedure: support-skill
workflow-instruction: support
---

# Operation: Check Concurrent Git Operations


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Find git directory](#step-1-find-git-directory)
  - [Step 2: Check main repository locks](#step-2-check-main-repository-locks)
  - [Step 3: Check worktree locks](#step-3-check-worktree-locks)
  - [Step 4: Check for running git processes](#step-4-check-for-running-git-processes)
  - [Step 5: Check lock file age](#step-5-check-lock-file-age)
  - [Step 6: Generate status report](#step-6-generate-status-report)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Lock File Types](#lock-file-types)
- [Handling Stale Locks](#handling-stale-locks)
- [Error Handling](#error-handling)
  - [Lock file present](#lock-file-present)
  - [Stale lock](#stale-lock)
  - [Git process hung](#git-process-hung)
- [Complete Check Script](#complete-check-script)
- [Verification](#verification)

## Purpose

Verify that no other git operations are currently running before starting a new git operation, preventing deadlocks and corruption.

## When to Use

- Before any worktree operation (create, remove)
- Before commit/push operations
- Before fetch/pull operations
- When experiencing git hangs or errors

## Prerequisites

1. Access to repository git directory
2. Access to worktree git directories (if any)

## Procedure

### Step 1: Find git directory

```bash
# Get main git directory
GIT_DIR=$(git rev-parse --git-dir)
REPO_ROOT=$(git rev-parse --show-toplevel)

echo "Git directory: $GIT_DIR"
echo "Repository: $REPO_ROOT"
```

### Step 2: Check main repository locks

```bash
LOCKS_FOUND=()

# Check common lock files
LOCK_FILES=(
  "$GIT_DIR/index.lock"
  "$GIT_DIR/HEAD.lock"
  "$GIT_DIR/config.lock"
  "$GIT_DIR/refs/heads/*.lock"
  "$GIT_DIR/shallow.lock"
  "$GIT_DIR/packed-refs.lock"
)

for pattern in "${LOCK_FILES[@]}"; do
  for lock in $pattern; do
    if [ -f "$lock" ]; then
      LOCKS_FOUND+=("$lock")
      echo "LOCK FOUND: $lock"
    fi
  done
done
```

### Step 3: Check worktree locks

```bash
# Get all worktrees
WORKTREES=$(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2)

for wt in $WORKTREES; do
  if [ -f "$wt/.git" ]; then
    # Worktree .git is a file pointing to git dir
    WT_GIT_DIR=$(cat "$wt/.git" | grep gitdir | cut -d: -f2 | tr -d ' ')
  else
    WT_GIT_DIR="$wt/.git"
  fi

  if [ -f "$WT_GIT_DIR/index.lock" ]; then
    LOCKS_FOUND+=("$WT_GIT_DIR/index.lock")
    echo "WORKTREE LOCK: $wt"
  fi
done
```

### Step 4: Check for running git processes

```bash
# Check for git processes
GIT_PROCS=$(ps aux | grep -E "[g]it (fetch|push|pull|commit|merge|rebase|checkout)" | grep -v grep)

if [ -n "$GIT_PROCS" ]; then
  echo "Running git processes found:"
  echo "$GIT_PROCS"
  CONCURRENT_OPS=true
else
  echo "No running git processes"
  CONCURRENT_OPS=false
fi
```

### Step 5: Check lock file age

```bash
# Stale locks (older than 1 hour) may be orphaned
for lock in "${LOCKS_FOUND[@]}"; do
  if [ -f "$lock" ]; then
    # Get file age in minutes
    if [[ "$OSTYPE" == "darwin"* ]]; then
      AGE_MINS=$(( ($(date +%s) - $(stat -f %m "$lock")) / 60 ))
    else
      AGE_MINS=$(( ($(date +%s) - $(stat -c %Y "$lock")) / 60 ))
    fi

    if [ $AGE_MINS -gt 60 ]; then
      echo "STALE LOCK (${AGE_MINS}m old): $lock"
    else
      echo "ACTIVE LOCK (${AGE_MINS}m old): $lock"
    fi
  fi
done
```

### Step 6: Generate status report

```bash
if [ ${#LOCKS_FOUND[@]} -eq 0 ] && [ "$CONCURRENT_OPS" = "false" ]; then
  STATUS="clear"
  echo ""
  echo "STATUS: CLEAR - No concurrent operations"
else
  STATUS="blocked"
  echo ""
  echo "STATUS: BLOCKED - Concurrent operations detected"
fi

cat << EOF
{
  "status": "$STATUS",
  "locks_found": ${#LOCKS_FOUND[@]},
  "git_processes": $CONCURRENT_OPS,
  "lock_files": $(printf '%s\n' "${LOCKS_FOUND[@]}" | jq -R . | jq -s .)
}
EOF
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| repo_path | string | no | Path to repository (default: current directory) |
| check_worktrees | boolean | no | Whether to check worktree locks (default: true) |
| check_processes | boolean | no | Whether to check running processes (default: true) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| status | string | clear or blocked |
| locks_found | number | Number of lock files found |
| git_processes | boolean | Whether git processes are running |
| lock_files | string[] | List of lock file paths |
| stale_locks | string[] | Lock files older than 1 hour |

## Example Output

```json
{
  "status": "clear",
  "locks_found": 0,
  "git_processes": false,
  "lock_files": [],
  "stale_locks": []
}
```

## Lock File Types

| Lock File | Operation |
|-----------|-----------|
| index.lock | add, commit, checkout, merge |
| HEAD.lock | checkout, reset |
| config.lock | config changes |
| refs/heads/*.lock | branch operations |
| shallow.lock | shallow clone operations |
| packed-refs.lock | gc, pack-refs |

## Handling Stale Locks

If a lock is stale (> 1 hour old and no git process):

```bash
# CAUTION: Only remove if certain no operation is running
rm "$GIT_DIR/index.lock"
```

**Warning**: Removing an active lock can corrupt the repository.

## Error Handling

### Lock file present

**Cause**: Another git operation is running.

**Solution**: Wait for operation to complete or investigate.

### Stale lock

**Cause**: Previous operation crashed without cleanup.

**Solution**: Remove lock after verifying no operation is running.

### Git process hung

**Cause**: Git operation is stuck.

**Solution**: Investigate process, kill if necessary.

## Complete Check Script

```bash
#!/bin/bash
# check_concurrent_git_ops.sh

REPO_PATH="${1:-.}"

echo "=== Checking for Concurrent Git Operations ==="

cd "$REPO_PATH"
GIT_DIR=$(git rev-parse --git-dir)

BLOCKED=false
LOCKS=()

# Check lock files
for lock in "$GIT_DIR/index.lock" "$GIT_DIR/HEAD.lock" "$GIT_DIR/config.lock"; do
  if [ -f "$lock" ]; then
    BLOCKED=true
    LOCKS+=("$lock")
    echo "LOCK: $lock"
  fi
done

# Check worktrees
for wt in $(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do
  if [ -f "$wt/.git" ]; then
    WT_GIT=$(cat "$wt/.git" | grep gitdir | cut -d: -f2 | tr -d ' ')
    if [ -f "$WT_GIT/index.lock" ]; then
      BLOCKED=true
      LOCKS+=("$WT_GIT/index.lock")
      echo "WORKTREE LOCK: $wt"
    fi
  fi
done

# Check processes
GIT_PROCS=$(pgrep -a git 2>/dev/null | grep -v "check_concurrent")
if [ -n "$GIT_PROCS" ]; then
  BLOCKED=true
  echo "RUNNING: git processes detected"
fi

echo ""
if [ "$BLOCKED" = "true" ]; then
  echo "STATUS: BLOCKED"
  echo "Cannot proceed - concurrent operations detected"
  exit 1
else
  echo "STATUS: CLEAR"
  echo "No concurrent operations - safe to proceed"
  exit 0
fi
```

## Verification

Use before git operations:

```bash
# Check before creating worktree
./check_concurrent_git_ops.sh && git worktree add /tmp/pr-123 pr-123

# Check before commit
./check_concurrent_git_ops.sh && git commit -m "message"

# Check before push
./check_concurrent_git_ops.sh && git push origin branch
```
