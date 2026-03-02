# Parallel PR Workflow - Part 2: Subagent Management and Path Validation

This document covers:
- Working directory management for subagents
- Path validation rules and common violations

## Table of Contents

- [2.3 Working Directory Management for Subagents](#23-working-directory-management-for-subagents)
  - [Assigning Worktrees to Subagents](#assigning-worktrees-to-subagents)
  - [Subagent Prompt Template](#subagent-prompt-template)
  - [Multi-Agent Coordination](#multi-agent-coordination)
  - [Preventing Cross-Worktree Contamination](#preventing-cross-worktree-contamination)
- [2.4 Path Validation Rules and Common Violations](#24-path-validation-rules-and-common-violations)
  - [Valid Paths (Within Worktree)](#valid-paths-within-worktree)
  - [Invalid Paths (Isolation Violations)](#invalid-paths-isolation-violations)
  - [Common Violation Patterns](#common-violation-patterns)
  - [Path Validation Function](#path-validation-function)

---

## 2.3 Working Directory Management for Subagents

### Assigning Worktrees to Subagents

When delegating PR work to subagents, each agent must receive:

1. **Assigned worktree path:** Absolute path to their worktree
2. **Main repo path:** For reference (read-only access)
3. **PR information:** Number, branch name, description
4. **Isolation rules:** Clear instructions about path constraints

### Subagent Prompt Template

Include this in every subagent prompt:

```
CRITICAL WORKTREE ISOLATION RULES:
- Your assigned worktree is: /tmp/worktrees/pr-<NUMBER>
- ALL file operations MUST be within this path
- NEVER write to /path/to/main-repo
- NEVER write to other worktrees
- Before any file operation, verify the path starts with your worktree

To verify you're in the right place:
  cd /tmp/worktrees/pr-<NUMBER>
  pwd  # Must show your worktree path

If you need to reference code from main repo:
  - Read-only access is permitted
  - NEVER modify files in main repo
  - Copy needed files TO your worktree if needed
```

### Multi-Agent Coordination

When multiple agents work on different PRs:

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                │
│  - Assigns worktrees to agents                                  │
│  - Monitors isolation compliance                                │
│  - Coordinates git operations (serialized)                      │
└─────────────────────────────────────────────────────────────────┘
        │               │               │
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Agent A    │ │  Agent B    │ │  Agent C    │
│  PR #123    │ │  PR #456    │ │  PR #789    │
│  /tmp/wt/   │ │  /tmp/wt/   │ │  /tmp/wt/   │
│  pr-123/    │ │  pr-456/    │ │  pr-789/    │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Preventing Cross-Worktree Contamination

**DO NOT:**
```bash
# WRONG: Agent A accidentally writes to Agent B's worktree
echo "fix" > /tmp/worktrees/pr-456/file.py  # Agent A should NOT do this
```

**DO:**
```bash
# CORRECT: Agent A only writes to their own worktree
echo "fix" > /tmp/worktrees/pr-123/file.py  # Agent A's worktree
```

---

## 2.4 Path Validation Rules and Common Violations

### Valid Paths (Within Worktree)

```
/tmp/worktrees/pr-123/src/main.py        ✓ Valid
/tmp/worktrees/pr-123/tests/test_main.py ✓ Valid
/tmp/worktrees/pr-123/.git               ✓ Valid (but don't modify)
/tmp/worktrees/pr-123/tmp/scratch.txt    ✓ Valid
```

### Invalid Paths (Isolation Violations)

```
/path/to/main-repo/src/main.py           ✗ VIOLATION: Main repo
/tmp/worktrees/pr-456/src/main.py        ✗ VIOLATION: Different worktree
/home/user/documents/notes.txt           ✗ VIOLATION: Outside worktrees
/tmp/scratch.txt                         ✗ VIOLATION: Outside worktree
```

### Common Violation Patterns

**Violation 1: Hardcoded Main Repo Path**
```python
# WRONG
with open("/home/user/project/config.json") as f:
    config = json.load(f)

# CORRECT
worktree = os.environ["WORKTREE_ROOT"]
with open(f"{worktree}/config.json") as f:
    config = json.load(f)
```

**Violation 2: Relative Path Escape**
```bash
# WRONG: Escapes worktree via parent reference
cd /tmp/worktrees/pr-123
cat ../../main-repo/secret.txt

# CORRECT: Stay within worktree
cd /tmp/worktrees/pr-123
cat ./config/settings.txt
```

**Violation 3: Symlink Following**
```bash
# DANGEROUS: Symlink points outside worktree
ls -la link  # link -> /path/to/main-repo/src
cat link/file.py  # Reads from main repo!

# SAFE: Resolve symlinks and validate
realpath link  # Check where it really points
```

**Violation 4: Tool Default Paths**
```bash
# WRONG: Tool writes to default location
prettier --write src/  # Might use main repo if not in worktree

# CORRECT: Explicit path within worktree
cd /tmp/worktrees/pr-123
prettier --write ./src/
```

### Path Validation Function

```python
import os
from pathlib import Path

def validate_worktree_path(
    target: str,
    worktree: str,
    allow_symlinks: bool = False
) -> tuple[bool, str]:
    """
    Validate that target path is within worktree.

    Returns:
        (is_valid, reason)
    """
    target_path = Path(target)
    worktree_path = Path(worktree)

    # Resolve to absolute
    if not target_path.is_absolute():
        target_path = Path.cwd() / target_path

    # Resolve symlinks if not allowed
    if not allow_symlinks:
        target_path = target_path.resolve()
        worktree_path = worktree_path.resolve()

    # Check containment
    try:
        target_path.relative_to(worktree_path)
        return True, "Path is within worktree"
    except ValueError:
        return False, f"Path {target} is outside worktree {worktree}"
```

---

**Previous:** [Part 1 - Creating Worktrees and Isolation](parallel-pr-workflow-part1-creating-and-isolation.md)

**Next:** [Part 3 - Concurrent Operations and Example Workflow](parallel-pr-workflow-part3-concurrency-and-example.md)
