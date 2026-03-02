# Removing Worktrees - Complete Index

This document provides a complete table of contents for all worktree removal documentation, split across three parts for efficient progressive disclosure.

---

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [Part 1: Preparation and Basic Commands](#part-1-preparation-and-basic-commands)
  - [Contents](#contents)
- [Part 2: Post-Removal and Automation](#part-2-post-removal-and-automation)
  - [Contents](#contents-1)
- [Part 3: Advanced Operations](#part-3-advanced-operations)
  - [Contents](#contents-2)
- [Key Commands Quick Reference](#key-commands-quick-reference)
- [Related Documentation](#related-documentation)

---

## Quick Navigation

| If you need to... | Go to |
|-------------------|-------|
| Understand worktree removal basics | [Part 1: Overview](#part-1-preparation-and-basic-commands) |
| Complete pre-removal checklist | [Part 1: Pre-Removal Checklist](#part-1-preparation-and-basic-commands) |
| Run removal commands | [Part 1: Removal Commands](#part-1-preparation-and-basic-commands) |
| Update registry after removal | [Part 2: Post-Removal Steps](#part-2-post-removal-and-automation) |
| Use automated cleanup script | [Part 2: Cleanup Script](#part-2-post-removal-and-automation) |
| Fix removal failures | [Part 2: Handling Failures](#part-2-post-removal-and-automation) |
| Remove multiple worktrees at once | [Part 3: Bulk Removal](#part-3-advanced-operations) |
| Verify successful removal | [Part 3: Verification](#part-3-advanced-operations) |
| Troubleshoot removal problems | [Part 3: Troubleshooting](#part-3-advanced-operations) |

---

## Part 1: Preparation and Basic Commands

**File:** [removing-worktrees-part1-basics.md](removing-worktrees-part1-basics.md)

### Contents

1. **Overview**
   - What is Worktree Removal
   - When to Remove a Worktree
   - Why Follow This Process

2. **Pre-Removal Checklist**
   - 2.1 Check for Uncommitted Work
   - 2.2 Check Pull Request Status
   - 2.3 Check for Running Processes
   - 2.4 Check Registry Entry
   - 2.5 Complete Checklist Template

3. **Removal Commands**
   - 3.1 Basic Removal (Standard)
   - 3.2 Force Removal
   - 3.3 Pruning Stale Entries
   - 3.4 Dry Run (Preview Only)

---

## Part 2: Post-Removal and Automation

**File:** [removing-worktrees-part2-post-removal.md](removing-worktrees-part2-post-removal.md)

### Contents

1. **Post-Removal Steps**
   - 1.1 Update Registry
   - 1.2 Release Allocated Ports
   - 1.3 Clean Up Remaining Files
   - 1.4 Update Agent Assignments
   - 1.5 Document Removal

2. **Cleanup Script**
   - Script location and usage
   - Script contents (full implementation)
   - Making script executable
   - Integration with task agents

3. **Handling Failures**
   - 3.1 Failure: Locked Worktree
   - 3.2 Failure: Missing Worktree Path
   - 3.3 Failure: Registry Out of Sync
   - 3.4 Failure: Permission Denied
   - 3.5 Failure: Worktree Has Uncommitted Changes

---

## Part 3: Advanced Operations

**File:** [removing-worktrees-part3-advanced.md](removing-worktrees-part3-advanced.md)

### Contents

1. **Bulk Removal**
   - 1.1 Method 1: Loop Through List
   - 1.2 Method 2: From Registry Query
   - 1.3 Method 3: Age-Based Removal
   - 1.4 Method 4: Interactive Selection
   - 1.5 Bulk Removal Script

2. **Verification**
   - 2.1 Verification Checklist
   - 2.2 Verification Commands
   - 2.3 Verification Script

3. **Troubleshooting**
   - 3.1 Cannot remove current worktree
   - 3.2 Removal succeeds but directory still exists
   - 3.3 Registry shows more worktrees than git
   - 3.4 Prune removes wrong worktree
   - 3.5 Force removal fails

4. **Quick Reference**
   - Common Removal Workflows
   - Key Commands Summary

---

## Key Commands Quick Reference

| Command | Purpose | Part |
|---------|---------|------|
| `git worktree remove <path>` | Standard removal | Part 1 |
| `git worktree remove --force <path>` | Force removal (discards changes) | Part 1 |
| `git worktree remove --dry-run <path>` | Preview removal | Part 1 |
| `git worktree prune` | Clean stale entries | Part 1 |
| `git worktree unlock <path>` | Unlock locked worktree | Part 2 |
| `./scripts/cleanup-worktree.sh` | Automated cleanup | Part 2 |
| `./scripts/bulk-cleanup-worktrees.sh` | Bulk cleanup | Part 3 |
| `./scripts/verify-worktree-removal.sh` | Verify removal | Part 3 |

---

## Related Documentation

- [Worktree Management Overview](../SKILL.md)
- [Creating Worktrees](creating-worktrees.md)
- [Worktree Registry](registry-system.md)

---

**Return to:** [Worktree Management Overview](../SKILL.md)
