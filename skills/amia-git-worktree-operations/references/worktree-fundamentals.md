# Worktree Fundamentals

## Table of Contents

- 1.1 What is a git worktree and why it exists
- 1.2 Worktree vs clone vs checkout - choosing the right approach
- 1.3 The shared git directory model explained
- 1.4 When worktrees provide measurable benefits
- 1.5 Common misconceptions about worktrees
- 1.6 Prerequisites and git version requirements

---

## 1.1 What is a Git Worktree and Why It Exists

A git worktree is an additional working directory attached to an existing git repository. It allows you to have multiple branches checked out simultaneously, each in its own directory, while sharing the same underlying git database (the `.git` directory).

### The Problem Worktrees Solve

Traditional git workflow requires you to:
1. Stash or commit your current changes
2. Switch branches
3. Do work on the new branch
4. Switch back to your original branch
5. Pop your stash or continue

This workflow breaks down when:
- You need to work on multiple features simultaneously
- You have long-running builds or tests on one branch
- You need to compare code across branches visually
- Multiple agents/people need isolated environments

### How Worktrees Solve This

With worktrees, you can:
```
/path/to/main-repo/           ← main worktree (e.g., 'main' branch)
    └── .git/                 ← shared git database

/tmp/worktrees/feature-a/     ← additional worktree (e.g., 'feature-a' branch)
    └── .git                  ← file pointing to main .git

/tmp/worktrees/feature-b/     ← additional worktree (e.g., 'feature-b' branch)
    └── .git                  ← file pointing to main .git
```

Each worktree has its own:
- Working directory with files
- Checked out branch
- Staged changes (index)
- Local modifications

All worktrees share:
- The git object database (commits, blobs, trees)
- Remote configurations
- Branches and tags
- Hooks

---

## 1.2 Worktree vs Clone vs Checkout - Choosing the Right Approach

### Comparison Table

| Aspect | Checkout | Clone | Worktree |
|--------|----------|-------|----------|
| Disk space | Minimal | Full repo copy | Minimal |
| Network | None | Full fetch | None |
| Git database | Shared | Separate | Shared |
| Branch conflict | N/A | None | One branch per worktree |
| Setup time | Fast | Slow (large repos) | Fast |
| Independence | None | Complete | Partial |
| Use case | Single task | Separate project | Parallel tasks |

### When to Use Each

**Use `git checkout` when:**
- You work on one thing at a time
- You can stash/commit before switching
- You don't need parallel execution

**Use `git clone` when:**
- You need complete independence
- You want to test destructive operations safely
- Network bandwidth is not a concern
- You need different remote configurations

**Use `git worktree` when:**
- You need multiple branches active simultaneously
- Disk space is limited
- You want fast setup/teardown
- You need shared commits across branches
- You're delegating to multiple subagents

### Decision Flowchart

```
Need to work on different branch?
│
├─► Can you commit/stash current work?
│   ├─► YES: Use git checkout
│   └─► NO: Continue below
│
├─► Need complete independence from main repo?
│   ├─► YES: Use git clone
│   └─► NO: Continue below
│
├─► Is disk space or network limited?
│   ├─► YES: Use git worktree
│   └─► NO: Either clone or worktree works
│
└─► Need fast setup/teardown?
    ├─► YES: Use git worktree
    └─► NO: Use git clone for maximum isolation
```

---

## 1.3 The Shared Git Directory Model Explained

### How Git Stores Data

Git stores all repository data in the `.git` directory:

```
.git/
├── objects/       ← All commits, files, trees (content-addressed)
├── refs/          ← Branch and tag pointers
├── HEAD           ← Current branch pointer
├── index          ← Staging area
├── config         ← Repository configuration
├── hooks/         ← Git hooks
└── worktrees/     ← Worktree metadata
```

### How Worktrees Share This Data

When you create a worktree, git does NOT copy the objects. Instead:

1. **Main repository:** Has the full `.git` directory
2. **Additional worktree:** Has a `.git` FILE (not directory) containing:
   ```
   gitdir: /path/to/main-repo/.git/worktrees/<worktree-name>
   ```

3. **Worktree-specific data** is stored in main repo's `.git/worktrees/<name>/`:
   ```
   .git/worktrees/<name>/
   ├── HEAD           ← This worktree's current branch
   ├── index          ← This worktree's staging area
   ├── commondir      ← Pointer to shared git dir
   └── gitdir         ← Path to worktree's .git file
   ```

### What This Means Practically

**Shared (changes visible everywhere):**
- New commits (once created)
- Branch creations/deletions
- Tags
- Remote URLs
- Git configuration

**Not shared (worktree-specific):**
- Working directory files
- Staged changes
- Which branch is checked out
- Local uncommitted modifications

