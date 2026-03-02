---
name: worktree-safety-checks
description: "Safety checks for git hooks running in worktree environments to prevent cross-repository contamination."
---

# Worktree Safety Checks for Git Hooks

## Table of Contents

- 1. Understanding git worktrees and why they create problems for hooks
  - 1.1. What git worktrees are and how they share repository state
  - 1.2. How worktrees differ from clones (shared objects, shared config)
  - 1.3. Why hooks must be aware of worktree environments
- 2. Fixing leaked environment variables that misdirect git operations
  - 2.1. The GIT_DIR environment variable problem
  - 2.2. The GIT_WORK_TREE environment variable problem
  - 2.3. How IDE editors and parent shells leak these variables into hooks
  - 2.4. The fix: unsetting dangerous variables at hook start
- 3. Detecting and fixing corrupted core.worktree configuration
  - 3.1. What core.worktree is and how it gets set accidentally
  - 3.2. How corrupted core.worktree causes phantom file additions
  - 3.3. Detecting the problem: checking for unexpected core.worktree values
  - 3.4. Fixing the problem: unsetting core.worktree
- 4. Detecting whether a hook is running in a worktree or the main repository
  - 4.1. How to distinguish a worktree from a main repository
  - 4.2. Reading the worktree gitdir file to find the main repository
  - 4.3. Adjusting hook behavior based on worktree detection
- 5. Graceful degradation when dependencies are not available in a worktree
  - 5.1. Why worktrees might lack build artifacts or installed dependencies
  - 5.2. Warning instead of blocking when tools are missing
  - 5.3. Skipping checks that require a full project setup
- 6. Complete safety preamble script for all git hooks
  - 6.1. Ready-to-use code block to paste at the top of any hook
  - 6.2. Explanation of each safety check in the preamble

---

## 1. Understanding git worktrees and why they create problems for hooks

### 1.1. What git worktrees are and how they share repository state

Git worktrees allow a single repository to have multiple working directories simultaneously. You create a worktree with:

```sh
git worktree add ../my-feature-branch feature-branch
```

This creates a new directory `../my-feature-branch/` that has:

- Its own working directory with the files checked out from `feature-branch`
- Its own index (staging area)
- Its own HEAD reference

But it shares with the main repository:

- The object database (all commits, blobs, trees)
- The refs database (all branches, tags)
- The git configuration (`.git/config`)
- The hooks directory (`.git/hooks/`)

This sharing is the root of all worktree-related hook problems. Because hooks are shared, a hook triggered in one worktree can accidentally affect another worktree if environment variables or configuration are not handled correctly.

### 1.2. How worktrees differ from clones (shared objects, shared config)

| Aspect | Clone | Worktree |
|--------|-------|----------|
| Object database | Independent copy | Shared with main repo |
| Configuration | Independent | Shared (partially) |
| Hooks | Independent | Shared |
| Branches | Can checkout any branch | Each worktree locks its checked-out branch |
| Disk usage | Full copy of all objects | Minimal (only working directory files) |

The shared hooks are the key difference. In a clone, each copy has its own hooks. In a worktree, the hooks from `.git/hooks/` in the main repository are used by ALL worktrees.

### 1.3. Why hooks must be aware of worktree environments

Because hooks are shared, a hook that assumes "the current directory is the only working directory" will malfunction. Specifically:

- A hook that reads `GIT_DIR` from the environment may point to the wrong repository entirely
- A hook that uses `git status` may report files from the wrong worktree if `GIT_WORK_TREE` is set
- A hook that reads `core.worktree` config may see a path pointing to a different worktree

---

## 2. Fixing leaked environment variables that misdirect git operations

### 2.1. The GIT_DIR environment variable problem

`GIT_DIR` is an environment variable that overrides git's automatic `.git` directory discovery. When set, git uses the value of `GIT_DIR` as the path to the repository instead of searching for `.git` in the current directory and its parents.

The problem arises when a parent process (an IDE, a shell session, or an automation tool) sets `GIT_DIR` for its own purposes, and that value leaks into child processes -- including git hooks.

Example scenario:

1. An IDE extension sets `GIT_DIR=/path/to/project-A/.git` to interact with repository A
2. The developer switches to repository B in the same terminal session
3. The developer commits in repository B
4. The commit-msg hook inherits `GIT_DIR=/path/to/project-A/.git`
5. The hook's git commands operate on repository A instead of repository B

### 2.2. The GIT_WORK_TREE environment variable problem

`GIT_WORK_TREE` overrides where git looks for the working directory. Combined with a leaked `GIT_DIR`, this creates a situation where git operations in a hook can read/write files from a completely different project.

### 2.3. How IDE editors and parent shells leak these variables into hooks

