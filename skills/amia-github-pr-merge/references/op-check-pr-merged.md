---
name: op-check-pr-merged
description: Check if a pull request is already merged using GraphQL API
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Check if PR is Merged

## Purpose

Verify whether a pull request has already been merged before attempting any merge operation. This prevents duplicate merge attempts and provides authoritative merge state information.

## When to Use

- Before attempting any merge operation
- When verifying if a previous merge completed
- When receiving conflicting information about PR state
- After enabling auto-merge to check completion

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository read access
- PR number and repository identifier

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--pr` | Integer | Yes | Pull request number |
| `--repo` | String | Yes | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `merged` | Boolean | True if PR is merged, False otherwise |
| `state` | String | PR state: OPEN, CLOSED, or MERGED |
| `merged_at` | String | ISO timestamp of merge (if merged) |
| `merge_commit_sha` | String | SHA of merge commit (if merged) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PR is NOT merged (can proceed with merge) |
| 1 | PR is already merged (idempotency skip) |
| 2 | PR not found |
| 3 | API error |
| 4 | Not authenticated |

## Procedure

1. Run the check script with required parameters
2. Parse the JSON output
3. Check the exit code to determine status
4. If exit code 0: PR is not merged, safe to proceed
5. If exit code 1: PR is already merged, no action needed

## Command

```bash
python scripts/amia_test_pr_merged.py --pr <NUMBER> --repo <OWNER/REPO>
```

## Example

```bash
# Check if PR #123 in myorg/myrepo is merged
python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo

# Expected output for non-merged PR:
# {"merged": false, "state": "OPEN"}
# Exit code: 0

# Expected output for merged PR:
# {"merged": true, "state": "MERGED", "merged_at": "2025-01-30T10:00:00Z"}
# Exit code: 1
```

## Critical Note

**NEVER trust `gh pr view --json state` for merge state verification.** The REST API can return stale data. Always use this GraphQL-based script for authoritative merge state.

## Error Handling

| Scenario | Action |
|----------|--------|
| Exit code 2 (not found) | Verify PR number and repository are correct |
| Exit code 3 (API error) | Retry after brief delay; check network |
| Exit code 4 (not auth) | Run `gh auth login` to authenticate |

## Related Operations

- [op-check-merge-readiness.md](op-check-merge-readiness.md) - Check if PR can be merged
- [op-execute-pr-merge.md](op-execute-pr-merge.md) - Execute the merge
- [op-verify-merge-completion.md](op-verify-merge-completion.md) - Verify merge completed
