# Merge Safeguards - Part 2: Advanced Topics

## Table of Contents

1. [If you need advanced merge techniques → Advanced Scenarios](#advanced-scenarios)
   - [When merging multiple worktrees → Multiple Sequential Merges](#multiple-sequential-merges)
   - [If resolving conflicts → Conflict Resolution Workflow](#conflict-resolution-workflow)
   - [When checking for breaking changes → Detecting Breaking Changes](#detecting-breaking-changes)
2. [When automating merge operations → Automation Scripts](#automation-scripts)
   - [If rebasing all worktrees → Auto-Rebase All Worktrees](#auto-rebase-all-worktrees)
   - [When running continuous checks → Continuous Validation](#continuous-validation)
3. [If you need merge guidelines → Best Practices](#best-practices)
4. [When you encounter merge problems → Troubleshooting](#troubleshooting)
5. [If integrating with worktree lifecycle → Integration with Worktree Lifecycle](#integration-with-worktree-lifecycle)
6. [When you need related documentation → See Also](#see-also)

---

**Prerequisites:** Read [merge-safeguards-part1-fundamentals.md](merge-safeguards-part1-fundamentals.md) first for core concepts and basic workflows.

---

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

## Automation Scripts

### Auto-Rebase All Worktrees

```bash
#!/bin/bash
# auto-rebase.sh

for worktree in worktrees/*; do
    if [ -d "$worktree/.git" ]; then
        echo "Rebasing $(basename $worktree)..."
        python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
            --rebase "$worktree"

        if [ $? -ne 0 ]; then
            echo "⚠ Rebase failed for $(basename $worktree)"
            echo "Manual intervention required"
            exit 1
        fi
    fi
done

echo "✓ All worktrees rebased successfully"
```

### Continuous Validation

```bash
#!/bin/bash
# validate-all.sh

failed=0

for worktree in worktrees/*; do
    if [ -d "$worktree/.git" ]; then
        python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
            --validate "$worktree" > /dev/null 2>&1

        if [ $? -ne 0 ]; then
            echo "✗ $(basename $worktree) - validation failed"
            failed=$((failed + 1))
        else
            echo "✓ $(basename $worktree) - ready to merge"
        fi
    fi
done

if [ $failed -gt 0 ]; then
    echo ""
    echo "$failed worktree(s) failed validation"
    exit 1
fi

echo ""
echo "All worktrees validated successfully"
```

## Best Practices

### 1. Validate Before Opening PR

```bash
# Before `gh pr create`:
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --validate worktrees/my-feature

# Fix any issues, then create PR
```

### 2. Rebase Daily

Keep worktrees synchronized to minimize conflicts:

```bash
# Daily workflow
git checkout main && git pull
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/my-feature
```

### 3. Coordinate Overlapping Changes

If file conflicts detected:

```bash
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py --conflicts

# Output shows src/api.py modified in 2 worktrees
# → Coordinate with other developer
# → Determine merge order
# → Second developer rebases after first merges
```

### 4. Test After Each Merge

```bash
# After merging PR #123
git checkout main && git pull

# Rebase active worktrees
for wt in worktrees/*; do
    cd "$wt"
    git rebase origin/main
    npm test  # or pytest
    cd -
done
```

## Troubleshooting

### Issue: Rebase Fails with Conflicts

**Symptom:**

```bash
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/feature-auth

# ✗ Rebase failed: CONFLICT (content): Merge conflict in src/api.py
```

**Solution:**

```bash
cd worktrees/feature-auth

# Manually resolve conflicts
git status  # See conflicted files
# Edit files, resolve conflicts
git add .
git rebase --continue

# Verify resolution
python ../scripts/merge_safeguard.py --validate .
```

### Issue: Validation Shows "Behind Remote"

**Symptom:**

```
✗ Validation failed for feature-auth:
  - Branch is 2 commits behind remote
```

**Solution:**

```bash
cd worktrees/feature-auth
git pull --rebase
```

### Issue: Multiple Conflicting Files

**Symptom:**

```
File Conflicts:
  src/api.py: modified in feature-A, feature-B, feature-C
```

**Solution:**

```bash
# Merge in sequence, rebase between each
# 1. Merge feature-A
gh pr merge 123

# 2. Rebase feature-B and feature-C
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/feature-B
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/feature-C

# 3. Test both
cd worktrees/feature-B && npm test
cd worktrees/feature-C && npm test

# 4. Merge feature-B
gh pr merge 124

# 5. Rebase feature-C again
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --rebase worktrees/feature-C
```

## Integration with Worktree Lifecycle

### During Creation

```bash
# Creating new worktree
python skills/amia-git-worktree-operations/scripts/worktree_create.py \
    --name feature-api-v3

# Immediately check status
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --check worktrees/feature-api-v3

# Should show: Status: clean (newly created)
```

### Before Removal

```bash
# Before removing worktree, ensure changes merged
python skills/amia-git-worktree-operations/scripts/merge_safeguard.py \
    --validate worktrees/feature-old

# If not merged, create PR first
cd worktrees/feature-old
gh pr create --fill

# After PR merged, safe to remove
python skills/amia-git-worktree-operations/scripts/worktree_remove.py \
    --name feature-old
```

## See Also

- **Part 1 Fundamentals**: [merge-safeguards-part1-fundamentals.md](merge-safeguards-part1-fundamentals.md)
- **Worktree Creation**: [creating-worktrees.md](creating-worktrees.md)
- **Worktree Removal**: [removing-worktrees-index.md](removing-worktrees-index.md)
- **Port Management**: [port-allocation.md](port-allocation.md)
- **Registry Format**: [registry-system-part1-schema.md](registry-system-part1-schema.md)
