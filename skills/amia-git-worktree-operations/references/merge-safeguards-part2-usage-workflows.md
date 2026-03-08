# Merge Safeguards - Part 2: Usage Workflows

## Table of Contents

- [Usage Workflows](#usage-workflows)
  - [1. Check Single Worktree Status](#1-check-single-worktree-status)
  - [2. Create Merge Plan](#2-create-merge-plan)
  - [3. Execute Merge Sequence](#3-execute-merge-sequence)
    - [Step 1: Merge First Worktree](#step-1-merge-first-worktree)
    - [Step 2: Rebase Remaining Worktrees](#step-2-rebase-remaining-worktrees)
    - [Step 3: Validate After Rebase](#step-3-validate-after-rebase)
  - [4. Detect File Conflicts](#4-detect-file-conflicts)

---

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

---

**Previous:** [Part 1: Core Concepts](merge-safeguards-part1-core-concepts.md)
**Next:** [Part 3: Validation and Advanced Scenarios](merge-safeguards-part3-validation-advanced.md)
