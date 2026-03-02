# Worktree Operations Part 5: Syncing with Main Branch

## Table of Contents
1. [Why Sync Regularly](#why-sync-regularly)
2. [Fetch Latest Main](#phase-1-fetch-latest-main)
3. [Verify Current State](#phase-2-verify-current-state)
4. [Rebase on Origin/Main](#phase-3-rebase-on-originmain)
5. [Handling Rebase Conflicts](#phase-4-handling-rebase-conflicts-if-they-occur)
6. [Force Push Updated Branch](#phase-5-force-push-updated-branch)
7. [Restoring Stashed Changes](#phase-6-if-you-stashed-changes-earlier)
8. [Complete Sync Workflow Example](#complete-sync-workflow-example)

---

## Syncing with Main Branch

**WHEN TO USE THIS**: When you need to incorporate the latest changes from the main branch into your worktree branch to keep it up to date and avoid large merge conflicts later.

### Why Sync Regularly

**Benefits of Regular Syncing**:
- Smaller, easier-to-resolve conflicts
- Your code works with latest main branch changes
- Easier for reviewers to review (clean diff against current main)
- Reduces integration problems when merging back to main
- Catches breaking changes early

**Recommended Frequency**: Sync at least once per day when actively working on a branch.

### Phase 1: Fetch Latest Main

**What Fetching Does**: Downloads commits from remote repository without changing your local files.

**Command**:
```bash
cd /path/to/worktree
git fetch origin
```

**Example**:
```bash
cd ../review-GH-42
git fetch origin
```

**Output**:
```
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (15/15), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 12 (delta 7), reused 10 (delta 5)
Unpacking objects: 100% (12/12), done.
From github.com:username/repo
   a1b2c3d..m4n5o6p  main       -> origin/main
   e4f5g6h..q7r8s9t  review/issue-42 -> origin/review/issue-42
```

**What This Output Means**:
- Main branch on remote has new commits (`a1b2c3d..m4n5o6p`)
- Your review branch on remote also has new commits
- Nothing has changed in your local files yet

### Phase 2: Verify Current State

**Check if you have uncommitted changes**:
```bash
git status
```

**If You Have Uncommitted Changes**:

**Option A: Commit Them**:
```bash
git add .
git commit -m "Work in progress before sync"
```

**Option B: Stash Them**:
```bash
git stash push -m "WIP before syncing with main"
```

**Why This Matters**: Rebasing requires a clean working tree. You must either commit or stash changes before rebasing.

### Phase 3: Rebase on Origin/Main

**Command**:
```bash
git rebase origin/main
```

**Example**:
```bash
cd ../review-GH-42
git rebase origin/main
```

**Output When Successful**:
```
First, rewinding head to replay your work on top of it...
Applying: Add user authentication
Applying: Fix login validation
Applying: Update test suite
```

**What Happened**:
1. Git identified the commits unique to your branch (not in main)
2. Git moved your branch pointer to match `origin/main`
3. Git replayed your commits one by one on top of the new base
4. Your branch now includes all main branch changes plus your changes

### Phase 4: Handling Rebase Conflicts (If They Occur)

**Conflict Detection Output**:
```
Auto-merging src/auth.ts
CONFLICT (content): Merge conflict in src/auth.ts
error: could not apply e4f5g6h... Add user authentication
Resolve all conflicts manually, mark them as resolved with
"git add/rm <conflicted_files>", then run "git rebase --continue".
```

**Step 1: Identify Conflicted Files**:
```bash
git status
```

**Output**:
```
rebase in progress; onto m4n5o6p
You are currently rebasing branch 'review/issue-42' on 'm4n5o6p'.
  (fix conflicts and then run "git rebase --continue")

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   src/auth.ts
```

**Step 2: Open and Resolve Conflicts**:

Open `src/auth.ts` in your editor. You will see:
```typescript
<<<<<<< HEAD  // Code from origin/main
function authenticate(user) {
    return newAuthSystem(user);
}
=======  // Your code
function authenticate(user) {
    return oldAuthSystem(user.email, user.password);
}
>>>>>>> e4f5g6h (Add user authentication)
```

**Edit to resolve** (keep what you need):
```typescript
function authenticate(user) {
    // Updated to use new auth system from main
    return newAuthSystem(user);
}
```

**Step 3: Mark as Resolved**:
```bash
git add src/auth.ts
```

**Step 4: Continue Rebase**:
```bash
git rebase --continue
```

**Step 5: Repeat if More Conflicts**:

If the next commit also conflicts, git will pause again. Repeat steps 1-4 until all commits are applied.

### Phase 5: Force Push Updated Branch

**Why Force Push is Needed**: Rebasing rewrites commit history. The remote branch has the old commits, so you must force push to replace them.

**Safe Force Push Command**:
```bash
git push --force-with-lease origin review/issue-42
```

**Why `--force-with-lease`**: Only pushes if no one else has pushed since your last fetch. Prevents overwriting others' work.

**Example**:
```bash
git push --force-with-lease origin review/issue-42
```

**Output**:
```
Enumerating objects: 18, done.
Counting objects: 100% (18/18), done.
Delta compression using up to 8 threads
Compressing objects: 100% (12/12), done.
Writing objects: 100% (14/14), 2.34 KiB | 2.34 MiB/s, done.
Total 14 (delta 8), reused 0 (delta 0)
To github.com:username/repo.git
 + e4f5g6h...n8o9p0q review/issue-42 -> review/issue-42 (forced update)
```

### Phase 6: If You Stashed Changes Earlier

**Restore Stashed Changes**:
```bash
git stash pop
```

**What This Does**: Applies your stashed changes back to the working tree and removes them from the stash.

**If Stash Conflicts with Rebased Code**:
```
Auto-merging src/auth.ts
CONFLICT (content): Merge conflict in src/auth.ts
```

**Resolution Steps** (same as rebase conflicts):
1. Open conflicted files
2. Resolve conflicts
3. `git add <file>`
4. `git stash drop` (to clear the stash entry)

### Complete Sync Workflow Example

```bash
# Step 1: Navigate to worktree
cd ../review-GH-42

# Step 2: Check for uncommitted changes
git status

# Step 3: Stash if needed
git stash push -m "WIP before sync"

# Step 4: Fetch latest from remote
git fetch origin

# Step 5: Rebase on main
git rebase origin/main

# Step 6: Force push if successful
git push --force-with-lease origin review/issue-42

# Step 7: Restore stashed changes
git stash pop
```

---

## End of Part 5

For best practices on worktree management, see [worktree-operations-part6-best-practices.md](worktree-operations-part6-best-practices.md).
