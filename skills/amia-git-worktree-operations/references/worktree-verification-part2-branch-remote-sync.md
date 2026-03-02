# Worktree Verification - Part 2: Branch and Remote Sync Verification

[Back to Worktree Verification Index](worktree-verification.md)

## Table of Contents

- [4.3 Branch State Verification Procedures](#43-branch-state-verification-procedures)
  - [Verifying Branch is Complete](#verifying-branch-is-complete)
  - [Verifying Branch Against Base](#verifying-branch-against-base)
  - [Verifying Branch Merge Status](#verifying-branch-merge-status)
  - [Verifying No Dependent Branches](#verifying-no-dependent-branches)
  - [Branch State Decision Tree](#branch-state-decision-tree)
- [4.4 Remote Sync Verification Steps](#44-remote-sync-verification-steps)
  - [Step 1: Verify Remote Tracking](#step-1-verify-remote-tracking)
  - [Step 2: Verify No Unpushed Commits](#step-2-verify-no-unpushed-commits)
  - [Step 3: Verify Remote Branch Exists](#step-3-verify-remote-branch-exists)
  - [Step 4: Verify Local and Remote Match](#step-4-verify-local-and-remote-match)
  - [Step 5: Verify Push Was Successful](#step-5-verify-push-was-successful)
  - [Remote Sync Verification Script](#remote-sync-verification-script)

---

## 4.3 Branch State Verification Procedures

### Verifying Branch is Complete

```bash
cd /tmp/worktrees/pr-123

# Check current branch
git branch --show-current
# Should show: pr-123

# Check if all work is committed
git status
# Should show: nothing to commit, working tree clean
```

### Verifying Branch Against Base

```bash
# Check commits since branching from main
git log main..HEAD --oneline

# Check files changed compared to main
git diff main --stat
```

### Verifying Branch Merge Status

```bash
# Is branch merged into main?
git branch --merged main | grep pr-123
# If output contains pr-123, it's merged

# Alternatively, check via GitHub API
gh pr view 123 --json state --jq '.state'
# Should show: MERGED or CLOSED
```

### Verifying No Dependent Branches

```bash
# Check if any branches are based on this one
git branch --contains pr-123

# If only 'pr-123' and 'main' appear, no dependent branches
```

### Branch State Decision Tree

```
Is branch fully merged to main?
├─► YES: Safe to delete branch and worktree
└─► NO:
    ├─► Is PR closed/rejected?
    │   ├─► YES: Confirm with user, then safe to remove
    │   └─► NO: DO NOT remove worktree
    └─► Is there more work pending?
        ├─► YES: DO NOT remove worktree
        └─► NO: Why isn't it merged? Investigate first
```

---

## 4.4 Remote Sync Verification Steps

### Step 1: Verify Remote Tracking

```bash
cd /tmp/worktrees/pr-123

# Check if branch tracks remote
git branch -vv
# Should show something like: pr-123 abc1234 [origin/pr-123] commit message
```

### Step 2: Verify No Unpushed Commits

```bash
# Count unpushed commits
git rev-list @{u}..HEAD --count
# Should show: 0

# List unpushed commits (if any)
git log @{u}..HEAD --oneline
# Should show nothing
```

### Step 3: Verify Remote Branch Exists

```bash
# Fetch latest remote info
git fetch origin

# Check if remote branch exists
git ls-remote --heads origin pr-123
# Should show the branch ref if it exists
```

### Step 4: Verify Local and Remote Match

```bash
# Compare local and remote
git diff HEAD origin/pr-123
# Should show nothing (identical)

# Compare commit hashes
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/pr-123)
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "Local and remote are in sync"
else
    echo "WARNING: Local and remote differ"
fi
```

### Step 5: Verify Push Was Successful

```bash
# Check last push result
git reflog show origin/pr-123 | head -1
# Shows when branch was last updated
```

### Remote Sync Verification Script

```bash
#!/bin/bash
# verify_remote_sync.sh

WORKTREE="$1"
if [ -z "$WORKTREE" ]; then
    echo "Usage: $0 <worktree-path>"
    exit 1
fi

cd "$WORKTREE" || exit 1

BRANCH=$(git branch --show-current)
echo "Verifying remote sync for branch: $BRANCH"

# Check tracking
if ! git rev-parse @{u} &>/dev/null; then
    echo "ERROR: Branch does not track a remote"
    exit 1
fi

# Check unpushed commits
UNPUSHED=$(git rev-list @{u}..HEAD --count)
if [ "$UNPUSHED" -gt 0 ]; then
    echo "ERROR: $UNPUSHED unpushed commits"
    git log @{u}..HEAD --oneline
    exit 1
fi

# Check local matches remote
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "ERROR: Local ($LOCAL) differs from remote ($REMOTE)"
    exit 1
fi

echo "OK: Branch is in sync with remote"
```

---

[Back to Worktree Verification Index](worktree-verification.md) | [Previous: Part 1](worktree-verification-part1-pre-cleanup-detection.md) | [Next: Part 3](worktree-verification-part3-automated-manual.md)
