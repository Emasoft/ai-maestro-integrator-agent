# Parallel PR Workflow with Git Worktrees

This document provides the complete guide for managing multiple PRs simultaneously using git worktrees, with strict isolation between agents.

---

## Table of Contents

### Part 1: Creating Worktrees and Isolation
**File:** [parallel-pr-workflow-part1-creating-and-isolation.md](parallel-pr-workflow-part1-creating-and-isolation.md)

- **2.1 Creating Worktrees for Multiple Simultaneous PRs**
  - 2.1.1 Standard worktree creation process (fetch, create, verify)
  - 2.1.2 Naming convention for worktree paths
  - 2.1.3 Creating worktree from remote branch
  - 2.1.4 Creating worktree for a new branch

- **2.2 Isolation Requirements and Enforcement Rules**
  - 2.2.1 The golden rule: all operations within assigned worktree
  - 2.2.2 Why isolation matters (merge conflicts, lost work, corruption)
  - 2.2.3 Enforcement rules for agents (path validation, directory lock)
  - 2.2.4 Automated isolation checking with verification script

### Part 2: Subagent Management and Path Validation
**File:** [parallel-pr-workflow-part2-subagents-and-paths.md](parallel-pr-workflow-part2-subagents-and-paths.md)

- **2.3 Working Directory Management for Subagents**
  - 2.3.1 Information each agent must receive (worktree path, PR info, rules)
  - 2.3.2 Subagent prompt template for isolation enforcement
  - 2.3.3 Multi-agent coordination diagram
  - 2.3.4 Preventing cross-worktree contamination

- **2.4 Path Validation Rules and Common Violations**
  - 2.4.1 Valid paths (within worktree)
  - 2.4.2 Invalid paths (isolation violations)
  - 2.4.3 Common violation patterns (hardcoded paths, escapes, symlinks, tool defaults)
  - 2.4.4 Path validation function (Python implementation)

### Part 3: Concurrent Operations and Example Workflow
**File:** [parallel-pr-workflow-part3-concurrency-and-example.md](parallel-pr-workflow-part3-concurrency-and-example.md)

- **2.5 Handling Concurrent Git Operation Limitations**
  - 2.5.1 The concurrency problem (shared .git locks)
  - 2.5.2 Problematic concurrent operations (commit, fetch, push conflicts)
  - 2.5.3 Safe concurrent operations (status, diff, log, file mods)
  - 2.5.4 Serialization strategies (orchestrator-controlled, queuing, locking)
  - 2.5.5 Best practice: git operation sequencing

- **2.6 Example Workflow: Processing 3 PRs in Parallel**
  - 2.6.1 Setup phase (creating 3 worktrees)
  - 2.6.2 Agent assignment phase (task delegation)
  - 2.6.3 Parallel work phase (simultaneous editing)
  - 2.6.4 Git operations phase (serialized commits)
  - 2.6.5 Cleanup phase (worktree removal)

### Part 4: Error Recovery
**File:** [parallel-pr-workflow-part4-error-recovery.md](parallel-pr-workflow-part4-error-recovery.md)

- **2.7 Error Recovery When Isolation is Violated**
  - 2.7.1 Detecting violations with verification script
  - 2.7.2 Recovery procedure for main repo contamination
  - 2.7.3 Recovery procedure for cross-worktree contamination
  - 2.7.4 Preventing future violations

- **Summary**
  - Key requirements for parallel PR workflow

---

## Quick Reference

### Creating a Worktree for a PR

```bash
cd /path/to/main-repo
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
git worktree add /tmp/worktrees/pr-<PR_NUMBER> pr-<PR_NUMBER>
```

### Subagent Isolation Rules (Copy to All Subagent Prompts)

```
CRITICAL WORKTREE ISOLATION RULES:
- Your assigned worktree is: /tmp/worktrees/pr-<NUMBER>
- ALL file operations MUST be within this path
- NEVER write to /path/to/main-repo
- NEVER write to other worktrees
- Before any file operation, verify the path starts with your worktree
```

### Safe vs Unsafe Concurrent Operations

| Safe (Parallel OK) | Unsafe (Serialize) |
|--------------------|-------------------|
| `git status`       | `git commit`      |
| `git diff`         | `git push`        |
| `git log`          | `git fetch`       |
| `git show`         | `git merge`       |
| File modifications | `git rebase`      |

### Violation Recovery Quick Steps

1. Run `git status` in main repo and all worktrees
2. Identify contaminated locations
3. Save changes with `git diff > /tmp/changes.patch`
4. Reset contaminated location with `git checkout -- .`
5. Apply patch to correct worktree

---

## Related Documents

- [worktree-fundamentals.md](worktree-fundamentals.md) - Basic worktree concepts
- [worktree-cleanup.md](worktree-cleanup.md) - Safe worktree removal procedures
- [troubleshooting.md](troubleshooting.md) - Common issues and solutions
