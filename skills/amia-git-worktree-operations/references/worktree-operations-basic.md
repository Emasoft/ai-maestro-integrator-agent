# Worktree Operations: Basic Operations

## Table of Contents
1. [When you need to see all active worktrees → Listing Worktrees](#listing-worktrees)
2. [If you need to work in a different worktree → Switching Between Worktrees](#switching-between-worktrees)
3. [When you need to get latest changes → Updating Worktrees](#updating-worktrees)

---

## Listing Worktrees

**WHEN TO USE THIS**: When you need to see all active worktrees in your repository, their locations, branches, and commit states.

### Basic Listing

**Command**:
```bash
git worktree list
```

**What This Does**: Displays all worktrees in a human-readable format with three columns:
1. **Worktree Path**: The absolute filesystem path to the worktree directory
2. **Commit Hash**: The shortened SHA hash of the current commit (first 7 characters)
3. **Branch Name**: The branch currently checked out in that worktree

**Example Output**:
```
/Users/username/myproject        a1b2c3d [main]
/Users/username/review-GH-42     e4f5g6h [review/issue-42]
/Users/username/hotfix-login     i7j8k9l [hotfix/login-bug]
```

**Interpreting the Output**:
- First line shows the main repository worktree (where the `.git` directory lives)
- Subsequent lines show additional worktrees
- Branch names in square brackets indicate active branches
- If a worktree is detached (not on any branch), you will see `(detached HEAD)` instead of a branch name

### Machine-Readable Listing

**Command**:
```bash
git worktree list --porcelain
```

**What This Does**: Outputs worktree information in a structured, machine-parseable format. Each worktree is represented by a block of key-value pairs separated by blank lines.

**Example Output**:
```
worktree /Users/username/myproject
HEAD a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
branch refs/heads/main

worktree /Users/username/review-GH-42
HEAD e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3
branch refs/heads/review/issue-42

worktree /Users/username/hotfix-login
HEAD i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6
branch refs/heads/hotfix/login-bug
locked working tree has a lock file
```

**Field Definitions**:
- `worktree`: Absolute path to the worktree directory
- `HEAD`: Full 40-character SHA hash of the current commit
- `branch`: Full reference path to the branch (starts with `refs/heads/`)
- `locked`: Present only if the worktree is locked, includes the lock reason if provided
- `prunable`: Present only if the worktree is prunable (missing or corrupted)

**When to Use Porcelain Format**:
- Writing scripts that need to parse worktree information
- Automating worktree management tasks
- Integrating with other tools or continuous integration systems
- Generating reports or dashboards

---

## Switching Between Worktrees

**WHEN TO USE THIS**: When you need to work in a different worktree without closing your current session or losing your working state.

### How Switching Works

Git worktrees are **separate directories** on your filesystem. Switching between them means **changing your current working directory** using your shell, not using git commands.

### Method 1: Using cd (Change Directory)

**Command**:
```bash
cd /path/to/worktree
```

**Example**:
```bash
# Currently in main worktree
pwd
# Output: /Users/username/myproject

# Switch to review worktree
cd ../review-GH-42

# Verify new location
pwd
# Output: /Users/username/review-GH-42

# Check which branch you're on
git branch --show-current
# Output: review/issue-42
```

### Method 2: Using Absolute Paths

**Command**:
```bash
cd /absolute/path/to/worktree
```

**Example**:
```bash
# Switch using absolute path
cd /Users/username/review-GH-42

# This works from anywhere in your filesystem
```

### Method 3: Creating Shell Aliases for Quick Switching

**Setup** (add to your `~/.bashrc` or `~/.zshrc`):
```bash
# Define aliases for common worktrees
alias goto-main='cd /Users/username/myproject'
alias goto-review='cd /Users/username/review-GH-42'
alias goto-hotfix='cd /Users/username/hotfix-login'
```

**Usage**:
```bash
# Switch to review worktree instantly
goto-review

# Switch back to main
goto-main
```

### Method 4: Using CDPATH Environment Variable

**Setup** (add to your `~/.bashrc` or `~/.zshrc`):
```bash
# Add parent directory of worktrees to CDPATH
export CDPATH=".:$HOME:$HOME/Code"
```

**Usage**:
```bash
# If worktrees are in /Users/username/Code/
cd review-GH-42  # Works from anywhere!
```

### Important Notes

1. **Each Worktree is Independent**: When you switch worktrees, you are switching to a completely separate working directory with its own:
   - Checked out files
   - Branch state
   - Index (staging area)
   - Uncommitted changes

2. **Terminal Sessions**: Each terminal window/tab operates in one directory at a time. To work in multiple worktrees simultaneously:
   - Open multiple terminal windows
   - Use terminal multiplexers (tmux, screen)
   - Use IDE with multiple terminal panes

3. **File Changes Are Isolated**: Changes made in one worktree do not affect files in other worktrees until you commit and merge branches.

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

## Related References

- For locking, moving, and checking worktree status, see [worktree-operations-management.md](worktree-operations-management.md)
- For syncing with main branch, best practices, and troubleshooting, see [worktree-operations-maintenance.md](worktree-operations-maintenance.md)