Common sources of leaked variables:

- **IDE terminal sessions**: Some IDE git integrations set `GIT_DIR` when opening an integrated terminal
- **Agent/automation tools**: Tools that manage multiple repositories may set these variables to control which repo git commands target
- **Shell initialization scripts**: Some `.bashrc` or `.zshrc` configurations set `GIT_DIR` for convenience
- **Docker containers and CI runners**: Build environments may pre-set these for multi-repo builds

The variables propagate to child processes through standard Unix process inheritance. Git hooks are child processes of the `git` command, which inherits from the shell.

### 2.4. The fix: unsetting dangerous variables at hook start

At the very top of every git hook, before any git command:

```sh
#!/bin/sh
# Safety: prevent leaked environment variables from misdirecting git operations.
# These variables, if set by a parent process (IDE, shell, agent), override
# git's automatic repository discovery and can cause hooks to operate on
# the WRONG repository.
unset GIT_DIR
unset GIT_WORK_TREE
```

After unsetting these variables, git will use its normal discovery mechanism: search for `.git` starting from the current working directory and walking up parent directories. This ensures the hook operates on the correct repository.

---

## 3. Detecting and fixing corrupted core.worktree configuration

### 3.1. What core.worktree is and how it gets set accidentally

`core.worktree` is a git configuration key that specifies the working directory for a repository. It is almost never needed for normal repositories because git infers the working directory from the `.git` directory location.

However, some tools accidentally set this value. When set, it tells git "the working directory is HERE" regardless of where `.git` is. This is a global config key that affects all operations on the repository.

Tools that have been known to set `core.worktree` accidentally:

- Certain IDE git integrations when handling submodules
- Scripts that configure bare repositories with working trees
- Worktree setup scripts that misconfigure the main repository

### 3.2. How corrupted core.worktree causes phantom file additions

When `core.worktree` points to the wrong directory:

1. `git status` shows files from the wrong directory as "untracked" or "modified"
2. `git add .` stages files from the wrong directory
3. Commits include files that do not belong to the project
4. Hooks that check staged files may see files from a different project entirely

This is extremely difficult to debug because the developer sees phantom files appearing in `git status` that they did not create or modify.

### 3.3. Detecting the problem: checking for unexpected core.worktree values

```sh
# Check if core.worktree is set
worktree_value=$(git config --get core.worktree 2>/dev/null)

if [ -n "$worktree_value" ]; then
  echo "WARNING: core.worktree is set to: $worktree_value"
  echo "This may cause git operations to target the wrong directory."
  echo "Expected: not set (git uses automatic discovery)"
fi
```

### 3.4. Fixing the problem: unsetting core.worktree

```sh
# Remove the corrupted core.worktree setting
git config --unset core.worktree

# Verify it was removed
git config --get core.worktree
# Should produce no output (not set)
```

In a hook, you can detect and fix this automatically:

```sh
worktree_value=$(git config --get core.worktree 2>/dev/null)
if [ -n "$worktree_value" ]; then
  echo "WARNING: Detected unexpected core.worktree=$worktree_value"
  echo "Unsetting to prevent cross-repository contamination."
  git config --unset core.worktree
fi
```

---

## 4. Detecting whether a hook is running in a worktree or the main repository

### 4.1. How to distinguish a worktree from a main repository

In the **main repository**, `.git` is a **directory** containing the full repository structure:

```
project/
  .git/           <-- this is a DIRECTORY
    HEAD
    config
    objects/
    refs/
    hooks/
```

In a **worktree**, `.git` is a **file** containing a pointer to the main repository:

```
my-worktree/
  .git            <-- this is a FILE containing: "gitdir: /path/to/project/.git/worktrees/my-worktree"
```

Detection in a shell script:

```sh
if [ -f ".git" ]; then
  echo "Running in a git worktree"
  is_worktree=1
elif [ -d ".git" ]; then
  echo "Running in the main repository"
  is_worktree=0
else
  echo "Not inside a git repository"
  exit 0
fi
```

### 4.2. Reading the worktree gitdir file to find the main repository

When in a worktree, the `.git` file contains a line like:

```
gitdir: /absolute/path/to/main-repo/.git/worktrees/worktree-name
```

To extract the main repository path:

```sh
if [ -f ".git" ]; then
  # Read the gitdir pointer
  worktree_gitdir=$(sed 's/^gitdir: //' .git)

  # The main repo .git is two levels up from .git/worktrees/<name>
  main_git_dir=$(cd "$worktree_gitdir/../.." && pwd)

  echo "Main repository .git directory: $main_git_dir"
fi
```

### 4.3. Adjusting hook behavior based on worktree detection

Some hooks may need to behave differently in worktrees:

