# Worktree Operations Part 2: Updating Worktrees

## Table of Contents
1. [Pulling Latest Changes from Remote](#phase-1-pulling-latest-changes-from-remote)
2. [Rebasing on Main Branch](#phase-2-rebasing-on-main-branch)
3. [Handling Rebase Conflicts](#phase-3-handling-rebase-conflicts)
4. [Pushing Updated Branch](#phase-4-pushing-updated-branch)

---

## Updating Worktrees

**WHEN TO USE THIS**: When you need to get the latest changes from the remote repository into your worktree, or when you need to incorporate changes from another branch.

### Phase 1: Pulling Latest Changes from Remote

**What Pulling Does**: Downloads commits from the remote repository and integrates them into your current branch.

**Command**:
```bash
cd /path/to/worktree
git pull origin <branch-name>
```

**Example**:
```bash
# Navigate to the worktree
cd ../review-GH-42

# Pull latest changes from remote
git pull origin review/issue-42
```

**Output When Successful**:
```
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 5 (delta 2), reused 5 (delta 2)
Unpacking objects: 100% (5/5), done.
From github.com:username/repo
   a1b2c3d..e4f5g6h  review/issue-42 -> origin/review/issue-42
Updating a1b2c3d..e4f5g6h
Fast-forward
 src/component.ts | 12 ++++++++++--
 1 file changed, 10 insertions(+), 2 deletions(-)
```

**What "Fast-forward" Means**: Your local branch was simply moved forward to match the remote branch. No merge was needed because you had no local commits that weren't on the remote.

### Phase 2: Rebasing on Main Branch

**What Rebasing Does**: Moves your branch commits to start from the latest commit on the main branch, creating a linear history.

**Why Rebase Instead of Merge**:
- Creates cleaner, linear history
- Avoids unnecessary merge commits
- Makes it easier to review changes
- Simplifies future git operations

**Command**:
```bash
cd /path/to/worktree
git fetch origin
git rebase origin/main
```

**Step-by-Step Example**:
```bash
# Step 1: Navigate to worktree
cd ../review-GH-42

# Step 2: Fetch latest changes without merging
git fetch origin

# Step 3: Rebase your branch on latest main
git rebase origin/main
```

**Output When Successful**:
```
First, rewinding head to replay your work on top of it...
Applying: Add user authentication
Applying: Fix login validation
Applying: Update test suite
```

**What This Output Means**:
- Git temporarily removes your commits
- It fast-forwards your branch to match `origin/main`
- It replays your commits one by one on top of the new base

### Phase 3: Handling Rebase Conflicts

**When Conflicts Occur**: If changes on `main` conflict with your changes, git pauses the rebase and asks you to resolve conflicts.

**Conflict Output**:
```
Auto-merging src/auth.ts
CONFLICT (content): Merge conflict in src/auth.ts
error: could not apply e4f5g6h... Add user authentication
Resolve all conflicts manually, mark them as resolved with
"git add/rm <conflicted_files>", then run "git rebase --continue".
You can instead skip this commit: run "git rebase --skip".
To abort and get back to the state before "git rebase", run "git rebase --abort".
Could not apply e4f5g6h... Add user authentication
```

**Conflict Resolution Steps**:

**Step 1: Check Which Files Have Conflicts**
```bash
git status
```

Output:
```
rebase in progress; onto a1b2c3d
You are currently rebasing branch 'review/issue-42' on 'a1b2c3d'.
  (fix conflicts and then run "git rebase --continue")
  (use "git rebase --skip" to skip this patch)
  (use "git rebase --abort" to check out the original branch)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   src/auth.ts
```

**Step 2: Open Conflicted File and Resolve**

Conflicts appear with markers:
```typescript
<<<<<<< HEAD  // Changes from main branch
function authenticate(user) {
    return validateToken(user.token);
}
=======  // Your changes
function authenticate(user) {
    return verifyCredentials(user.email, user.password);
}
>>>>>>> e4f5g6h (Add user authentication)
```

**Edit the file to keep desired changes**:
```typescript
// Resolved version combining both approaches
function authenticate(user) {
    if (user.token) {
        return validateToken(user.token);
    }
    return verifyCredentials(user.email, user.password);
}
```

**Step 3: Mark Conflict as Resolved**
```bash
git add src/auth.ts
```

**Step 4: Continue Rebase**
```bash
git rebase --continue
```

**Step 5: If More Conflicts Exist, Repeat Steps 1-4**

Git will pause again if the next commit also has conflicts. Continue resolving until all commits are applied.

**Alternative: Aborting the Rebase**

If you want to cancel the rebase and return to the state before you started:
```bash
git rebase --abort
```

### Phase 4: Pushing Updated Branch

After successfully rebasing, your local branch history has changed. You need to force push to update the remote.

**Command**:
```bash
git push --force-with-lease origin review/issue-42
```

**Why `--force-with-lease` Instead of `--force`**:
- `--force-with-lease`: Only pushes if no one else has pushed to the branch since your last fetch. Prevents accidentally overwriting others' work.
- `--force`: Unconditionally overwrites remote branch. Dangerous if others are working on the same branch.

**Example**:
```bash
git push --force-with-lease origin review/issue-42
```

**Output**:
```
Enumerating objects: 12, done.
Counting objects: 100% (12/12), done.
Delta compression using up to 8 threads
Compressing objects: 100% (7/7), done.
Writing objects: 100% (8/8), 1.23 KiB | 1.23 MiB/s, done.
Total 8 (delta 5), reused 0 (delta 0)
To github.com:username/repo.git
 + e4f5g6h...a1b2c3d review/issue-42 -> review/issue-42 (forced update)
```

---

## End of Part 2

For locking and moving worktrees, see [worktree-operations-part3-locking-moving.md](worktree-operations-part3-locking-moving.md).
