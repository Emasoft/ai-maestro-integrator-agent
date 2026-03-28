# Operation: Verify Merge Completion

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Exit Codes](#exit-codes)
- [Procedure](#procedure)
- [Command](#command)
- [Example](#example)
- [Verification Workflow](#verification-workflow)
- [When Verification Fails](#when-verification-fails)
- [Retry Logic](#retry-logic)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Confirm that a merge operation completed successfully after executing a merge or enabling auto-merge. This provides authoritative verification via GraphQL.

## When to Use

- Immediately after executing a merge operation
- After auto-merge should have triggered
- When verifying merge status for reporting
- When merge command succeeded but confirmation needed

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
| `merged` | Boolean | True if PR is merged |
| `state` | String | OPEN, CLOSED, or MERGED |
| `merged_at` | String | ISO timestamp of merge |
| `merge_commit_sha` | String | SHA of merge commit |
| `merged_by` | String | Username who performed merge |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PR is NOT merged (verification failed) |
| 1 | PR IS merged (verification successful) |
| 2 | PR not found |
| 3 | API error |
| 4 | Not authenticated |

## Procedure

1. Run the merged check script
2. Verify exit code is 1 (merged)
3. If exit code is 0, merge did not complete
4. Extract merge details from JSON output

## Command

```bash
python scripts/amia_test_pr_merged.py --pr <NUMBER> --repo <OWNER/REPO>
```

## Example

```bash
# After executing merge, verify completion
python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo

# Successful verification (exit code 1):
# {
#   "merged": true,
#   "state": "MERGED",
#   "merged_at": "2025-01-30T10:00:00Z",
#   "merge_commit_sha": "abc123def456",
#   "merged_by": "github-actions[bot]"
# }

# Failed verification (exit code 0):
# {
#   "merged": false,
#   "state": "OPEN"
# }
```

## Verification Workflow

```bash
# Complete merge and verify workflow
# Step 1: Execute merge
python scripts/amia_merge_pr.py --pr 123 --repo myorg/myrepo --strategy squash
# Exit code 0 - merge command succeeded

# Step 2: Verify completion
python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo
# Exit code 1 - VERIFIED merged

# If exit code 0 - merge did NOT complete, investigate
```

## When Verification Fails

If merge command succeeded but verification shows not merged:

1. **Timing Issue**: Wait 5-10 seconds and retry (GitHub propagation delay)
2. **Race Condition**: Another actor may have closed the PR
3. **API Error**: Check if merge command actually failed silently

## Retry Logic

```bash
# Retry with delay if verification fails
python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo
if [ $? -eq 0 ]; then
    sleep 10  # Wait for propagation
    python scripts/amia_test_pr_merged.py --pr 123 --repo myorg/myrepo
fi
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Exit 0 after merge | Wait and retry; if persistent, check PR state manually |
| Exit 2 (not found) | Verify PR number is correct |
| Exit 3 (API error) | Retry after delay; check network |

## Related Operations

- [op-execute-pr-merge.md](op-execute-pr-merge.md) - The merge to verify
- [op-check-pr-merged.md](op-check-pr-merged.md) - Same script, different context
- [op-rollback-bad-merge.md](op-rollback-bad-merge.md) - If merge needs reverting
