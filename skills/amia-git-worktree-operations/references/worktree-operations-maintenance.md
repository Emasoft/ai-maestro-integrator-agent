# Worktree Operations: Maintenance

This document serves as an index to detailed maintenance operations for git worktrees.

---

## Quick Reference

| If you need to... | See this document |
|-------------------|-------------------|
| Sync worktree with main branch | [Part 1: Syncing](worktree-operations-maintenance-part1-syncing.md) |
| Follow worktree management guidelines | [Part 2: Best Practices](worktree-operations-maintenance-part2-best-practices.md) |
| Fix worktree operation problems | [Part 3: Troubleshooting](worktree-operations-maintenance-part3-troubleshooting.md) |

---

## Part 1: Syncing with Main Branch

**File**: [worktree-operations-maintenance-part1-syncing.md](worktree-operations-maintenance-part1-syncing.md)

**WHEN TO USE**: When you need to incorporate the latest changes from the main branch into your worktree branch.

### Contents
1. Why Sync Regularly
2. Phase 1: Fetch Latest Main
3. Phase 2: Verify Current State
4. Phase 3: Rebase on Origin/Main
5. Phase 4: Handling Rebase Conflicts (If They Occur)
6. Phase 5: Force Push Updated Branch
7. Phase 6: If You Stashed Changes Earlier
8. Complete Sync Workflow Example

---

## Part 2: Best Practices

**File**: [worktree-operations-maintenance-part2-best-practices.md](worktree-operations-maintenance-part2-best-practices.md)

**WHEN TO USE**: When you need guidelines for managing worktrees effectively and avoiding common mistakes.

### Contents
1. Practice 1: Keep Worktrees Updated
2. Practice 2: Clean Working Tree Before Switching
3. Practice 3: Use Meaningful Worktree Names
4. Practice 4: Lock Worktrees When In Active Use
5. Practice 5: Remove Completed Worktrees Promptly
6. Practice 6: Prune Stale Worktrees Regularly
7. Practice 7: Document Worktree Purpose

---

## Part 3: Troubleshooting

**File**: [worktree-operations-maintenance-part3-troubleshooting.md](worktree-operations-maintenance-part3-troubleshooting.md)

**WHEN TO USE**: When you encounter problems with worktree operations and need solutions.

### Contents
1. Problem 1: Cannot Remove Worktree (Locked)
2. Problem 2: Worktree Path Already Exists
3. Problem 3: Cannot Rebase (Uncommitted Changes)
4. Problem 4: Force Push Rejected (--force-with-lease)
5. Problem 5: Worktree List Shows Deleted Directory
6. Problem 6: Cannot Move Worktree (Path Does Not Exist)
7. Problem 7: Rebase Conflicts Too Complex
8. Problem 8: Forgot Which Worktree Contains Which Work
9. Problem 9: Disk Space Running Low
10. Problem 10: Branch Not Tracking Remote

---

## Related References

- For basic operations (listing, switching, updating), see [worktree-operations-basic.md](worktree-operations-basic.md)
- For locking, moving, and checking status, see [worktree-operations-management.md](worktree-operations-management.md)
