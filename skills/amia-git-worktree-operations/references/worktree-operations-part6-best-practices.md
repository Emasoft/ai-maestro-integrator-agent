# Worktree Operations Part 6: Best Practices

## Table of Contents
1. [Keep Worktrees Updated](#practice-1-keep-worktrees-updated)
2. [Clean Working Tree Before Switching](#practice-2-clean-working-tree-before-switching)
3. [Use Meaningful Worktree Names](#practice-3-use-meaningful-worktree-names)
4. [Lock Worktrees When In Active Use](#practice-4-lock-worktrees-when-in-active-use)
5. [Remove Completed Worktrees Promptly](#practice-5-remove-completed-worktrees-promptly)
6. [Prune Stale Worktrees Regularly](#practice-6-prune-stale-worktrees-regularly)
7. [Document Worktree Purpose](#practice-7-document-worktree-purpose)

---

## Best Practices

### Practice 1: Keep Worktrees Updated

**Why**: Prevents large, difficult merge conflicts and keeps your work compatible with latest codebase changes.

**How**:
```bash
# Daily routine for each active worktree
cd /path/to/worktree
git fetch origin
git rebase origin/main
git push --force-with-lease origin <branch-name>
```

**Automation Idea**:
Create a shell script `~/bin/sync-worktrees.sh`:
```bash
#!/bin/bash
WORKTREES=$(git worktree list --porcelain | grep '^worktree' | cut -d' ' -f2)

for worktree in $WORKTREES; do
    echo "Syncing $worktree..."
    cd "$worktree"

    # Skip if worktree has uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        echo "  Skipping (has uncommitted changes)"
        continue
    fi

    git fetch origin
    git rebase origin/main && git push --force-with-lease
done
```

### Practice 2: Clean Working Tree Before Switching

**Why**: Prevents confusion about which changes belong to which worktree.

**How**:
```bash
# Before switching to another worktree:

# Option A: Commit your changes
git add .
git commit -m "WIP: <description of current work>"

# Option B: Stash your changes
git stash push -m "WIP on <feature name>"

# Then switch
cd /path/to/other/worktree
```

### Practice 3: Use Meaningful Worktree Names

**Bad Names** (vague, hard to remember):
```bash
git worktree add ../wt1 review/issue-42
git worktree add ../temp hotfix/bug
git worktree add ../new-feature feature/auth
```

**Good Names** (descriptive, self-documenting):
```bash
git worktree add ../review-auth-refactor review/issue-42
git worktree add ../hotfix-login-timeout hotfix/bug-login
git worktree add ../feature-oauth-integration feature/auth
```

**Naming Convention Recommendation**:
```
<purpose>-<description>

Examples:
review-GH-42            # For reviewing GitHub issue #42
hotfix-login-bug        # For urgent login bug fix
feature-oauth           # For OAuth feature development
experiment-new-db       # For experimental database changes
test-ci-pipeline        # For testing CI/CD changes
```

### Practice 4: Lock Worktrees When In Active Use

**Why**: Prevents accidental deletion and signals to others (or your future self) that the worktree is important.

**When to Lock**:
- Starting a multi-day code review
- Working on a worktree located on a removable drive
- Worktree contains experiments you want to preserve
- Shared worktree being used by multiple people

**How**:
```bash
# Lock with descriptive reason
git worktree lock ../review-GH-42 --reason "3-day security audit in progress"

# Unlock when done
git worktree unlock ../review-GH-42
```

### Practice 5: Remove Completed Worktrees Promptly

**Why**: Reduces clutter, prevents confusion, frees disk space.

**When to Remove**:
- After PR is merged
- After branch is deleted
- After review is complete
- After hotfix is deployed

**How**:
```bash
# Step 1: Verify work is committed and pushed
cd ../review-GH-42
git status
git log origin/review/issue-42..HEAD  # Should show nothing

# Step 2: Navigate back to main repo
cd /path/to/main/repo

# Step 3: Remove worktree
git worktree remove ../review-GH-42
```

### Practice 6: Prune Stale Worktrees Regularly

**Why**: Removes git metadata for worktrees that were manually deleted.

**How**:
```bash
# Check for prunable worktrees
git worktree list

# Prune stale entries
git worktree prune

# Dry run to see what would be pruned
git worktree prune --dry-run
```

### Practice 7: Document Worktree Purpose

**Method 1: Lock Reason**:
```bash
git worktree lock ../review-GH-42 --reason "Reviewing authentication refactor"
```

**Method 2: README in Worktree**:
```bash
cd ../review-GH-42
echo "Purpose: Review authentication refactor for PR #42" > WORKTREE_README.md
echo "Owner: Alice" >> WORKTREE_README.md
echo "Created: 2025-12-31" >> WORKTREE_README.md
```

**Method 3: Branch Naming**:
```bash
# Branch name itself documents purpose
git worktree add ../review-auth-pr42 review/auth-refactor-pr42
```

---

## End of Part 6

For troubleshooting worktree issues, see [worktree-operations-part7-troubleshooting.md](worktree-operations-part7-troubleshooting.md).
