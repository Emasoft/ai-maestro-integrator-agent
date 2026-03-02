# Worktree Operations Part 3: Locking and Moving

## Table of Contents
1. [If you need to protect a worktree from deletion → Locking and Unlocking Worktrees](#locking-and-unlocking-worktrees)
2. [When you need to relocate a worktree → Moving Worktrees](#moving-worktrees)

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

## End of Part 3

For checking worktree status, see [worktree-operations-part4-status.md](worktree-operations-part4-status.md).
