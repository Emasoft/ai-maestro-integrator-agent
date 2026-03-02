# Parallel PR Workflow - Part 1: Creating Worktrees and Isolation

This document covers the foundational aspects of parallel PR workflow:
- Creating worktrees for multiple simultaneous PRs
- Isolation requirements and enforcement rules

## Table of Contents

- [2.1 Creating Worktrees for Multiple Simultaneous PRs](#21-creating-worktrees-for-multiple-simultaneous-prs)
  - [Standard Worktree Creation Process](#standard-worktree-creation-process)
  - [Naming Convention for Worktree Paths](#naming-convention-for-worktree-paths)
  - [Creating Worktree from Remote Branch](#creating-worktree-from-remote-branch)
  - [Creating Worktree for a New Branch](#creating-worktree-for-a-new-branch)
- [2.2 Isolation Requirements and Enforcement Rules](#22-isolation-requirements-and-enforcement-rules)
  - [The Golden Rule of Worktree Isolation](#the-golden-rule-of-worktree-isolation)
  - [Why Isolation Matters](#why-isolation-matters)
  - [Enforcement Rules for Agents](#enforcement-rules-for-agents)
  - [Automated Isolation Checking](#automated-isolation-checking)

---

## 2.1 Creating Worktrees for Multiple Simultaneous PRs

### Standard Worktree Creation Process

For each PR you want to work on in parallel:

**Step 1: Fetch the PR branch from remote**
```bash
cd /path/to/main-repo
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
```

**Step 2: Create the worktree**
```bash
git worktree add /tmp/worktrees/pr-<PR_NUMBER> pr-<PR_NUMBER>
```

**Step 3: Verify the worktree was created**
```bash
git worktree list
# Should show new worktree in output
```

### Naming Convention for Worktree Paths

Use a consistent naming scheme to avoid confusion:

```
/tmp/worktrees/
├── pr-123/          ← Worktree for PR #123
├── pr-456/          ← Worktree for PR #456
├── pr-789/          ← Worktree for PR #789
└── issue-42/        ← Worktree for issue #42 (if not a PR)
```

**Rules:**
- Use `/tmp/worktrees/` or similar temporary location
- Include PR number in directory name
- Use lowercase, hyphen-separated names
- Avoid spaces and special characters

### Creating Worktree from Remote Branch

If the branch exists on remote but not locally:

```bash
# Fetch and create worktree in one step
git worktree add -b pr-123 /tmp/worktrees/pr-123 origin/feature-branch
```

### Creating Worktree for a New Branch

If you need to create a new branch for the PR:

```bash
# Create new branch from current HEAD
git worktree add -b new-feature /tmp/worktrees/new-feature

# Create new branch from specific commit/branch
git worktree add -b hotfix-123 /tmp/worktrees/hotfix-123 main
```

---

## 2.2 Isolation Requirements and Enforcement Rules

### The Golden Rule of Worktree Isolation

**EVERY file operation MUST happen within the assigned worktree directory.**

This means:
- File reads: ONLY from within worktree
- File writes: ONLY to within worktree
- File edits: ONLY files within worktree
- Script execution: FROM within worktree
- Temp files: INSIDE worktree (e.g., `<worktree>/tmp/`)

### Why Isolation Matters

Violating isolation causes:
1. **Merge conflicts:** Changes appear in wrong branch
2. **Lost work:** Changes committed to wrong PR
3. **Repository corruption:** Mixed states across branches
4. **Review failures:** PR contains unrelated changes

### Enforcement Rules for Agents

**Rule 1: Path Prefix Validation**
Before any file operation, verify the target path starts with the assigned worktree:
```python
def validate_path(target_path: str, worktree_path: str) -> bool:
    """Returns True if target is inside worktree."""
    target = os.path.realpath(target_path)
    worktree = os.path.realpath(worktree_path)
    return target.startswith(worktree + os.sep)
```

**Rule 2: Working Directory Lock**
Set and verify working directory at operation start:
```bash
cd /tmp/worktrees/pr-123
# Verify we're in the right place
if [[ "$(pwd)" != "/tmp/worktrees/pr-123" ]]; then
    echo "ERROR: Not in expected worktree" >&2
    exit 1
fi
```

**Rule 3: No Absolute Paths to Main Repo**
Never use paths like `/path/to/main-repo/src/file.py` when working in a worktree. Always use worktree-relative paths.

**Rule 4: Environment Variable for Worktree Root**
Set an environment variable for validation:
```bash
export WORKTREE_ROOT="/tmp/worktrees/pr-123"
```

### Automated Isolation Checking

Run the verification script periodically:
```bash
python scripts/amia_verify_worktree_isolation.py \
    --worktree-path /tmp/worktrees/pr-123 \
    --main-repo /path/to/main-repo
```

---

**Next:** [Part 2 - Subagent Management and Path Validation](parallel-pr-workflow-part2-subagents-and-paths.md)
