# Merge Safeguards - Part 1: Fundamentals

## Table of Contents

1. [When you need to understand merge safeguards → Overview](#overview)
2. [If you need fundamental merge concepts → Core Concepts](#core-concepts)
   - [When understanding worktree states → Merge Status States](#merge-status-states)
   - [If detecting file conflicts → File Conflicts](#file-conflicts)
   - [When optimizing merge order → Merge Order Optimization](#merge-order-optimization)
3. [When you need to perform merge workflows → Usage Workflows](#usage-workflows)
   - [If checking a single worktree → 1. Check Single Worktree Status](#1-check-single-worktree-status)
   - [When planning multiple merges → 2. Create Merge Plan](#2-create-merge-plan)
   - [If executing the merge plan → 3. Execute Merge Sequence](#3-execute-merge-sequence)
   - [When finding file conflicts → 4. Detect File Conflicts](#4-detect-file-conflicts)
4. [Before merging any worktree → Pre-Merge Validation Checklist](#pre-merge-validation-checklist)
5. [For advanced topics → See Part 2](#see-part-2)

---

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

## Usage Workflows

### 1. Check Single Worktree Status

Before opening a PR, verify the worktree can merge cleanly:

```bash
cd /project-root
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --check worktrees/feature-api-v2

# Output:
# Merge Status for feature-api-v2:
#   Branch: feature/api-v2
#   Commits ahead of main: 12
#   Commits behind main: 3
#   Status: needs_rebase
#   Conflicting files: []
```

**Interpretation:**

- `needs_rebase` - Rebase before merging
- No conflicting files - Rebase should be clean

### 2. Create Merge Plan

When multiple PRs are ready, create a merge plan:

```bash
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py --plan

# Output:
# === MERGE PLAN ===
#
# Merge Order:
#   1. worktrees/feature-api-v2
#   2. worktrees/feature-auth
#   3. worktrees/feature-dashboard
#
# CONFLICTS DETECTED:
#   src/api.py: modified in feature-api-v2, feature-auth
#   src/types.ts: modified in feature-api-v2, feature-dashboard
#
# RECOMMENDED STRATEGY:
# 1. Merge worktrees one at a time
# 2. After each merge, rebase remaining worktrees
# 3. Resolve conflicts in each rebase before proceeding
# 4. Run tests after each merge to catch integration issues
```

### 3. Execute Merge Sequence

Follow the plan:

#### Step 1: Merge First Worktree

```bash
# Validate
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --validate worktrees/feature-api-v2

# Merge PR on GitHub
gh pr merge 123 --squash

# Update local main
git checkout main
git pull
```

#### Step 2: Rebase Remaining Worktrees

```bash
# Rebase second worktree
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/feature-auth

# If conflicts occur:
cd worktrees/feature-auth
git status  # See conflicted files
# Resolve conflicts manually
git add .
git rebase --continue

# Rebase third worktree
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/feature-dashboard
```

#### Step 3: Validate After Rebase

```bash
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --validate worktrees/feature-auth
# ✓ Worktree feature-auth is ready for merge

# Merge second PR
gh pr merge 124 --squash
```

### 4. Detect File Conflicts

See which files are modified across multiple worktrees:

```bash
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py --conflicts

# Output:
# === FILE CONFLICTS ===
#
# src/api.py:
#   - feature-api-v2
#   - feature-auth
#
# src/types.ts:
#   - feature-api-v2
#   - feature-dashboard
```

**Use this to:**

- Identify high-risk files before merging
- Coordinate with other developers
- Split large PRs to reduce conflicts

## Pre-Merge Validation Checklist

The validator checks:

```
✓ Clean working directory (no uncommitted changes)
✓ Up-to-date with remote branch
✓ No merge conflicts with base branch
✓ Tests pass (if test command configured)
```

**Example validation failure:**

```bash
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --validate worktrees/feature-auth

# ✗ Validation failed for feature-auth:
#   - Uncommitted changes: 3 files
#   - Branch is 2 commits behind remote
#   - Merge conflicts detected: 1 files
```

**Resolution:**

```bash
cd worktrees/feature-auth

# Commit changes
git add .
git commit -m "Complete auth implementation"

# Sync with remote
git pull --rebase

# Resolve conflicts
python ../scripts/merge_safeguard.py --rebase .
```

---

## See Part 2

For advanced topics, see [merge-safeguards-part2-advanced.md](merge-safeguards-part2-advanced.md):

- Multiple Sequential Merges
- Conflict Resolution Workflow
- Detecting Breaking Changes
- Automation Scripts (Auto-Rebase, Continuous Validation)
- Best Practices
- Troubleshooting
- Integration with Worktree Lifecycle
