---
name: op-worktree-commit-push
description: "Commit and push changes from within a git worktree"
procedure: support-skill
workflow-instruction: support
---

# Operation: Worktree Commit Push


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Navigate to worktree](#step-1-navigate-to-worktree)
  - [Step 2: Verify no concurrent operations](#step-2-verify-no-concurrent-operations)
  - [Step 3: Check for changes to commit](#step-3-check-for-changes-to-commit)
  - [Step 4: Stage changes](#step-4-stage-changes)
  - [Step 5: Commit changes](#step-5-commit-changes)
  - [Step 6: Push to remote](#step-6-push-to-remote)
  - [Step 7: Verify push success](#step-7-verify-push-success)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Commit Message Format](#commit-message-format)
- [Error Handling](#error-handling)
  - [Nothing to commit](#nothing-to-commit)
  - [Push rejected](#push-rejected)
  - [Commit message empty](#commit-message-empty)
  - [Lock file present](#lock-file-present)
- [Complete Commit/Push Script](#complete-commitpush-script)
- [Verification](#verification)

## Purpose

Safely commit changes and push to remote from within a git worktree, ensuring no concurrent git operations and proper isolation.

## When to Use

- After making changes in a worktree
- When ready to update the PR with changes
- Before cleaning up a worktree

## Prerequisites

1. Worktree path is known
2. Changes have been made and are ready to commit
3. No other git operations are running
4. Push access to remote repository

## Procedure

### Step 1: Navigate to worktree

```bash
WORKTREE_PATH="/tmp/worktrees/pr-123"

if [ ! -d "$WORKTREE_PATH" ]; then
  echo "ERROR: Worktree not found at $WORKTREE_PATH"
  exit 1
fi

cd "$WORKTREE_PATH"
echo "Working in: $(pwd)"
```

### Step 2: Verify no concurrent operations

```bash
# Check for lock files in worktree
if [ -f ".git/index.lock" ] || [ -f "$(cat .git | grep gitdir | cut -d: -f2 | tr -d ' ')/index.lock" ]; then
  echo "ERROR: Git is locked - another operation is running"
  exit 1
fi

# Check main repo for locks
MAIN_REPO=$(git worktree list | head -1 | awk '{print $1}')
if [ -f "$MAIN_REPO/.git/index.lock" ]; then
  echo "ERROR: Main repo is locked"
  exit 1
fi

echo "No concurrent git operations detected"
```

### Step 3: Check for changes to commit

```bash
# Check status
git status --porcelain

if [ -z "$(git status --porcelain)" ]; then
  echo "No changes to commit"
  exit 0
fi

# Show what will be committed
echo "Changes to commit:"
git status --short
```

### Step 4: Stage changes

```bash
# Stage all changes
git add -A

# Or stage specific files
# git add file1.py file2.py

echo "Staged changes:"
git diff --cached --stat
```

### Step 5: Commit changes

```bash
COMMIT_MSG="$1"

if [ -z "$COMMIT_MSG" ]; then
  echo "ERROR: Commit message required"
  exit 1
fi

# Commit
git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
  COMMIT_SHA=$(git rev-parse --short HEAD)
  echo "Committed: $COMMIT_SHA"
else
  echo "ERROR: Commit failed"
  exit 1
fi
```

### Step 6: Push to remote

```bash
# Get current branch
BRANCH=$(git branch --show-current)

# Push to origin
git push origin "$BRANCH"

if [ $? -eq 0 ]; then
  echo "Pushed to origin/$BRANCH"
else
  echo "ERROR: Push failed"

  # Check if branch needs to be set upstream
  if git push --set-upstream origin "$BRANCH"; then
    echo "Set upstream and pushed"
  else
    exit 1
  fi
fi
```

### Step 7: Verify push success

```bash
# Compare local and remote
LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse "origin/$BRANCH")

if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
  echo "Push verified: local and remote are in sync"
else
  echo "WARNING: Local and remote differ after push"
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| worktree_path | string | yes | Path to the worktree |
| commit_message | string | yes | Message for the commit |
| push | boolean | no | Whether to push (default: true) |
| force_push | boolean | no | Whether to force push (default: false, requires approval) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether operation succeeded |
| commit_sha | string | SHA of new commit |
| branch | string | Branch that was pushed |
| pushed | boolean | Whether push was executed |

## Example Output

```json
{
  "success": true,
  "commit_sha": "abc123d",
  "branch": "pr-123",
  "pushed": true
}
```

## Commit Message Format

Follow conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
fix(auth): resolve null pointer in login flow

Added null check before accessing user object.
Fixes #456
```

## Error Handling

### Nothing to commit

**Cause**: No changes were made.

**Solution**: Verify changes exist, check if already committed.

### Push rejected

**Cause**: Remote has changes not in local.

**Solution**: Pull first, resolve conflicts, then push.

### Commit message empty

**Cause**: No message provided.

**Solution**: Provide commit message as argument.

### Lock file present

**Cause**: Concurrent git operation.

**Solution**: Wait for other operation to complete, or remove stale lock.

## Complete Commit/Push Script

```bash
#!/bin/bash
# worktree_commit_push.sh

WORKTREE_PATH="$1"
COMMIT_MSG="$2"
PUSH="${3:-true}"

if [ -z "$WORKTREE_PATH" ] || [ -z "$COMMIT_MSG" ]; then
  echo "Usage: worktree_commit_push.sh <worktree_path> <message> [push=true]"
  exit 1
fi

echo "=== Worktree Commit & Push ==="
cd "$WORKTREE_PATH" || exit 1

# Check for locks
GIT_DIR=$(cat .git 2>/dev/null | grep gitdir | cut -d: -f2 | tr -d ' ')
if [ -f "$GIT_DIR/index.lock" ]; then
  echo "ERROR: Git is locked"
  exit 1
fi

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing to commit"
  exit 0
fi

# Stage and commit
git add -A
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
  echo "ERROR: Commit failed"
  exit 1
fi

COMMIT_SHA=$(git rev-parse --short HEAD)
echo "Committed: $COMMIT_SHA"

# Push
if [ "$PUSH" = "true" ]; then
  BRANCH=$(git branch --show-current)
  git push origin "$BRANCH"

  if [ $? -eq 0 ]; then
    echo "Pushed to origin/$BRANCH"
  else
    echo "ERROR: Push failed"
    exit 1
  fi
fi

echo ""
echo "Success!"
echo "Commit: $COMMIT_SHA"
```

## Verification

After commit and push:

```bash
# Verify commit exists
git log -1 --oneline

# Verify remote has commit
git log origin/$(git branch --show-current) -1 --oneline

# Compare local and remote
git status -sb  # Should show "Your branch is up to date"
```
