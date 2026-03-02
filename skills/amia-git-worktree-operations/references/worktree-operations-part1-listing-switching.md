# Worktree Operations Part 1: Listing and Switching

## Table of Contents
1. [When you need to see all active worktrees → Listing Worktrees](#listing-worktrees)
2. [If you need to work in a different worktree → Switching Between Worktrees](#switching-between-worktrees)

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

## End of Part 1

For updating worktrees with latest changes, see [worktree-operations-part2-updating.md](worktree-operations-part2-updating.md).
