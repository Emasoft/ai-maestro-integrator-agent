# Merge Safeguards - Part 1: Core Concepts

## Overview

When developing multiple features in parallel across git worktrees, merging them sequentially can create conflicts and integration issues. The merge safeguard system prevents these problems through:

1. **Conflict Detection** - Identify files modified in multiple worktrees
2. **Merge Validation** - Verify each worktree is ready to merge
3. **Optimal Ordering** - Determine best merge sequence
4. **Rebase Automation** - Keep worktrees synchronized with base branch

## Core Concepts

### Merge Status States

Each worktree can be in one of four merge states:

| Status | Description | Action Required |
|--------|-------------|-----------------|
| `CLEAN` | No conflicts, up-to-date | Safe to merge |
| `NEEDS_REBASE` | Behind base branch, no conflicts | Rebase first |
| `CONFLICTS` | Has merge conflicts | Resolve conflicts |
| `DIVERGED` | Significantly diverged from base | Manual intervention |

### File Conflicts

A **file conflict** occurs when the same file is modified in multiple worktrees. This doesn't guarantee a merge conflict, but indicates high risk.

**Example:**
```
worktrees/feature-A/: Modified src/api.py
worktrees/feature-B/: Modified src/api.py
```

When feature-A merges first, feature-B must rebase and may encounter conflicts in `src/api.py`.

### Merge Order Optimization

The system determines merge order using:

1. **Commit timestamps** - Older commits merge first
2. **Dependency analysis** - Dependencies merge before dependents
3. **Conflict minimization** - Reduce total rebases needed

**Why oldest-first?**
```
Timeline:
t0: feature-A created (first commit: Jan 1)
t1: feature-B created (first commit: Jan 5)
t2: Both features completed (Jan 10)

Merge order: A → B
- A merges cleanly
- B rebases once, conflicts resolved
- Total rebases: 1

Reverse order: B → A
- B merges cleanly
- A rebases, finds conflicts with B
- A may need multiple rebases if B introduced breaking changes
- Total rebases: 1-3
```

---

**Next:** [Part 2: Usage Workflows](merge-safeguards-part2-usage-workflows.md)
