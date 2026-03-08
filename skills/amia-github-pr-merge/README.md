# GitHub PR Merge Skill

Comprehensive PR merge operations using GraphQL as the authoritative source of truth for merge state verification, avoiding stale REST API data.

## When to Use

- Merging pull requests (squash, merge, rebase)
- Checking if a PR is already merged
- Verifying merge readiness (CI, reviews, conflicts)
- Configuring auto-merge for PRs waiting on CI or approvals

## Key Scripts

| Script | Purpose |
|--------|---------|
| `amia_test_pr_merged.py` | Check if PR is merged (GraphQL) |
| `amia_test_pr_merge_ready.py` | Verify all merge requirements |
| `amia_merge_pr.py` | Execute merge with strategy |
| `amia_set_auto_merge.py` | Enable/disable auto-merge |

## Quick Start

```bash
# Check if merged
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo

# Check readiness
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo

# Squash merge and delete branch
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch

# Enable auto-merge
python scripts/amia_set_auto_merge.py --pr 123 --repo owner/repo --enable --merge-method SQUASH
```

## Critical Note

**Never use `gh pr view --json state`** for merge verification - it can return stale data. All scripts in this skill use GraphQL queries for authoritative merge state.

## Documentation

See [SKILL.md](SKILL.md) for complete documentation including:

- Decision tree for merge operations
- Exit code reference
- Troubleshooting guide
- Reference documents for merge strategies and auto-merge
