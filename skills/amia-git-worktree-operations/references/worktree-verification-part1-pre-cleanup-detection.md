# Worktree Verification - Part 1: Pre-Cleanup and Isolation Detection

[Back to Worktree Verification Index](worktree-verification.md)

## Table of Contents

- [4.1 Pre-Cleanup Verification Checklist](#41-pre-cleanup-verification-checklist)
  - [Complete Verification Checklist](#complete-verification-checklist)
  - [Quick Verification Commands](#quick-verification-commands)
- [4.2 Detecting Files Written Outside Worktree Boundaries](#42-detecting-files-written-outside-worktree-boundaries)
  - [The Isolation Violation Problem](#the-isolation-violation-problem)
  - [Detection Method 1: Main Repo Status Check](#detection-method-1-main-repo-status-check)
  - [Detection Method 2: Timestamp Analysis](#detection-method-2-timestamp-analysis)
  - [Detection Method 3: Git Diff Against Expected State](#detection-method-3-git-diff-against-expected-state)
  - [Detection Method 4: File System Monitoring](#detection-method-4-file-system-monitoring)
  - [Detection Method 5: Hash Comparison](#detection-method-5-hash-comparison)
  - [Automated Isolation Check](#automated-isolation-check)

---

## 4.1 Pre-Cleanup Verification Checklist

### Complete Verification Checklist

Before removing any worktree, verify ALL of the following:

```
WORKTREE CLEANUP VERIFICATION CHECKLIST
=======================================
Worktree Path: ____________________________
PR Number: ________________________________
Date: ____________________________________

CHANGE STATUS
□ git status shows "working tree clean"
□ No untracked files exist
□ No staged but uncommitted changes
□ No stashed changes for this worktree

REMOTE SYNC
□ All local commits pushed to remote
□ Remote branch is up to date
□ No pending push operations

BRANCH STATE
□ Branch is merged OR intentionally abandoned
□ No dependent branches exist
□ PR is closed on GitHub/GitLab

ISOLATION VERIFICATION
□ No files written to main repository
□ No files written to other worktrees
□ No files written outside worktree tree

PROCESS STATE
□ No running processes use worktree files
□ No editors have worktree files open
□ No terminal sessions are in worktree directory

SIGN-OFF
Verified by: ______________________________
Verification method: □ Script  □ Manual  □ Both
```

### Quick Verification Commands

Run these commands to quickly verify status:

```bash
WORKTREE="/tmp/worktrees/pr-123"

# 1. Check for uncommitted changes
echo "=== Uncommitted Changes ==="
git -C "$WORKTREE" status --porcelain

# 2. Check for unpushed commits
echo "=== Unpushed Commits ==="
git -C "$WORKTREE" log @{u}..HEAD --oneline 2>/dev/null || echo "No upstream set"

# 3. Check for stashed changes
echo "=== Stashed Changes ==="
git -C "$WORKTREE" stash list

# 4. Check main repo for unexpected changes
echo "=== Main Repo Status ==="
git -C /path/to/main-repo status --porcelain
```

---

## 4.2 Detecting Files Written Outside Worktree Boundaries

### The Isolation Violation Problem

When agents write files outside their assigned worktree:
- Changes appear in wrong branch
- Commits contain unrelated changes
- PR reviews fail
- Merge conflicts arise

### Detection Method 1: Main Repo Status Check

```bash
cd /path/to/main-repo
git status --porcelain

# If output is NOT empty, isolation may be violated
```

### Detection Method 2: Timestamp Analysis

Find files modified during worktree session:

```bash
# Find files modified in last hour in main repo
find /path/to/main-repo -type f -mmin -60 -not -path '*/\.git/*'

# Compare with worktree
find /tmp/worktrees/pr-123 -type f -mmin -60 -not -path '*/\.git/*'
```

### Detection Method 3: Git Diff Against Expected State

```bash
cd /path/to/main-repo

# Check if main branch has unexpected modifications
git diff HEAD

# Check against last known clean state
git diff <last-known-clean-commit>
```

### Detection Method 4: File System Monitoring

Set up monitoring before agent work begins:

```bash
# Using inotifywait (Linux)
inotifywait -m -r /path/to/main-repo --exclude '\.git' \
    -e modify -e create -e delete > /tmp/main-repo-events.log &

# After agent work, check log for unexpected events
cat /tmp/main-repo-events.log
```

### Detection Method 5: Hash Comparison

```bash
# Before agent work
find /path/to/main-repo -type f -not -path '*/\.git/*' \
    -exec md5sum {} \; > /tmp/before.md5

# After agent work
find /path/to/main-repo -type f -not -path '*/\.git/*' \
    -exec md5sum {} \; > /tmp/after.md5

# Compare
diff /tmp/before.md5 /tmp/after.md5
```

### Automated Isolation Check

```bash
#!/bin/bash
# check_isolation.sh

MAIN_REPO="/path/to/main-repo"
WORKTREE="/tmp/worktrees/pr-123"

echo "Checking isolation for worktree: $WORKTREE"

# Check main repo for changes
MAIN_CHANGES=$(git -C "$MAIN_REPO" status --porcelain | wc -l)
if [ "$MAIN_CHANGES" -gt 0 ]; then
    echo "VIOLATION: Main repo has $MAIN_CHANGES uncommitted changes"
    git -C "$MAIN_REPO" status --porcelain
    exit 1
fi

# Check other worktrees for changes
for OTHER in /tmp/worktrees/*/; do
    if [ "$OTHER" != "$WORKTREE/" ]; then
        OTHER_CHANGES=$(git -C "$OTHER" status --porcelain | wc -l)
        if [ "$OTHER_CHANGES" -gt 0 ]; then
            echo "WARNING: Other worktree $OTHER has changes"
        fi
    fi
done

echo "OK: No isolation violations detected"
```

---

[Back to Worktree Verification Index](worktree-verification.md) | [Next: Part 2 - Branch and Remote Sync](worktree-verification-part2-branch-remote-sync.md)