### Example of Shared Commits

```bash
# In worktree A
cd /tmp/worktrees/feature-a
git commit -m "New feature"

# Commit is immediately visible in worktree B
cd /tmp/worktrees/feature-b
git log --oneline --all | grep "New feature"
# Shows the commit!
```

---

## 1.4 When Worktrees Provide Measurable Benefits

### Scenario 1: Parallel PR Review and Development

**Without worktrees:**
- Review PR: stash, checkout, review, checkout back, pop stash
- Time lost: Context switching, stash conflicts, mental overhead

**With worktrees:**
- Review PR in one worktree while developing in another
- Zero context switching
- Time saved: 5-10 minutes per PR review session

### Scenario 2: Long-Running Tests

**Without worktrees:**
- Run tests on feature branch
- Wait for completion (30+ minutes)
- Cannot work on other branches

**With worktrees:**
- Run tests in worktree A
- Continue development in worktree B
- Productivity maintained during test runs

### Scenario 3: Multi-Agent PR Processing

**Without worktrees:**
- Agents must serialize branch operations
- One agent blocks all others
- Throughput limited to one PR at a time

**With worktrees:**
- Each agent gets isolated worktree
- Parallel PR processing
- Throughput scales with agent count

### Quantified Benefits

| Metric | Without Worktrees | With Worktrees | Improvement |
|--------|-------------------|----------------|-------------|
| PR review time | 15 min | 5 min | 3x faster |
| Context switches/day | 10-20 | 0-2 | 90% reduction |
| Parallel PR capacity | 1 | N (limited by disk) | Nx throughput |
| Risk of stash conflicts | Medium | None | Eliminated |

---

## 1.5 Common Misconceptions About Worktrees

### Misconception 1: "Worktrees are copies of the repo"

**Reality:** Worktrees share the git database. Only working files are "copied" (actually, checked out fresh).

**Implication:** Creating a worktree is fast (seconds) even for large repos.

### Misconception 2: "I can checkout the same branch in multiple worktrees"

**Reality:** Git enforces ONE branch per worktree. Attempting to checkout an already-checked-out branch fails:
```
fatal: 'feature-a' is already checked out at '/tmp/worktrees/feature-a'
```

**Workaround:** Create a new branch from the same commit:
```bash
git worktree add /tmp/new-worktree -b new-branch-name existing-branch
```

### Misconception 3: "Worktrees are completely isolated"

**Reality:** Worktrees share the git database. Operations like `git fetch` affect all worktrees.

**Implication:** Coordinate git operations across worktrees to avoid conflicts.

### Misconception 4: "I can just delete the worktree directory"

**Reality:** Deleting the directory leaves stale entries in `.git/worktrees/`. Always use:
```bash
git worktree remove <path>
# Or if directory already deleted:
git worktree prune
```

### Misconception 5: "Worktrees work with submodules out of the box"

**Reality:** Submodules require special handling in worktrees. Each worktree needs its own submodule checkout.

**Recommendation:** Avoid worktrees with submodule-heavy repos unless necessary.

---

## 1.6 Prerequisites and Git Version Requirements

### Minimum Git Version

**Git 2.5.0 (July 2015):** Basic worktree support (`git worktree add`)

**Git 2.15.0 (October 2017):** Recommended minimum
- `git worktree remove` command added
- `git worktree move` command added
- Improved worktree locking

**Git 2.17.0 (April 2018):**
- Better worktree pruning
- `--track` option for worktree add

### Checking Your Git Version

```bash
git --version
# Example output: git version 2.39.2
```

### Verifying Worktree Support

```bash
# This command should work without error
git worktree list
# Output example:
# /path/to/repo  abc1234 [main]
```

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Git version | 2.15.0 | 2.30.0+ |
| Disk space | 2x working files | 3x working files |
| File system | Any | POSIX-compliant |
| OS | Linux, macOS, Windows | Linux, macOS |

### Known Limitations by Platform

**Windows:**
- Long path issues (enable long paths in git config)
- File locking can cause issues
- NTFS performs worse than ext4/APFS

**macOS:**
- Case-insensitive by default (can cause branch name issues)
- Works well otherwise

**Linux:**
- Best performance and compatibility
- No known limitations

---

## Summary

Git worktrees provide a powerful mechanism for parallel development by allowing multiple working directories to share a single git database. They are particularly valuable for:

1. Multi-agent PR processing
2. Parallel task execution
3. Long-running operations
4. Context-switch-free development

Key constraints to remember:
- One branch per worktree
- Shared git database means coordinated operations
- Always use `git worktree remove` for cleanup
- Minimum Git 2.15.0 required

Continue to [parallel-pr-workflow.md](parallel-pr-workflow.md) for implementing parallel PR processing with worktrees.
