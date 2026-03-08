# Merge Safeguards - Part 3: Validation and Advanced Scenarios

## Table of Contents

- [Pre-Merge Validation Checklist](#pre-merge-validation-checklist)
- [Advanced Scenarios](#advanced-scenarios)
  - [Multiple Sequential Merges](#multiple-sequential-merges)
  - [Conflict Resolution Workflow](#conflict-resolution-workflow)
  - [Detecting Breaking Changes](#detecting-breaking-changes)

---

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

## Advanced Scenarios

### Multiple Sequential Merges

When merging 5+ worktrees:

```bash
# 1. Create plan
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --plan --output merge-plan.json

# 2. Iterate through merge order
for worktree in $(jq -r '.merge_order[]' merge-plan.json); do
    echo "=== Processing $worktree ==="

    # Validate
    python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
        --validate "$worktree"

    if [ $? -ne 0 ]; then
        echo "Validation failed, skipping"
        continue
    fi

    # Get PR number (from branch name or registry)
    pr_num=$(gh pr list --head "$(basename $worktree)" --json number -q '.[0].number')

    # Merge PR
    gh pr merge "$pr_num" --squash

    # Update main
    git checkout main && git pull

    # Rebase remaining worktrees
    # (continue loop)
done
```

### Conflict Resolution Workflow

When rebasing encounters conflicts:

```bash
cd worktrees/feature-auth
git rebase origin/main

# Conflict in src/api.py
# <<<<<<< HEAD
# Your changes
# =======
# Changes from main
# >>>>>>> origin/main

# 1. Open file in editor, resolve conflict
# 2. Remove conflict markers
# 3. Stage resolved file
git add src/api.py

# 4. Continue rebase
git rebase --continue

# 5. Push force (required after rebase)
git push --force-with-lease
```

### Detecting Breaking Changes

After each merge, test remaining worktrees:

```bash
# After merging feature-api-v2
cd worktrees/feature-auth

# Rebase to get latest main
git rebase origin/main

# Run tests
npm test
# or
pytest

# If tests fail:
# - feature-api-v2 introduced breaking changes
# - Update feature-auth to adapt
# - Commit fixes
# - Continue merge sequence
```

---

**Previous:** [Part 2: Usage Workflows](merge-safeguards-part2-usage-workflows.md)
**Next:** [Part 4: Automation and Best Practices](merge-safeguards-part4-automation-practices.md)
