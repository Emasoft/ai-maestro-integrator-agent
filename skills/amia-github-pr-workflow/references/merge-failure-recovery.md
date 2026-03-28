---
name: Merge Failure Recovery
description: Comprehensive guide to handling merge failures, conflicts, and recovery procedures
version: 1.0.0
---

# Merge Failure Recovery

## Table of Contents

- [Overview](#overview)
- [Types of Merge Failures](#types-of-merge-failures)
- [Merge Conflict Resolution](#merge-conflict-resolution)
- [CI Failure During Merge](#ci-failure-during-merge)
- [Partial Merge Recovery](#partial-merge-recovery)
- [Notification Procedures](#notification-procedures)
- [Rollback If Merge Corrupts Main](#rollback-if-merge-corrupts-main)
- [Prevention Strategies](#prevention-strategies)

## Overview

Merge failures can occur at various stages of the PR merge process. This document provides step-by-step recovery procedures for each type of failure to ensure code integrity and minimize disruption.

## Types of Merge Failures

| Failure Type | Cause | Severity | Recovery Difficulty |
|--------------|-------|----------|---------------------|
| Merge Conflict | Divergent changes in same files | Medium | Usually straightforward |
| CI Failure During Merge | Tests fail post-merge | High | Depends on failure type |
| Partial Merge | Process interrupted mid-merge | Critical | Requires careful recovery |
| Branch Protection Violation | Missing approvals or checks | Low | Re-request approvals |
| Main Branch Corruption | Bad merge reached main | Critical | Requires immediate rollback |

## Merge Conflict Resolution

### Step 1: Identify Conflicting Files

```bash
# Check merge status
git status

# List conflicting files
git diff --name-only --diff-filter=U
```

### Step 2: Understand the Conflict

```bash
# View conflict details for each file
git diff <filename>

# View both versions
git show :1:<filename>  # Common ancestor
git show :2:<filename>  # Ours (target branch)
git show :3:<filename>  # Theirs (source branch)
```

### Step 3: Resolve Conflicts

**Option A: Manual Resolution**

```bash
# Open file and resolve conflict markers
# <<<<<<< HEAD
# (your changes)
# =======
# (their changes)
# >>>>>>> branch-name

# After resolving, mark as resolved
git add <filename>
```

**Option B: Accept One Side**

```bash
# Accept ours (target branch version)
git checkout --ours <filename>
git add <filename>

# Accept theirs (source branch version)
git checkout --theirs <filename>
git add <filename>
```

**Option C: Use Merge Tool**

```bash
git mergetool <filename>
```

### Step 4: Complete the Merge

```bash
# Verify all conflicts resolved
git status

# Complete merge commit
git commit -m "Merge branch 'feature' into main - resolved conflicts in [files]"

# Push to remote
git push origin main
```

### Step 5: Notify Author

Send a message using the `agent-messaging` skill with:

- **Recipient**: `PR_AUTHOR_AGENT`
- **Subject**: `Merge Conflict Resolved: PR #123`
- **Priority**: `normal`
- **Content**: `{"type": "merge-conflict-resolved", "message": "Merge conflicts in PR #123 have been resolved. Files affected: [LIST]. Please verify the resolution."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## CI Failure During Merge

### Scenario: Tests Fail After Merge to Main

This is a critical situation - broken code has reached the main branch.

### Step 1: Assess Severity

```bash
# Get CI failure details
gh run list --repo owner/repo --branch main --limit 5 --json status,conclusion,name

# View specific run logs
gh run view <run-id> --log-failed
```

### Step 2: Determine Action

| Failure Type | Action |
|--------------|--------|
| Flaky test | Re-run CI, investigate flakiness |
| New test failure | Revert merge, fix in PR branch |
| Build failure | Revert immediately |
| Security scan failure | Revert immediately |

### Step 3: Quick Fix vs Revert Decision

**Quick Fix (< 15 minutes, minor issue)**

```bash
# Create hotfix branch
git checkout main
git pull origin main
git checkout -b hotfix/fix-ci-pr-123

# Apply fix
# ... make changes ...

# Push and create PR
git push -u origin hotfix/fix-ci-pr-123
gh pr create --title "Hotfix: Fix CI failure from PR #123" --base main
```

**Revert (> 15 minutes or critical)**

```bash
# Find the merge commit
git log --oneline -10

# Revert the merge commit
git revert -m 1 <merge-commit-sha>
git push origin main
```

### Step 4: Notify Stakeholders

**Notify author of failure:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `PR_AUTHOR_AGENT`
- **Subject**: `[CI FAILURE] PR #123 merge caused test failures`
- **Priority**: `urgent`
- **Content**: `{"type": "ci-failure-post-merge", "message": "PR #123 merge to main caused CI failures. Action taken: [REVERT/HOTFIX]. Failures: [SUMMARY]. Please investigate and resubmit."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Notify orchestrator:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `[CI FAILURE] Main branch temporarily broken`
- **Priority**: `urgent`
- **Content**: `{"type": "main-branch-issue", "message": "Main branch CI failing after PR #123 merge. Recovery action: [REVERT/HOTFIX]. ETA for resolution: [TIME]."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## Partial Merge Recovery

### Scenario: Merge Process Interrupted

This can happen due to:

- Network failure during push
- Process killed mid-merge
- System crash

### Step 1: Assess Current State

```bash
# Check if merge is in progress
git status

# If "You have unmerged paths", merge is incomplete
# If clean, check remote state
git fetch origin
git log --oneline origin/main -5
git log --oneline main -5
```

### Step 2: Recovery Options

**Option A: Merge Was Not Pushed**

```bash
# Abort the incomplete merge
git merge --abort

# Or reset to pre-merge state
git reset --hard HEAD~1
```

**Option B: Partial Push Occurred**

```bash
# Check what reached remote
git log origin/main --oneline -10

# If merge commit exists on remote but is incomplete:
# Option 1: Complete the merge locally and force push (DANGEROUS)
# Option 2: Revert on remote

# Safer option - revert on remote
git revert -m 1 <partial-merge-commit>
git push origin main
```

**Option C: Unknown State**

```bash
# Create backup of current state
git branch backup-recovery-$(date +%Y%m%d)

# Fetch latest remote state
git fetch origin

# Reset local to match remote
git reset --hard origin/main

# Re-attempt merge from clean state
```

### Step 3: Verify Recovery

```bash
# Verify main branch is clean
git log --oneline -10
git status

# Verify CI is green
gh run list --repo owner/repo --branch main --limit 1

# Verify no corruption
git fsck
```

## Notification Procedures

### Notify PR Author

Always notify the PR author when:

- Merge conflicts occur
- CI fails after merge
- Merge is reverted

Send a message using the `agent-messaging` skill with:

- **Recipient**: `PR_AUTHOR_AGENT`
- **Subject**: `[MERGE ISSUE] PR #123 - Action Required`
- **Priority**: `high`
- **Content**: `{"type": "merge-issue", "message": "Issue with PR #123 merge: [DESCRIPTION]. Required action: [ACTION]. Please respond within [TIMEFRAME]."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Notify Code Reviewer

Notify reviewer if their approved PR caused issues. Send a message using the `agent-messaging` skill with:

- **Recipient**: `REVIEWER_AGENT`
- **Subject**: `[FYI] PR #123 post-merge issue`
- **Priority**: `normal`
- **Content**: `{"type": "review-followup", "message": "PR #123 which you reviewed encountered post-merge issues: [SUMMARY]. This is for awareness only - author has been notified."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Notify Orchestrator

Always notify orchestrator of significant merge issues. Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `[MERGE STATUS] PR #123`
- **Priority**: `high`
- **Content**: `{"type": "merge-status", "message": "PR #123 merge status: [FAILED/REVERTED/RECOVERED]. Reason: [REASON]. Next steps: [STEPS]."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## Rollback If Merge Corrupts Main

### When to Rollback

Rollback immediately if:

- Build completely broken
- Security vulnerability introduced
- Data corruption possible
- Multiple downstream systems affected

### Step 1: Stop the Bleeding

```bash
# Prevent further merges
# (If using branch protection, CI failure should block this automatically)

# Alert team: Send a message using the agent-messaging skill with:
#   Recipient: orchestrator-amoa
#   Subject: [CRITICAL] Main branch corrupted - Rollback in progress
#   Priority: urgent
#   Content: {"type": "critical-rollback", "message": "Main branch corrupted by PR #123. Initiating immediate rollback. All merges blocked until resolved."}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.
```

### Step 2: Identify Good State

```bash
# Find last known good commit
git log --oneline main -20

# Verify each commit's CI status
gh run list --repo owner/repo --branch main --limit 20 --json headSha,conclusion

# Identify the commit before the bad merge
GOOD_COMMIT="<sha-of-good-commit>"
```

### Step 3: Execute Rollback

**Option A: Revert (Preferred - Preserves History)**

```bash
# Revert the bad merge
git checkout main
git pull origin main
git revert -m 1 <bad-merge-sha>
git push origin main

# Verify CI passes
gh run watch
```

**Option B: Reset (Last Resort - Destructive)**

```bash
# REQUIRES EXPLICIT APPROVAL - This rewrites history
# Only use if revert is not possible

git checkout main
git reset --hard $GOOD_COMMIT
git push --force origin main  # DANGEROUS
```

### Step 4: Verify Recovery

```bash
# Verify main is healthy
git log --oneline -5
gh run list --repo owner/repo --branch main --limit 1

# Run smoke tests
./scripts/smoke-tests.sh

# Verify downstream systems
curl https://api.example.com/health
```

### Step 5: Post-Mortem

Document what happened:

- What caused the corruption
- How it was detected
- Recovery steps taken
- Prevention measures for future

## Prevention Strategies

### Pre-Merge Checks

1. **Always verify CI passes before merge**

   ```bash
   python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo
   ```

2. **Use branch protection rules**
   - Require status checks to pass
   - Require pull request reviews
   - Require linear history (optional)

3. **Run local tests before merge**

   ```bash
   git checkout pr-branch
   git merge main --no-commit
   pytest tests/
   git merge --abort  # If tests fail
   ```

### During Merge

1. **Never force push to protected branches**
2. **Use `--no-ff` for merge commits** (creates explicit merge point)
3. **Verify merge locally before pushing**

### Post-Merge Monitoring

1. **Watch CI immediately after merge**

   ```bash
   gh run watch
   ```

2. **Monitor error rates in production** (if auto-deployed)

3. **Be ready to revert within 15 minutes**

---

## Quick Reference: Recovery Decision Tree

```
Merge Failed
    |
    +-- Conflict?
    |   +-- YES -> Resolve conflicts manually or accept one side
    |   +-- NO -> Continue
    |
    +-- CI Failed?
    |   +-- YES -> Is fix < 15 min?
    |   |   +-- YES -> Hotfix
    |   |   +-- NO -> Revert
    |   +-- NO -> Continue
    |
    +-- Partial merge?
    |   +-- YES -> Abort or revert depending on push state
    |   +-- NO -> Continue
    |
    +-- Main corrupted?
        +-- YES -> IMMEDIATE ROLLBACK
        +-- NO -> Investigate and fix
```

---

**Version**: 1.0.0
**Last Updated**: 2025-02-04
**Category**: Merge Recovery
