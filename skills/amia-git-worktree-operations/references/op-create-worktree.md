---
name: op-create-worktree
description: "Create a git worktree for parallel PR processing"
procedure: support-skill
workflow-instruction: support
---

# Operation: Create Worktree


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify git version](#step-1-verify-git-version)
  - [Step 2: Check no concurrent git operations](#step-2-check-no-concurrent-git-operations)
  - [Step 3: Fetch PR branch](#step-3-fetch-pr-branch)
  - [Step 4: Determine worktree path](#step-4-determine-worktree-path)
  - [Step 5: Create worktree](#step-5-create-worktree)
  - [Step 6: Verify worktree creation](#step-6-verify-worktree-creation)
  - [Step 7: Output worktree info](#step-7-output-worktree-info)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Worktree Path Rules](#worktree-path-rules)
- [Error Handling](#error-handling)
  - [Branch already checked out](#branch-already-checked-out)
  - [Fetch fails](#fetch-fails)
  - [Path already exists](#path-already-exists)
  - [Permission denied](#permission-denied)
- [Complete Creation Script](#complete-creation-script)
- [Verification](#verification)

## Purpose

Create a new git worktree directory for working on a PR in isolation, enabling parallel development without branch switching.

## When to Use

- When starting work on a new PR
- When need to work on multiple PRs simultaneously
- When delegating PR work to a subagent
- When reviewing a PR while continuing other work

## Prerequisites

1. Git version 2.15 or higher (`git --version`)
2. Sufficient disk space for worktree
3. Write access to base path for worktrees
4. No other git operations currently running

## Procedure

### Step 1: Verify git version

```bash
GIT_VERSION=$(git --version | grep -oP '\d+\.\d+')
MIN_VERSION="2.15"

if [ "$(printf '%s\n' "$MIN_VERSION" "$GIT_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
  echo "ERROR: Git version $GIT_VERSION is below minimum $MIN_VERSION"
  exit 1
fi
echo "Git version: $GIT_VERSION (OK)"
```

### Step 2: Check no concurrent git operations

```bash
# Check for lock files
if [ -f ".git/index.lock" ]; then
  echo "ERROR: Git index is locked - another operation is running"
  exit 1
fi

echo "No concurrent git operations detected"
```

### Step 3: Fetch PR branch

```bash
PR_NUMBER=123
REPO_ROOT=$(git rev-parse --show-toplevel)

# Fetch the PR branch
git fetch origin "pull/$PR_NUMBER/head:pr-$PR_NUMBER"

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to fetch PR #$PR_NUMBER"
  exit 1
fi

echo "Fetched PR #$PR_NUMBER"
```

### Step 4: Determine worktree path

```bash
BASE_PATH="/tmp/worktrees"
WORKTREE_PATH="$BASE_PATH/pr-$PR_NUMBER"

# Ensure base path exists
mkdir -p "$BASE_PATH"

# Check worktree doesn't already exist
if [ -d "$WORKTREE_PATH" ]; then
  echo "ERROR: Worktree already exists at $WORKTREE_PATH"
  echo "Use existing worktree or clean up first"
  exit 1
fi
```

### Step 5: Create worktree

```bash
# Create the worktree
git worktree add "$WORKTREE_PATH" "pr-$PR_NUMBER"

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to create worktree"
  exit 1
fi

echo "Created worktree at $WORKTREE_PATH"
```

### Step 6: Verify worktree creation

```bash
# Verify worktree exists in list
git worktree list | grep -q "$WORKTREE_PATH"

if [ $? -eq 0 ]; then
  echo "Worktree verified in git worktree list"
else
  echo "WARNING: Worktree not found in list"
fi

# Verify directory exists and has .git
if [ -f "$WORKTREE_PATH/.git" ]; then
  echo "Worktree directory structure verified"
else
  echo "ERROR: Worktree directory structure invalid"
  exit 1
fi
```

### Step 7: Output worktree info

```bash
# Get branch name
BRANCH=$(cd "$WORKTREE_PATH" && git branch --show-current)

# Get commit
COMMIT=$(cd "$WORKTREE_PATH" && git rev-parse --short HEAD)

echo ""
echo "=== Worktree Created ==="
echo "Path: $WORKTREE_PATH"
echo "Branch: $BRANCH"
echo "Commit: $COMMIT"
echo "PR: #$PR_NUMBER"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pr_number | number | yes | PR number to create worktree for |
| base_path | string | no | Base path for worktrees (default: /tmp/worktrees) |
| branch_name | string | no | Custom branch name (default: pr-{number}) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| worktree_path | string | Absolute path to created worktree |
| branch | string | Branch checked out in worktree |
| commit | string | Current commit SHA |
| pr_number | number | Associated PR number |

## Example Output

```json
{
  "worktree_path": "/tmp/worktrees/pr-123",
  "branch": "pr-123",
  "commit": "abc123d",
  "pr_number": 123
}
```

## Worktree Path Rules

1. **Outside main repository** - Never nest inside the main repo
2. **Absolute paths only** - Always use full paths
3. **Never nest worktrees** - Worktrees cannot contain other worktrees
4. **Unique per branch** - Each branch can only exist in one worktree

## Error Handling

### Branch already checked out

**Cause**: Branch exists in another worktree.

**Solution**: Use the existing worktree or remove it first.

### Fetch fails

**Cause**: PR doesn't exist or network issue.

**Solution**: Verify PR number, check network.

### Path already exists

**Cause**: Directory exists from previous worktree.

**Solution**: Clean up orphaned directory or use different path.

### Permission denied

**Cause**: No write access to base path.

**Solution**: Choose different base path or fix permissions.

## Complete Creation Script

```bash
#!/bin/bash
# create_worktree.sh

PR_NUMBER="$1"
BASE_PATH="${2:-/tmp/worktrees}"

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: create_worktree.sh <pr_number> [base_path]"
  exit 1
fi

WORKTREE_PATH="$BASE_PATH/pr-$PR_NUMBER"
BRANCH_NAME="pr-$PR_NUMBER"

echo "=== Creating Worktree for PR #$PR_NUMBER ==="

# Check git version
GIT_VER=$(git --version | grep -oP '\d+\.\d+')
echo "Git version: $GIT_VER"

# Check for locks
if [ -f ".git/index.lock" ]; then
  echo "ERROR: Git is locked"
  exit 1
fi

# Fetch PR
echo "Fetching PR #$PR_NUMBER..."
git fetch origin "pull/$PR_NUMBER/head:$BRANCH_NAME" || exit 1

# Create base path
mkdir -p "$BASE_PATH"

# Check existing
if [ -d "$WORKTREE_PATH" ]; then
  echo "ERROR: Path exists: $WORKTREE_PATH"
  exit 1
fi

# Create worktree
echo "Creating worktree..."
git worktree add "$WORKTREE_PATH" "$BRANCH_NAME" || exit 1

# Verify
if git worktree list | grep -q "$WORKTREE_PATH"; then
  echo ""
  echo "SUCCESS: Worktree created"
  echo "Path: $WORKTREE_PATH"
  echo "Branch: $BRANCH_NAME"
  cd "$WORKTREE_PATH" && echo "Commit: $(git rev-parse --short HEAD)"
else
  echo "ERROR: Verification failed"
  exit 1
fi
```

## Verification

After creation:

```bash
# List all worktrees
git worktree list

# Navigate to worktree
cd "$WORKTREE_PATH"

# Verify correct branch
git branch --show-current

# Verify clean state
git status
```
