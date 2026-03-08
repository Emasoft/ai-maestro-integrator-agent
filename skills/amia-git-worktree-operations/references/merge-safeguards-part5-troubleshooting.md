# Merge Safeguards - Part 5: Troubleshooting and Integration

## Table of Contents

- [Troubleshooting](#troubleshooting)
  - [Issue: Rebase Fails with Conflicts](#issue-rebase-fails-with-conflicts)
  - [Issue: Validation Shows "Behind Remote"](#issue-validation-shows-behind-remote)
  - [Issue: Multiple Conflicting Files](#issue-multiple-conflicting-files)
- [Integration with Worktree Lifecycle](#integration-with-worktree-lifecycle)
  - [During Creation](#during-creation)
  - [Before Removal](#before-removal)
- [See Also](#see-also)

---

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

- **Worktree Creation**: `worktree-creation.md`
- **Worktree Removal**: `worktree-removal.md`
- **Port Management**: `port-allocation.md`
- **Registry Format**: `registry-format.md`

---

**Previous:** [Part 4: Automation and Best Practices](merge-safeguards-part4-automation-practices.md)
**Back to Index:** [Merge Safeguards](merge-safeguards.md)
