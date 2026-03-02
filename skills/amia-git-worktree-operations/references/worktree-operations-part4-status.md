# Worktree Operations Part 4: Checking Worktree Status

## Table of Contents
1. [Basic Status Check](#phase-1-basic-status-check)
2. [Checking Modified Files in Detail](#phase-2-checking-modified-files-in-detail)
3. [Checking Commit Status](#phase-3-checking-commit-status)
4. [Checking Upstream Tracking](#phase-4-checking-upstream-tracking)
5. [Checking If Pull Needed](#phase-5-checking-if-pull-needed)
6. [Summary Commands Table](#summary-commands-table)

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

## End of Part 4

For syncing worktrees with main branch, see [worktree-operations-part5-syncing.md](worktree-operations-part5-syncing.md).
