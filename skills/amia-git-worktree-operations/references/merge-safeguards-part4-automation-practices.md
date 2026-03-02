# Merge Safeguards - Part 4: Automation and Best Practices

## Table of Contents

- [Automation Scripts](#automation-scripts)
  - [Auto-Rebase All Worktrees](#auto-rebase-all-worktrees)
  - [Continuous Validation](#continuous-validation)
- [Best Practices](#best-practices)
  - [1. Validate Before Opening PR](#1-validate-before-opening-pr)
  - [2. Rebase Daily](#2-rebase-daily)
  - [3. Coordinate Overlapping Changes](#3-coordinate-overlapping-changes)
  - [4. Test After Each Merge](#4-test-after-each-merge)

---

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

---

**Previous:** [Part 3: Validation and Advanced Scenarios](merge-safeguards-part3-validation-advanced.md)
**Next:** [Part 5: Troubleshooting and Integration](merge-safeguards-part5-troubleshooting.md)
