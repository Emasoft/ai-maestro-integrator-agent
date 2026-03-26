# Operation: Check Merge Readiness

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Exit Codes](#exit-codes)
- [Procedure](#procedure)
- [Command](#command)
- [Example](#example)
- [MergeStateStatus Values](#mergestatestatus-values)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Verify that all requirements are met for merging a pull request. This includes CI status, review approvals, merge conflicts, and unresolved threads.

## When to Use

- Before executing any merge operation
- When diagnosing why a PR cannot be merged
- When deciding between immediate merge vs auto-merge
- After resolving a blocking condition to verify readiness

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository read access
- PR number and repository identifier

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--pr` | Integer | Yes | Pull request number |
| `--repo` | String | Yes | Repository in owner/repo format |
| `--ignore-ci` | Flag | No | Skip CI check (emergency merge) |
| `--ignore-threads` | Flag | No | Skip unresolved threads check |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `ready` | Boolean | True if PR is ready to merge |
| `merge_state` | String | MergeStateStatus from GitHub API |
| `blocking_reasons` | Array | List of conditions blocking merge |
| `ci_status` | String | Status of required CI checks |
| `review_status` | Object | Approval counts and requirements |
| `conflict_status` | Boolean | True if conflicts exist |
| `threads_resolved` | Boolean | True if all threads resolved |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PR is ready to merge |
| 1 | CI checks failing |
| 2 | Merge conflicts exist |
| 3 | Unresolved review threads |
| 4 | Missing required approvals |
| 5 | PR is already merged |
| 6 | Other blocking condition |

## Procedure

1. Run the readiness check script
2. Parse the JSON output for blocking reasons
3. If exit code 0: Proceed to merge
4. If exit code 1-4: Address the specific blocker
5. Use `--ignore-ci` or `--ignore-threads` only with explicit approval

## Command

```bash
python scripts/amia_test_pr_merge_ready.py --pr <NUMBER> --repo <OWNER/REPO>

# Skip CI check (requires explicit approval)
python scripts/amia_test_pr_merge_ready.py --pr <NUMBER> --repo <OWNER/REPO> --ignore-ci

# Skip unresolved threads check
python scripts/amia_test_pr_merge_ready.py --pr <NUMBER> --repo <OWNER/REPO> --ignore-threads
```

## Example

```bash
# Full readiness check
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo myorg/myrepo

# Ready to merge:
# {"ready": true, "merge_state": "MERGEABLE"}
# Exit code: 0

# Not ready (CI failing):
# {"ready": false, "merge_state": "BLOCKED", "blocking_reasons": ["ci_failing"]}
# Exit code: 1

# Not ready (conflicts):
# {"ready": false, "merge_state": "CONFLICTING", "blocking_reasons": ["conflicts"]}
# Exit code: 2
```

## MergeStateStatus Values

| Status | Meaning | Action |
|--------|---------|--------|
| MERGEABLE | Safe to merge | Proceed with merge |
| CONFLICTING | Conflicts exist | Resolve conflicts first |
| BLOCKED | Branch protection rules blocking | Check required checks/reviews |
| BEHIND | Branch needs update | Rebase or merge base branch |
| UNSTABLE | Required status checks failing | Wait for CI or fix issues |
| UNKNOWN | State being computed | Wait 5-10 seconds and retry |

## Error Handling

| Exit Code | Recovery Action |
|-----------|-----------------|
| 1 (CI failing) | Fix CI issues OR use `--ignore-ci` with approval |
| 2 (conflicts) | Resolve conflicts in the PR branch |
| 3 (threads) | Resolve all review threads OR use `--ignore-threads` |
| 4 (reviews) | Get required approvals from reviewers |

## Related Operations

- [op-check-pr-merged.md](op-check-pr-merged.md) - Check if already merged
- [op-execute-pr-merge.md](op-execute-pr-merge.md) - Execute the merge
- [op-configure-auto-merge.md](op-configure-auto-merge.md) - Enable auto-merge when waiting
