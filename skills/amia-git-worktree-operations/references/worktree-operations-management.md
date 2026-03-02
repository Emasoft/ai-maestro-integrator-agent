# Worktree Operations: Management

## Table of Contents
1. [If you need to protect a worktree from deletion → Locking and Unlocking Worktrees](#locking-and-unlocking-worktrees)
2. [When you need to relocate a worktree → Moving Worktrees](#moving-worktrees)
3. [If you need to check worktree state → Checking Worktree Status](#checking-worktree-status)

---

## Locking and Unlocking Worktrees

**WHEN TO USE THIS**: When you want to prevent a worktree from being accidentally removed or pruned, especially when it is under active use or located on a removable drive.

### What Locking Does

Locking a worktree creates a lock file (`.git/worktrees/<worktree-name>/locked`) that:
- Prevents `git worktree prune` from removing the worktree
- Prevents `git worktree remove` from deleting the worktree
- Serves as a signal to other users that the worktree is in use

**Lock file does NOT**:
- Prevent git operations within the worktree (commits, pulls, etc. still work)
- Lock files from being edited
- Prevent manual deletion of the worktree directory

### Locking a Worktree

**Basic Lock Command**:
```bash
git worktree lock /path/to/worktree
```

**Example**:
```bash
git worktree lock ../review-GH-42
```

**Output**:
```
(no output means success)
```

**Lock with Reason**:
```bash
git worktree lock ../review-GH-42 --reason "Under active code review - do not remove"
```

**Why Provide a Reason**:
- Documents why the worktree is locked
- Helps team members understand the lock
- Appears in `git worktree list --porcelain` output
- Serves as a reminder for yourself

### Unlocking a Worktree

**Command**:
```bash
git worktree unlock /path/to/worktree
```

**Example**:
```bash
git worktree unlock ../review-GH-42
```

**Output**:
```
(no output means success)
```

### Checking Lock Status

**Method 1: Using `git worktree list --porcelain`**
```bash
git worktree list --porcelain
```

**Output for Locked Worktree**:
```
worktree /Users/username/review-GH-42
HEAD e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3
branch refs/heads/review/issue-42
locked Under active code review - do not remove
```

**Method 2: Manually Check Lock File**
```bash
cat .git/worktrees/review-GH-42/locked
```

**Output**:
```
Under active code review - do not remove
```

### Common Use Cases

**Use Case 1: Protecting Active Work**
```bash
# Lock worktree before starting multi-day review
git worktree lock ../review-GH-42 --reason "Multi-day code review in progress"
```

**Use Case 2: Removable Drive Worktrees**
```bash
# Lock worktree on external drive
git worktree lock /Volumes/ExternalDrive/hotfix-urgent --reason "On removable drive"
```

**Use Case 3: Shared Team Worktrees**
```bash
# Lock worktree in shared location
git worktree lock /shared/team-review --reason "Team review session - Alice leading"
```

---

## Moving Worktrees

**WHEN TO USE THIS**: When you need to relocate a worktree to a different directory without losing your work or having to recreate the worktree.

### What Moving Does

The `git worktree move` command:
- Physically moves the worktree directory to a new location
- Updates git internal references to point to the new location
- Preserves all commits, branches, and working changes
- Updates the worktree registry in `.git/worktrees/`

**What Moving Does NOT Do**:
- Change the branch checked out in the worktree
- Modify any commits or file contents
- Affect other worktrees

### Basic Move Command

**Syntax**:
```bash
git worktree move <old-path> <new-path>
```

**Example**:
```bash
# Move worktree from current location to new location
git worktree move ../review-GH-42 ../reviews/issue-42
```

**What This Does**:
1. Verifies the old path exists and is a valid worktree
2. Verifies the new path does not already exist
3. Moves the entire directory tree
4. Updates `.git/worktrees/<name>/gitdir` to point to new location
5. Reports success

**Output When Successful**:
```
(no output means success)
```

### Moving Locked Worktrees

**Error When Moving Locked Worktree**:
```bash
git worktree move ../review-GH-42 ../new-location
```

**Output**:
```
fatal: 'review-GH-42' is locked
```

**Solution: Unlock First, Then Move**:
```bash
# Step 1: Unlock
git worktree unlock ../review-GH-42

# Step 2: Move
git worktree move ../review-GH-42 ../new-location

# Step 3: Lock again if needed
git worktree lock ../new-location --reason "Moved and locked"
```

### Common Move Scenarios

**Scenario 1: Reorganizing Worktree Structure**
```bash
# Create organized directory structure
mkdir -p ../worktrees/reviews
mkdir -p ../worktrees/hotfixes

# Move review worktrees
git worktree move ../review-GH-42 ../worktrees/reviews/issue-42
git worktree move ../review-GH-55 ../worktrees/reviews/issue-55

# Move hotfix worktrees
git worktree move ../hotfix-login ../worktrees/hotfixes/login-bug
```

**Scenario 2: Moving to Faster Drive**
```bash
# Move worktree from HDD to SSD for better performance
git worktree move /Volumes/SlowDrive/review-GH-42 /Volumes/SSD/review-GH-42
```

**Scenario 3: Renaming Worktree Directory**
```bash
# Rename worktree for clarity
git worktree move ../review-GH-42 ../review-auth-refactor
```

### Verifying Successful Move

**Check Worktree List**:
```bash
git worktree list
```

**Expected Output**:
```
/Users/username/myproject           a1b2c3d [main]
/Users/username/new-location        e4f5g6h [review/issue-42]
```

**Navigate and Verify**:
```bash
cd ../new-location
git status
git branch --show-current
```

---

## Checking Worktree Status

**WHEN TO USE THIS**: When you need to understand the current state of a worktree: what files are modified, what is staged, whether commits need to be pushed, or if the branch is up to date with remote.

### Phase 1: Basic Status Check

**Command**:
```bash
cd /path/to/worktree
git status
```

**Example**:
```bash
cd ../review-GH-42
git status
```

**Output When Clean**:
```
On branch review/issue-42
Your branch is up to date with 'origin/review/issue-42'.

nothing to commit, working tree clean
```

**What This Means**:
- Currently on branch `review/issue-42`
- Local branch matches remote branch (same commit)
- No modified files
- No staged changes

**Output With Changes**:
```
On branch review/issue-42
Your branch is ahead of 'origin/review/issue-42' by 2 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   src/auth.ts
        modified:   src/utils.ts

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        src/newfeature.ts

no changes added to commit (use "git add" and/or "git commit -a")
```

**Interpreting This Output**:
- You have 2 local commits not yet pushed to remote
- `src/auth.ts` and `src/utils.ts` have uncommitted modifications
- `src/newfeature.ts` is a new file not yet tracked by git
- Nothing is currently staged for commit

### Phase 2: Checking Modified Files in Detail

**Command to See What Changed**:
```bash
git diff
```

**What This Shows**: Line-by-line differences for all modified files (not staged).

**Example Output**:
```diff
diff --git a/src/auth.ts b/src/auth.ts
index a1b2c3d..e4f5g6h 100644
--- a/src/auth.ts
+++ b/src/auth.ts
@@ -10,7 +10,7 @@ export function authenticate(user: User) {
     if (!user.email || !user.password) {
-        throw new Error('Missing credentials');
+        throw new Error('Email and password are required');
     }
     return validateUser(user);
 }
```

**Reading the Diff**:
- Lines starting with `-` were removed
- Lines starting with `+` were added
- `@@ -10,7 +10,7 @@` shows line numbers (old file, new file)

**Command to See Staged Changes**:
```bash
git diff --staged
```

**What This Shows**: Differences for files already staged with `git add`.

### Phase 3: Checking Commit Status

**Command to See Recent Commits**:
```bash
git log --oneline -5
```

**What This Shows**: Last 5 commits in compact format.

**Example Output**:
```
e4f5g6h (HEAD -> review/issue-42) Fix login validation
c7d8e9f Add user authentication
a1b2c3d (origin/main, main) Update README
```

**Reading the Output**:
- `e4f5g6h`: Commit hash (shortened)
- `(HEAD -> review/issue-42)`: Current branch pointer
- `Fix login validation`: Commit message
- `(origin/main, main)`: Branch references

**Command to See Commit Details**:
```bash
git show <commit-hash>
```

**Example**:
```bash
git show e4f5g6h
```

**Output**: Shows full commit message, author, date, and diff.

### Phase 4: Checking Upstream Tracking

**Command**:
```bash
git branch -vv
```

**What This Shows**: All local branches with their upstream tracking information.

**Example Output**:
```
  main           a1b2c3d [origin/main] Update README
* review/issue-42 e4f5g6h [origin/review/issue-42: ahead 2] Fix login validation
  hotfix/login   i7j8k9l [origin/hotfix/login: behind 1] Quick fix
```

**Reading the Output**:
- `*` indicates current branch
- `[origin/review/issue-42: ahead 2]`: Your branch has 2 commits not on remote
- `[origin/hotfix/login: behind 1]`: Remote has 1 commit you don't have locally
- `[origin/main]`: In sync with remote

### Phase 5: Checking If Pull Needed

**Command**:
```bash
git fetch origin
git status
```

**Example**:
```bash
cd ../review-GH-42
git fetch origin
git status
```

**Output If Behind Remote**:
```
On branch review/issue-42
Your branch is behind 'origin/review/issue-42' by 3 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)
```

**What To Do**: Run `git pull` to get the 3 missing commits.

**Output If Diverged**:
```
On branch review/issue-42
Your branch and 'origin/review/issue-42' have diverged,
and have 2 and 3 different commits each, respectively.
  (use "git pull" to merge the remote branch into yours)
```

**What This Means**: You have 2 local commits, remote has 3 different commits. You need to pull and resolve potential merge conflicts.

### Summary Commands Table

| What You Want to Check | Command |
|------------------------|---------|
| Overall status | `git status` |
| Modified files diff | `git diff` |
| Staged files diff | `git diff --staged` |
| Recent commits | `git log --oneline -5` |
| Specific commit | `git show <hash>` |
| Branch tracking | `git branch -vv` |
| Check for remote updates | `git fetch && git status` |
| List all worktrees | `git worktree list` |

---

## Related References

- For basic operations (listing, switching, updating), see [worktree-operations-basic.md](worktree-operations-basic.md)
- For syncing with main branch, best practices, and troubleshooting, see [worktree-operations-maintenance.md](worktree-operations-maintenance.md)
