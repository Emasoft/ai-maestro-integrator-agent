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

- [ ] Verify governance authorization via `team-governance` skill
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

## Error Handling

On failure, check exit code and stderr. Exit 1 = invalid params; Exit 2-4 = API errors. See the detailed guide in Resources.

## Resources

- [detailed-guide](references/detailed-guide.md) — Full reference
  - GraphQL is the Source of Truth
  - Decision Tree for PR Merge Operations
  - Script Usage Details
  - Common Workflows
  - Exit Codes Reference
  - Error Handling
  - Safety Warning: Destructive Operations
  - Script Locations
  - Reference Documents Index

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
