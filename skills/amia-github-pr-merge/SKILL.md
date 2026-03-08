---
name: amia-github-pr-merge
description: "Use when merging pull requests, checking merge status, or configuring auto-merge. Trigger with merge, auto-merge, or readiness verification requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: "1.0.0"
  author: Emasoft
  category: github-workflow
  tags: "github, pull-request, merge, graphql, automation"
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub PR Merge Operations

## Overview

Merge pull requests, check merge status, verify readiness, and configure auto-merge via the GitHub GraphQL API. Always use GraphQL (not `gh pr view --json state`) as the authoritative merge state source.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for automation scripts
- Repository write access for merge operations
- GraphQL API access (included with standard GitHub auth)

## Instructions

1. Check if the PR is already merged: `amia_test_pr_merged.py --pr <N> --repo <owner/repo>`
2. Verify merge readiness: `amia_test_pr_merge_ready.py --pr <N> --repo <owner/repo>`
3. Resolve any blockers indicated by exit codes (CI, conflicts, reviews, threads)
4. Execute merge: `amia_merge_pr.py --pr <N> --repo <owner/repo> --strategy <merge|squash|rebase>`
5. Or enable auto-merge: `amia_set_auto_merge.py --pr <N> --repo <owner/repo> --enable --merge-method <MERGE|SQUASH|REBASE>`
6. Verify completion: `amia_test_pr_merged.py --pr <N> --repo <owner/repo>`

### Checklist

Copy this checklist and track your progress:

- [ ] Check if PR is already merged (exit 5 = already merged)
- [ ] Verify merge readiness (exit 0 = ready)
- [ ] Resolve blocking conditions (CI, conflicts, reviews, threads)
- [ ] Select merge strategy (merge/squash/rebase)
- [ ] Execute merge or enable auto-merge
- [ ] Verify merge completion
- [ ] Handle errors based on exit codes

## Output

| Output Type | Format | Key Fields |
|-------------|--------|------------|
| Merge status | JSON | `merged` (bool), `state` (OPEN/CLOSED/MERGED) |
| Readiness check | JSON | `ready` (bool), `merge_state`, blocking reasons |
| Merge result | JSON | `success` (bool), `merged_at`, `sha` |
| Auto-merge | JSON | `auto_merge_enabled` (bool), `merge_method` |

Exit codes: 0=success, 1=invalid params, 2=not found, 3=API error, 4=auth, 5=already merged, 6=not mergeable.

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

**Merge Operations:**

- `references/merge-state-verification.md` -- GraphQL merge state verification, MergeStateStatus values
- `references/merge-strategies.md` -- Merge/squash/rebase strategy selection guide
- `references/auto-merge.md` -- Auto-merge configuration via GraphQL mutations

**Operation Guides:**

- `references/op-check-pr-merged.md` -- Check if PR is merged
- `references/op-check-merge-readiness.md` -- Verify merge eligibility
- `references/op-execute-pr-merge.md` -- Execute PR merge
- `references/op-configure-auto-merge.md` -- Configure auto-merge
- `references/op-verify-merge-completion.md` -- Verify merge completion
- `references/op-rollback-bad-merge.md` -- Rollback a bad merge

**Detailed Guide:**

- `references/detailed-guide.md` -- Decision trees, workflows, error handling, safety warnings

## Error Handling

If a script fails, check the exit code and stderr output. Common issues:

- **Exit 1**: Invalid parameters or missing arguments
- **Exit 2-4**: GitHub API errors (auth, not found, rate limit)

See `references/detailed-guide.md` for detailed error scenarios.

## Resources

- `references/auto-merge.md`
- `references/detailed-guide.md`
- `references/merge-state-verification.md`
- `references/merge-strategies.md`
- `references/op-check-merge-readiness.md`
- `references/op-check-pr-merged.md`
- `references/op-configure-auto-merge.md`
- `references/op-execute-pr-merge.md`
- ...and 2 more in `references/`

## Examples

### Example 1: Standard PR Merge

```bash
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo
# {"merged": false, "state": "OPEN"} -> continue

python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo
# {"ready": true, "merge_state": "MERGEABLE"} -> ready

python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch
# {"success": true, "merged_at": "2025-01-30T10:00:00Z"}
```
