# Merge Safeguards for Multi-Worktree Development

## Table of Contents

This document is split into 5 parts for easier navigation. Each part covers specific topics.

---

### [Part 1: Core Concepts](merge-safeguards-part1-core-concepts.md)

- 1.1 Overview - Understanding merge safeguard system purpose
- 1.2 Merge Status States - CLEAN, NEEDS_REBASE, CONFLICTS, DIVERGED
- 1.3 File Conflicts - When same file modified in multiple worktrees
- 1.4 Merge Order Optimization - Why oldest-first strategy works

**Read this when:** You need to understand fundamental merge concepts and terminology.

---

### [Part 2: Usage Workflows](merge-safeguards-part2-usage-workflows.md)

- 2.1 Check Single Worktree Status - Verify worktree can merge cleanly
- 2.2 Create Merge Plan - Plan multiple PR merges
- 2.3 Execute Merge Sequence - Step-by-step merge process
  - 2.3.1 Merge First Worktree
  - 2.3.2 Rebase Remaining Worktrees
  - 2.3.3 Validate After Rebase
- 2.4 Detect File Conflicts - Find files modified in multiple worktrees

**Read this when:** You need to perform merge operations on worktrees.

---

### [Part 3: Validation and Advanced Scenarios](merge-safeguards-part3-validation-advanced.md)

- 3.1 Pre-Merge Validation Checklist - What the validator checks
- 3.2 Multiple Sequential Merges - Merging 5+ worktrees
- 3.3 Conflict Resolution Workflow - Handling rebase conflicts
- 3.4 Detecting Breaking Changes - Testing after merges

**Read this when:** You need to validate merges or handle complex merge scenarios.

---

### [Part 4: Automation and Best Practices](merge-safeguards-part4-automation-practices.md)

- 4.1 Auto-Rebase All Worktrees - Script for batch rebasing
- 4.2 Continuous Validation - Script for validating all worktrees
- 4.3 Best Practices
  - 4.3.1 Validate Before Opening PR
  - 4.3.2 Rebase Daily
  - 4.3.3 Coordinate Overlapping Changes
  - 4.3.4 Test After Each Merge

**Read this when:** You want to automate merge operations or follow best practices.

---

### [Part 5: Troubleshooting and Integration](merge-safeguards-part5-troubleshooting.md)

- 5.1 Troubleshooting
  - 5.1.1 Rebase Fails with Conflicts
  - 5.1.2 Validation Shows "Behind Remote"
  - 5.1.3 Multiple Conflicting Files
- 5.2 Integration with Worktree Lifecycle
  - 5.2.1 During Creation
  - 5.2.2 Before Removal
- 5.3 See Also - Related documentation links

**Read this when:** You encounter merge problems or need lifecycle integration.

---

## Quick Reference

| Scenario | Go To |
|----------|-------|
| First time learning merge safeguards | Part 1 |
| Checking worktree status before PR | Part 2, Section 2.1 |
| Creating merge plan for multiple PRs | Part 2, Section 2.2 |
| Executing merges step-by-step | Part 2, Section 2.3 |
| Validation failed, need resolution | Part 3, Section 3.1 |
| Merging 5+ worktrees at once | Part 3, Section 3.2 |
| Rebase has conflicts | Part 3, Section 3.3 or Part 5, Section 5.1.1 |
| Setting up automation scripts | Part 4, Sections 4.1-4.2 |
| Following merge best practices | Part 4, Section 4.3 |
| Any merge problem or error | Part 5, Section 5.1 |
| Integrating with worktree create/remove | Part 5, Section 5.2 |

---

## Related Documentation

- **Worktree Creation**: `worktree-creation.md`
- **Worktree Removal**: `worktree-removal.md`
- **Port Management**: `port-allocation.md`
- **Registry Format**: `registry-format.md`
