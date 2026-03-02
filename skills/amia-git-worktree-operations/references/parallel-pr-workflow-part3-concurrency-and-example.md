# Parallel PR Workflow - Part 3: Concurrent Operations and Example Workflow

This document covers:
- Handling concurrent git operation limitations
- Complete example workflow for processing 3 PRs in parallel

## Table of Contents

- [2.5 Handling Concurrent Git Operation Limitations](#25-handling-concurrent-git-operation-limitations)
  - [The Concurrency Problem](#the-concurrency-problem)
  - [Problematic Concurrent Operations](#problematic-concurrent-operations)
  - [Safe Concurrent Operations](#safe-concurrent-operations)
  - [Serialization Strategies](#serialization-strategies)
  - [Best Practice: Git Operation Sequencing](#best-practice-git-operation-sequencing)
- [2.6 Example Workflow: Processing 3 PRs in Parallel](#26-example-workflow-processing-3-prs-in-parallel)
  - [Setup Phase](#setup-phase)
  - [Agent Assignment Phase](#agent-assignment-phase)
  - [Parallel Work Phase](#parallel-work-phase)
  - [Git Operations Phase (Serialized)](#git-operations-phase-serialized)
  - [Cleanup Phase](#cleanup-phase)

---

## 2.5 Handling Concurrent Git Operation Limitations

### The Concurrency Problem

Git uses file locks to prevent concurrent modifications:
- `.git/index.lock` during staging operations
- `.git/refs/heads/<branch>.lock` during branch updates
- `.git/COMMIT_EDITMSG` during commits

**In worktrees, all share the same `.git` directory, so locks affect ALL worktrees.**

### Problematic Concurrent Operations

```
Agent A (pr-123)          Agent B (pr-456)          Result
─────────────────────────────────────────────────────────────
git commit -m "fix"       git commit -m "update"    CONFLICT!
git fetch origin          git push origin           CONFLICT!
git rebase main           git merge main            CONFLICT!
```

### Safe Concurrent Operations

These operations are generally safe to run in parallel:
- `git status`
- `git diff`
- `git log`
- `git show`
- File modifications (not git operations)

### Serialization Strategies

**Strategy 1: Orchestrator-Controlled Git Operations**

Only the orchestrator runs git operations, one at a time:
```python
async def safe_git_operation(worktree: str, operation: list[str]):
    async with git_lock:  # Global lock
        subprocess.run(["git", "-C", worktree] + operation)
```

**Strategy 2: Agent Queuing**

Agents request git operations through a queue:
```
Agent A: REQUEST commit in pr-123
Agent B: REQUEST push in pr-456
Orchestrator: EXECUTE A's commit, then B's push
```

**Strategy 3: Worktree-Level Locking**

Lock at worktree level for operations affecting only that worktree:
```bash
# In worktree pr-123
flock /tmp/worktrees/pr-123/.git.lock git commit -m "fix"
```

### Best Practice: Git Operation Sequencing

```
1. All agents: Complete file modifications
2. Orchestrator: SIGNAL "git operations window open"
3. Agent A: Commit and push (others wait)
4. Agent B: Commit and push (others wait)
5. Agent C: Commit and push (others wait)
6. Orchestrator: SIGNAL "git operations complete"
7. All agents: Resume file modifications
```

---

## 2.6 Example Workflow: Processing 3 PRs in Parallel

### Setup Phase

```bash
# Orchestrator creates worktrees
cd /path/to/main-repo

# PR #101: Bug fix
git fetch origin pull/101/head:pr-101
git worktree add /tmp/worktrees/pr-101 pr-101

# PR #202: New feature
git fetch origin pull/202/head:pr-202
git worktree add /tmp/worktrees/pr-202 pr-202

# PR #303: Documentation
git fetch origin pull/303/head:pr-303
git worktree add /tmp/worktrees/pr-303 pr-303

# Verify
git worktree list
```

### Agent Assignment Phase

```
Orchestrator sends to Agent A:
  "Work on PR #101 in /tmp/worktrees/pr-101.
   Fix the bug in src/handler.py.
   DO NOT write outside your worktree."

Orchestrator sends to Agent B:
  "Work on PR #202 in /tmp/worktrees/pr-202.
   Implement new feature in src/feature.py.
   DO NOT write outside your worktree."

Orchestrator sends to Agent C:
  "Work on PR #303 in /tmp/worktrees/pr-303.
   Update documentation in docs/.
   DO NOT write outside your worktree."
```

### Parallel Work Phase

```
Agent A                   Agent B                   Agent C
───────────────────────────────────────────────────────────────
cd pr-101                 cd pr-202                 cd pr-303
vim src/handler.py        vim src/feature.py        vim docs/README.md
# Editing...              # Editing...              # Editing...
# Done                    # Done                    # Done
```

### Git Operations Phase (Serialized)

```bash
# Agent A commits first
cd /tmp/worktrees/pr-101
git add -A
git commit -m "Fix handler bug"
git push origin pr-101

# Agent B commits second
cd /tmp/worktrees/pr-202
git add -A
git commit -m "Add new feature"
git push origin pr-202

# Agent C commits third
cd /tmp/worktrees/pr-303
git add -A
git commit -m "Update documentation"
git push origin pr-303
```

### Cleanup Phase

```bash
# After PRs are merged
git worktree remove /tmp/worktrees/pr-101
git worktree remove /tmp/worktrees/pr-202
git worktree remove /tmp/worktrees/pr-303

# Clean up remote branches if needed
git push origin --delete pr-101 pr-202 pr-303
```

---

**Previous:** [Part 2 - Subagent Management and Path Validation](parallel-pr-workflow-part2-subagents-and-paths.md)

**Next:** [Part 4 - Error Recovery](parallel-pr-workflow-part4-error-recovery.md)
