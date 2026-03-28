# Operation: Configure Auto-Merge

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Exit Codes](#exit-codes)
- [Procedure](#procedure)
  - [Enable Auto-Merge](#enable-auto-merge)
  - [Disable Auto-Merge](#disable-auto-merge)
- [Command](#command)
- [Example](#example)
- [Requirements for Auto-Merge](#requirements-for-auto-merge)
- [Auto-Merge Trigger Conditions](#auto-merge-trigger-conditions)
- [When Auto-Merge is Canceled](#when-auto-merge-is-canceled)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Enable or disable automatic merging of a pull request. Auto-merge will merge the PR automatically when all required conditions are met (CI passes, reviews approved).

## When to Use

- When PR is waiting for CI to complete
- When PR needs additional review approvals
- When you want PR to merge automatically once ready
- To cancel previously enabled auto-merge

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository write access
- Repository must have auto-merge enabled in settings
- Branch protection rules must be configured
- PR number and repository identifier

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--pr` | Integer | Yes | Pull request number |
| `--repo` | String | Yes | Repository in owner/repo format |
| `--enable` | Flag | Conditional | Enable auto-merge |
| `--disable` | Flag | Conditional | Disable auto-merge |
| `--merge-method` | String | If enabling | MERGE, SQUASH, or REBASE |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `auto_merge_enabled` | Boolean | Current auto-merge state |
| `merge_method` | String | Configured merge method |
| `enabled_at` | String | When auto-merge was enabled |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Operation successful |
| 1 | Invalid parameters |
| 2 | PR not found |
| 3 | API error |
| 4 | Not authenticated |
| 5 | PR already merged |
| 6 | Cannot enable auto-merge (repo settings) |

## Procedure

### Enable Auto-Merge

1. Verify PR is not already merged
2. Verify repository has auto-merge enabled
3. Run enable command with desired merge method
4. Verify auto-merge is configured
5. Monitor for auto-merge completion

### Disable Auto-Merge

1. Run disable command
2. Verify auto-merge is disabled
3. Proceed with manual merge workflow if needed

## Command

```bash
# Enable auto-merge with squash
python scripts/amia_set_auto_merge.py --pr <NUMBER> --repo <OWNER/REPO> --enable --merge-method SQUASH

# Enable auto-merge with merge commit
python scripts/amia_set_auto_merge.py --pr <NUMBER> --repo <OWNER/REPO> --enable --merge-method MERGE

# Enable auto-merge with rebase
python scripts/amia_set_auto_merge.py --pr <NUMBER> --repo <OWNER/REPO> --enable --merge-method REBASE

# Disable auto-merge
python scripts/amia_set_auto_merge.py --pr <NUMBER> --repo <OWNER/REPO> --disable
```

## Example

```bash
# Enable auto-merge for PR waiting on CI
python scripts/amia_set_auto_merge.py --pr 456 --repo myorg/myrepo --enable --merge-method SQUASH
# Output: {"auto_merge_enabled": true, "merge_method": "SQUASH"}

# Later, check if it merged
python scripts/amia_test_pr_merged.py --pr 456 --repo myorg/myrepo

# If needed, cancel auto-merge
python scripts/amia_set_auto_merge.py --pr 456 --repo myorg/myrepo --disable
# Output: {"auto_merge_enabled": false}
```

## Requirements for Auto-Merge

For auto-merge to work, the repository must have:

1. **Auto-merge enabled** in repository settings
2. **Branch protection rules** on target branch
3. **Required status checks** configured
4. **Required reviewers** configured (optional)

Without these, auto-merge cannot be enabled.

## Auto-Merge Trigger Conditions

Auto-merge will execute when ALL of the following are true:

- All required status checks pass
- All required reviews are approved
- No merge conflicts exist
- No review threads are unresolved (if required)
- No new changes pushed after approval (if required)

## When Auto-Merge is Canceled

Auto-merge is automatically canceled when:

- New commits are pushed to the PR
- A review is dismissed
- The PR is closed
- Someone manually disables it

## Error Handling

| Exit Code | Action |
|-----------|--------|
| 6 (cannot enable) | Enable auto-merge in repo settings first |
| 5 (already merged) | No action needed |
| 3 (API error) | Verify repo permissions and settings |

## Related Operations

- [op-check-pr-merged.md](op-check-pr-merged.md) - Check if auto-merged
- [op-check-merge-readiness.md](op-check-merge-readiness.md) - Why auto-merge not triggering
- [op-execute-pr-merge.md](op-execute-pr-merge.md) - Manual merge alternative
