# Operation: Execute PR Merge

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Exit Codes](#exit-codes)
- [Merge Strategies](#merge-strategies)
- [Procedure](#procedure)
- [Command](#command)
- [Example](#example)
- [Strategy Selection Guide](#strategy-selection-guide)
- [Safety Warnings](#safety-warnings)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Execute the actual merge of a pull request using the specified merge strategy (merge commit, squash, or rebase).

## When to Use

- After verifying PR is not already merged (op-check-pr-merged)
- After confirming merge readiness (op-check-merge-readiness)
- When immediate merge is preferred over auto-merge

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository write access
- PR number and repository identifier
- Merge readiness confirmed (exit code 0 from readiness check)

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--pr` | Integer | Yes | Pull request number |
| `--repo` | String | Yes | Repository in owner/repo format |
| `--strategy` | String | Yes | Merge strategy: merge, squash, or rebase |
| `--delete-branch` | Flag | No | Delete source branch after merge |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | True if merge succeeded |
| `merged_at` | String | ISO timestamp of merge |
| `merge_commit_sha` | String | SHA of the merge commit |
| `branch_deleted` | Boolean | True if branch was deleted |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Merge successful |
| 1 | Invalid parameters |
| 2 | PR not found |
| 3 | API error |
| 4 | Not authenticated |
| 5 | PR already merged (idempotency) |
| 6 | PR not mergeable |

## Merge Strategies

| Strategy | Commit History | Use When |
|----------|---------------|----------|
| `merge` | Preserves all commits + merge commit | Full history needed |
| `squash` | Combines all commits into one | Clean history, WIP commits |
| `rebase` | Applies commits on top of base | Linear history preferred |

## Procedure

1. Verify PR is not already merged using op-check-pr-merged
2. Verify merge readiness using op-check-merge-readiness
3. Select appropriate merge strategy
4. Execute merge with optional branch deletion
5. Verify merge completion using op-check-pr-merged

## Command

```bash
# Squash merge and delete branch (most common)
python scripts/amia_merge_pr.py --pr <NUMBER> --repo <OWNER/REPO> --strategy squash --delete-branch

# Regular merge commit
python scripts/amia_merge_pr.py --pr <NUMBER> --repo <OWNER/REPO> --strategy merge

# Rebase merge
python scripts/amia_merge_pr.py --pr <NUMBER> --repo <OWNER/REPO> --strategy rebase
```

## Example

```bash
# Complete merge workflow
# Step 1: Check if already merged
python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo
# Exit code 0 - not merged, proceed

# Step 2: Check readiness
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo myorg/myrepo
# Exit code 0 - ready

# Step 3: Execute merge
python scripts/amia_merge_pr.py --pr 123 --repo myorg/myrepo --strategy squash --delete-branch
# Output: {"success": true, "merged_at": "2025-01-30T10:00:00Z", "merge_commit_sha": "abc123"}

# Step 4: Verify completion
python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo
# Exit code 1 - confirmed merged
```

## Strategy Selection Guide

**Use `squash` when:**

- PR has many WIP/fixup commits
- You want a clean, linear history
- Individual commits are not valuable

**Use `merge` when:**

- You need to preserve full commit history
- Tracking individual changes is important
- Branch protection requires merge commits

**Use `rebase` when:**

- You want linear history without merge commits
- Individual commits are meaningful
- Project prefers rebased history

## Safety Warnings

**IRREVERSIBLE**: Merge commits cannot be undone without force push. Always:

1. Verify readiness before merging
2. Create backup branch if uncertain
3. Have rollback plan ready

## Error Handling

| Exit Code | Action |
|-----------|--------|
| 5 (already merged) | No action needed - idempotent success |
| 6 (not mergeable) | Run readiness check to identify blocker |
| 3 (API error) | Retry after brief delay |

## Related Operations

- [op-check-pr-merged.md](op-check-pr-merged.md) - Pre-merge check
- [op-check-merge-readiness.md](op-check-merge-readiness.md) - Verify requirements
- [op-verify-merge-completion.md](op-verify-merge-completion.md) - Post-merge verification
- [op-rollback-bad-merge.md](op-rollback-bad-merge.md) - If merge causes issues
