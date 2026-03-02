# Git Worktree Operations Skill

Git worktree management for parallel PR processing. Enables simultaneous work on multiple PRs in isolated directories without branch switching overhead.

## When to Use

- Processing multiple PRs concurrently with subagents
- Running long tests on one branch while developing another
- Reviewing PRs locally without interrupting current work
- Any workflow requiring simultaneous access to multiple branches

## When NOT to Use

- Single-branch workflows
- Disk space constrained environments
- Repositories with complex submodule setups

## Key Features

| Feature | Description |
|---------|-------------|
| Complete isolation | Each PR in its own directory |
| Shared git database | No duplicate .git storage |
| Subagent-friendly | Easy to delegate PR tasks |
| Safe cleanup | Verification before removal |

## Critical Constraints

1. **Absolute Isolation**: All file operations MUST stay within worktree boundaries
2. **No Concurrent Git Ops**: Serialize git commands across worktrees
3. **One Branch Per Worktree**: Git enforces this automatically
4. **Verify Before Cleanup**: Always check for uncommitted changes
5. **Worktree Path Rules**: Paths must be outside main repo, use absolute paths, never nest worktrees

## Included Scripts

| Script | Purpose |
|--------|---------|
| `amia_create_worktree.py` | Create worktree for a PR |
| `amia_list_worktrees.py` | List all active worktrees |
| `amia_cleanup_worktree.py` | Safely remove a worktree |
| `amia_verify_worktree_isolation.py` | Check isolation violations |
| `amia_worktree_commit_push.py` | Commit and push changes |

## Quick Start

```bash
# Create worktree for PR #123
python scripts/amia_create_worktree.py --pr 123 --base-path /tmp/worktrees

# Work in /tmp/worktrees/pr-123, then cleanup
python scripts/amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-123
```

See [SKILL.md](SKILL.md) for complete documentation.
