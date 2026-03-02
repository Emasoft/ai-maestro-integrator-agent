---
name: op-fetch-pr-branch
description: "Fetch a PR branch from the remote repository"
procedure: support-skill
workflow-instruction: support
---

# Operation: Fetch PR Branch


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify PR exists](#step-1-verify-pr-exists)
  - [Step 2: Determine local branch name](#step-2-determine-local-branch-name)
  - [Step 3: Fetch the PR branch](#step-3-fetch-the-pr-branch)
  - [Step 4: Verify fetch success](#step-4-verify-fetch-success)
  - [Step 5: Show branch info](#step-5-show-branch-info)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Fetch Patterns](#fetch-patterns)
  - [Standard PR fetch](#standard-pr-fetch)
  - [Fetch and checkout](#fetch-and-checkout)
  - [Fetch without local branch](#fetch-without-local-branch)
  - [Update existing PR branch](#update-existing-pr-branch)
- [Error Handling](#error-handling)
  - [PR not found](#pr-not-found)
  - [Network error](#network-error)
  - [Branch already exists](#branch-already-exists)
  - [Permission denied](#permission-denied)
- [Complete Fetch Script](#complete-fetch-script)
- [Verification](#verification)

## Purpose

Fetch a pull request branch from the remote repository into a local branch, preparing it for worktree creation or local review.

## When to Use

- Before creating a worktree for a PR
- When updating a local PR branch with remote changes
- When reviewing a PR locally

## Prerequisites

1. GitHub CLI or git configured for the repository
2. Network access to remote
3. Read access to the PR

## Procedure

### Step 1: Verify PR exists

```bash
PR_NUMBER=123

# Using GitHub CLI
gh pr view "$PR_NUMBER" --json number,headRefName,state > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: PR #$PR_NUMBER not found or not accessible"
  exit 1
fi

# Get PR details
PR_INFO=$(gh pr view "$PR_NUMBER" --json number,headRefName,state,headRepositoryOwner)
HEAD_REF=$(echo "$PR_INFO" | jq -r '.headRefName')
PR_STATE=$(echo "$PR_INFO" | jq -r '.state')

echo "PR #$PR_NUMBER: $HEAD_REF ($PR_STATE)"
```

### Step 2: Determine local branch name

```bash
# Use pr-{number} format for consistency
LOCAL_BRANCH="pr-$PR_NUMBER"

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/$LOCAL_BRANCH"; then
  echo "Branch $LOCAL_BRANCH already exists locally"
  BRANCH_EXISTS=true
else
  BRANCH_EXISTS=false
fi
```

### Step 3: Fetch the PR branch

```bash
# Fetch PR head ref into local branch
git fetch origin "pull/$PR_NUMBER/head:$LOCAL_BRANCH"

if [ $? -eq 0 ]; then
  echo "Fetched PR #$PR_NUMBER into $LOCAL_BRANCH"
else
  echo "ERROR: Failed to fetch PR"
  exit 1
fi
```

### Step 4: Verify fetch success

```bash
# Check local branch exists now
if git show-ref --verify --quiet "refs/heads/$LOCAL_BRANCH"; then
  # Get commit info
  COMMIT=$(git rev-parse --short "$LOCAL_BRANCH")
  echo "Branch $LOCAL_BRANCH at commit $COMMIT"
else
  echo "ERROR: Branch not created after fetch"
  exit 1
fi
```

### Step 5: Show branch info

```bash
# Show recent commits on the branch
echo ""
echo "Recent commits on $LOCAL_BRANCH:"
git log "$LOCAL_BRANCH" --oneline -5

# Show diff stat from base
BASE_BRANCH=$(gh pr view "$PR_NUMBER" --json baseRefName --jq '.baseRefName')
echo ""
echo "Changes from $BASE_BRANCH:"
git diff --stat "$BASE_BRANCH...$LOCAL_BRANCH" 2>/dev/null || echo "(cannot compare - base may not be fetched)"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pr_number | number | yes | PR number to fetch |
| local_branch | string | no | Local branch name (default: pr-{number}) |
| force | boolean | no | Force update if branch exists |

## Output

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether fetch succeeded |
| pr_number | number | PR that was fetched |
| local_branch | string | Local branch name |
| commit | string | HEAD commit of fetched branch |
| head_ref | string | Remote branch name |

## Example Output

```json
{
  "success": true,
  "pr_number": 123,
  "local_branch": "pr-123",
  "commit": "abc123d",
  "head_ref": "feature/new-auth"
}
```

## Fetch Patterns

### Standard PR fetch

```bash
git fetch origin pull/123/head:pr-123
```

### Fetch and checkout

```bash
gh pr checkout 123
```

### Fetch without local branch

```bash
git fetch origin pull/123/head
# Access as FETCH_HEAD
```

### Update existing PR branch

```bash
# Delete and re-fetch
git branch -D pr-123
git fetch origin pull/123/head:pr-123
```

## Error Handling

### PR not found

**Cause**: PR number doesn't exist or was deleted.

**Solution**: Verify PR number, check repository.

### Network error

**Cause**: Cannot reach remote.

**Solution**: Check network, verify remote URL.

### Branch already exists

**Cause**: Previous fetch created the branch.

**Solution**: Delete branch first or use different name.

### Permission denied

**Cause**: No read access to PR.

**Solution**: Verify authentication and permissions.

## Complete Fetch Script

```bash
#!/bin/bash
# fetch_pr_branch.sh

PR_NUMBER="$1"
LOCAL_BRANCH="${2:-pr-$PR_NUMBER}"
FORCE="${3:-false}"

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: fetch_pr_branch.sh <pr_number> [local_branch] [force]"
  exit 1
fi

echo "=== Fetching PR #$PR_NUMBER ==="

# Verify PR exists
if ! gh pr view "$PR_NUMBER" > /dev/null 2>&1; then
  echo "ERROR: PR #$PR_NUMBER not found"
  exit 1
fi

# Get PR info
HEAD_REF=$(gh pr view "$PR_NUMBER" --json headRefName --jq '.headRefName')
echo "Remote branch: $HEAD_REF"
echo "Local branch: $LOCAL_BRANCH"

# Handle existing branch
if git show-ref --verify --quiet "refs/heads/$LOCAL_BRANCH"; then
  if [ "$FORCE" = "true" ]; then
    echo "Deleting existing branch..."
    git branch -D "$LOCAL_BRANCH"
  else
    echo "Branch exists. Use force=true to update."
    exit 1
  fi
fi

# Fetch
git fetch origin "pull/$PR_NUMBER/head:$LOCAL_BRANCH"

if [ $? -eq 0 ]; then
  COMMIT=$(git rev-parse --short "$LOCAL_BRANCH")
  echo ""
  echo "Success!"
  echo "Branch: $LOCAL_BRANCH"
  echo "Commit: $COMMIT"
else
  echo "ERROR: Fetch failed"
  exit 1
fi
```

## Verification

After fetching:

```bash
# Verify branch exists
git branch -l "pr-$PR_NUMBER"

# Show branch info
git log "pr-$PR_NUMBER" -1 --oneline

# Compare with remote
git log --oneline "pr-$PR_NUMBER" -3
```
