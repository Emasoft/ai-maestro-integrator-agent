# Worktree Verification

## Table of Contents

This document is organized into four parts for easier reference:

### Part 1: Pre-Cleanup and Isolation Detection

[worktree-verification-part1-pre-cleanup-detection.md](worktree-verification-part1-pre-cleanup-detection.md)

- 4.1 Pre-cleanup verification checklist
  - Complete Verification Checklist
  - Quick Verification Commands
- 4.2 Detecting files written outside worktree boundaries
  - The Isolation Violation Problem
  - Detection Method 1: Main Repo Status Check
  - Detection Method 2: Timestamp Analysis
  - Detection Method 3: Git Diff Against Expected State
  - Detection Method 4: File System Monitoring
  - Detection Method 5: Hash Comparison
  - Automated Isolation Check

### Part 2: Branch and Remote Sync Verification

[worktree-verification-part2-branch-remote-sync.md](worktree-verification-part2-branch-remote-sync.md)

- 4.3 Branch state verification procedures
  - Verifying Branch is Complete
  - Verifying Branch Against Base
  - Verifying Branch Merge Status
  - Verifying No Dependent Branches
  - Branch State Decision Tree
- 4.4 Remote sync verification steps
  - Step 1: Verify Remote Tracking
  - Step 2: Verify No Unpushed Commits
  - Step 3: Verify Remote Branch Exists
  - Step 4: Verify Local and Remote Match
  - Step 5: Verify Push Was Successful
  - Remote Sync Verification Script

### Part 3: Automated and Manual Verification

[worktree-verification-part3-automated-manual.md](worktree-verification-part3-automated-manual.md)

- 4.5 Automated verification script usage
  - Using amia_verify_worktree_isolation.py
  - Interpreting Script Output
  - Integrating Verification into Workflow
- 4.6 Manual verification when scripts fail
  - When to Use Manual Verification
  - Manual Verification Procedure
  - Manual Verification Checklist

### Part 4: Reporting Violations

[worktree-verification-part4-reporting.md](worktree-verification-part4-reporting.md)

- 4.7 Reporting isolation violations
  - Violation Report Format
  - Escalation Criteria
  - Violation Categories
  - Reporting Template for Orchestrator

---

## Overview

Worktree verification ensures:

1. **Clean state:** No uncommitted changes before cleanup
2. **Isolation:** No files written outside worktree
3. **Branch integrity:** Branch properly merged or handled
4. **Remote sync:** All commits pushed
5. **Documentation:** Violations properly reported

Use the automated verification scripts when available, fall back to manual verification when necessary, and always document any violations found.

---

## Quick Reference

### Essential Commands

```bash
# Check worktree status
git -C /tmp/worktrees/pr-123 status --porcelain

# Check for unpushed commits
git -C /tmp/worktrees/pr-123 log @{u}..HEAD --oneline

# Check main repo for unexpected changes
git -C /path/to/main-repo status --porcelain

# Verify isolation with script
python scripts/amia_verify_worktree_isolation.py \
    --worktree-path /tmp/worktrees/pr-123 \
    --main-repo /path/to/main-repo
```

### Verification Decision Tree

```
Before removing worktree:
├─► Is working tree clean?
│   └─► NO: Commit or stash changes first
├─► Are all commits pushed?
│   └─► NO: Push to remote first
├─► Is branch merged or intentionally abandoned?
│   └─► NO: Verify with user before removal
└─► Were any files written outside worktree?
    └─► YES: Document violation and fix first
```

---

Return to [SKILL.md](../SKILL.md) for the complete skill overview.