```sh
if [ -f ".git" ]; then
  # In a worktree: hooks directory is in the main repo
  # Dependencies might not be installed here
  # Be more lenient with missing tools
  STRICT_MODE=0
else
  # In the main repository: full environment expected
  STRICT_MODE=1
fi
```

---

## 5. Graceful degradation when dependencies are not available in a worktree

### 5.1. Why worktrees might lack build artifacts or installed dependencies

When a developer creates a worktree, the new working directory starts with only the checked-out files. It does NOT automatically have:

- Installed dependencies (`node_modules/`, `.venv/`, `vendor/`)
- Build artifacts (`dist/`, `build/`, `target/`)
- Generated files (compiled assets, lock files from build steps)
- Tool configurations that are in `.gitignore` (local settings, IDE configs)

If a hook tries to run a tool (like `ruff` or `eslint`) that is installed in a virtual environment or `node_modules/`, it will fail in a fresh worktree.

### 5.2. Warning instead of blocking when tools are missing

```sh
# Check if ruff is available before trying to use it
if command -v ruff >/dev/null 2>&1; then
  echo "Running ruff lint..."
  ruff check src/ || exit 1
elif [ -f ".venv/bin/ruff" ]; then
  echo "Running ruff from virtual environment..."
  .venv/bin/ruff check src/ || exit 1
else
  echo "WARNING: ruff not found. Skipping lint check."
  echo "Install with: pip install ruff (or set up the virtual environment)"
  # Do NOT exit 1 here -- warn but allow the operation to proceed
fi
```

### 5.3. Skipping checks that require a full project setup

```sh
# Skip test suite if dependencies are not installed
if [ ! -d ".venv" ] && [ ! -d "node_modules" ]; then
  echo "WARNING: Dependencies not installed. Skipping test suite."
  echo "Run your package manager's install command to enable pre-push tests."
  exit 0
fi
```

---

## 6. Complete safety preamble script for all git hooks

### 6.1. Ready-to-use code block to paste at the top of any hook

Copy the following block to the top of every git hook script, immediately after the shebang line:

```sh
#!/bin/sh
# ==================================================================
# Git Hook Safety Preamble
# ==================================================================
# This block prevents common environmental issues that cause hooks
# to malfunction, especially in worktree and multi-IDE environments.
#
# Include this at the top of EVERY git hook (pre-commit, commit-msg,
# pre-push, post-merge, etc.).
# ==================================================================

# 1. Prevent leaked environment variables from misdirecting git.
#    Parent processes (IDEs, agents, shells) may set these, causing
#    hooks to operate on the WRONG repository.
unset GIT_DIR
unset GIT_WORK_TREE

# 2. Detect and fix corrupted core.worktree configuration.
#    Some tools accidentally set this, causing phantom file additions
#    from wrong directories.
_cw=$(git config --get core.worktree 2>/dev/null)
if [ -n "$_cw" ]; then
  echo "HOOK WARNING: Detected core.worktree=$_cw (unsetting to prevent contamination)"
  git config --unset core.worktree
fi
unset _cw

# 3. Detect worktree environment for conditional behavior.
#    In a worktree, .git is a FILE (pointer). In main repo, it is a DIRECTORY.
IS_WORKTREE=0
if [ -f ".git" ]; then
  IS_WORKTREE=1
fi

# 4. Helper function: check if a command exists before running it.
#    Use this before every tool invocation to handle missing dependencies
#    gracefully (especially in worktrees without installed dependencies).
check_tool() {
  tool_name="$1"
  if ! command -v "$tool_name" >/dev/null 2>&1; then
    echo "HOOK WARNING: $tool_name not found. Skipping related checks."
    return 1
  fi
  return 0
}

# ==================================================================
# End of Safety Preamble. Hook-specific logic follows below.
# ==================================================================
```

### 6.2. Explanation of each safety check in the preamble

| Check | What It Prevents | Cost |
|-------|-----------------|------|
| `unset GIT_DIR` | Hook operating on wrong repository due to leaked env var | Zero runtime cost |
| `unset GIT_WORK_TREE` | Hook reading/writing files from wrong working directory | Zero runtime cost |
| `core.worktree` detection | Phantom files from wrong directory appearing in git status | One git config read (~1ms) |
| `core.worktree` fix | Ongoing contamination from corrupted config | One git config write (~1ms), only when needed |
| Worktree detection | Allows conditional behavior (strict vs lenient checks) | One filesystem stat (~1ms) |
| `check_tool` helper | Hook crashing with "command not found" in worktrees without dependencies | One `command -v` call per tool (~1ms each) |

Total overhead of the safety preamble: approximately 5 milliseconds. This is negligible compared to the time saved by preventing misdiagnosed failures.
