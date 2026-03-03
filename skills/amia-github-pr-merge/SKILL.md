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

This skill provides comprehensive guidance for merging pull requests, checking merge status, verifying merge readiness, and configuring auto-merge using the GitHub API.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for running automation scripts
- Repository write access for merge operations
- GraphQL API access (included with standard GitHub authentication)

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Merge status | JSON | Contains `merged` (boolean), `state` (OPEN/CLOSED/MERGED) |
| Readiness check | JSON | Contains `ready` (boolean), `merge_state` (MergeStateStatus), blocking reasons |
| Merge result | JSON | Contains `success` (boolean), `merged_at` (ISO timestamp), `sha` (commit hash) |
| Auto-merge status | JSON | Contains `auto_merge_enabled` (boolean), `merge_method` (MERGE/SQUASH/REBASE) |
| Exit codes | Integer | Standardized codes: 0=success, 1=invalid params, 2=not found, 3=API error, 4=auth, 5=already merged, 6=not mergeable |

## Instructions

1. Identify the operation needed (check merged status, verify readiness, execute merge, or configure auto-merge)
2. Consult the decision tree below to select the appropriate script
3. Run the selected script with required parameters (--pr, --repo, strategy/method as applicable)
4. Parse the JSON output to determine success or blocking conditions
5. If blocked, resolve the issue indicated by the exit code and JSON details
6. For merge operations, verify completion using `amia_test_pr_merged.py`

### Checklist

Copy this checklist and track your progress:

- [ ] Identify the operation needed (check/verify/merge/auto-merge)
- [ ] Check if PR is already merged using `amia_test_pr_merged.py`
- [ ] Verify merge readiness using `amia_test_pr_merge_ready.py`
- [ ] Resolve any blocking conditions (CI, conflicts, reviews, threads)
- [ ] Execute merge with appropriate strategy (merge/squash/rebase)
- [ ] Or enable auto-merge if waiting for CI/reviews
- [ ] Verify merge completion using `amia_test_pr_merged.py`
- [ ] Handle any errors based on exit codes

## CRITICAL: GraphQL is the Source of Truth

**NEVER trust `gh pr view --json state` for merge state verification.**

The REST API and `gh pr view` can return stale data. GraphQL queries against the GitHub API provide the authoritative, real-time merge state. Always use GraphQL for:

- Checking if a PR is already merged
- Verifying merge eligibility (MergeStateStatus)
- Confirming merge completion

## Overview of Operations

| Operation | Script | Purpose |
|-----------|--------|---------|
| Check if merged | `amia_test_pr_merged.py` | Verify PR merge status via GraphQL |
| Check readiness | `amia_test_pr_merge_ready.py` | Verify all merge requirements met |
| Execute merge | `amia_merge_pr.py` | Merge with specified strategy |
| Auto-merge | `amia_set_auto_merge.py` | Enable/disable auto-merge |

## Decision Tree for PR Merge Operations

```
START: Need to merge a PR
    │
    ├─► Is PR already merged?
    │   Run: amia_test_pr_merged.py --pr <number> --repo <owner/repo>
    │       │
    │       ├─► Exit 1 (merged) → STOP: PR already merged
    │       │
    │       └─► Exit 0 (not merged) → Continue
    │
    ├─► Is PR ready to merge?
    │   Run: amia_test_pr_merge_ready.py --pr <number> --repo <owner/repo>
    │       │
    │       ├─► Exit 0 (ready) → Proceed to merge
    │       │
    │       ├─► Exit 1 (CI failing) → Fix CI or use --ignore-ci
    │       │
    │       ├─► Exit 2 (conflicts) → Resolve conflicts first
    │       │
    │       ├─► Exit 3 (threads) → Resolve threads or use --ignore-threads
    │       │
    │       └─► Exit 4 (reviews) → Get required approvals
    │
    ├─► Should merge now or auto-merge?
    │       │
    │       ├─► Merge now:
    │       │   Run: amia_merge_pr.py --pr <number> --repo <owner/repo> \
    │       │        --strategy <merge|squash|rebase> [--delete-branch]
    │       │
    │       └─► Auto-merge when ready:
    │           Run: amia_set_auto_merge.py --pr <number> --repo <owner/repo> \
    │                --enable --merge-method <MERGE|SQUASH|REBASE>
    │
    └─► Verify merge completed:
        Run: amia_test_pr_merged.py --pr <number> --repo <owner/repo>
```

## When to Use Each Script

### amia_test_pr_merged.py

Use BEFORE attempting any merge operation to avoid:
- Duplicate merge attempts
- Confusing error messages
- Wasted API calls

```bash
# Check if PR #123 in owner/repo is merged
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo
```

### amia_test_pr_merge_ready.py

Use to understand WHY a PR cannot be merged:

```bash
# Full readiness check
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo

# Skip CI check (emergency merge)
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo --ignore-ci

# Skip unresolved threads check
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo --ignore-threads
```

### amia_merge_pr.py

Use to execute the actual merge:

```bash
# Squash merge and delete branch
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch

# Regular merge commit
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy merge

# Rebase merge
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy rebase
```

### amia_set_auto_merge.py

Use when PR needs to wait for CI or reviews:

```bash
# Enable auto-merge with squash
python scripts/amia_set_auto_merge.py --pr 123 --repo owner/repo --enable --merge-method SQUASH

# Disable auto-merge
python scripts/amia_set_auto_merge.py --pr 123 --repo owner/repo --disable
```

## Reference Documents

### Merge State Verification

See [references/merge-state-verification.md](references/merge-state-verification.md):

- 1.1 Why `gh pr view --json state` can be stale
  - 1.1.1 REST API caching behavior
  - 1.1.2 Race conditions in merge state
- 1.2 GraphQL as the source of truth
  - 1.2.1 GraphQL query for merge state
  - 1.2.2 Interpreting MergeStateStatus values
- 1.3 MergeStateStatus values explained
  - 1.3.1 MERGEABLE - safe to merge
  - 1.3.2 CONFLICTING - conflicts exist
  - 1.3.3 UNKNOWN - state being computed
  - 1.3.4 BLOCKED - branch protection rules blocking
  - 1.3.5 BEHIND - branch needs update
  - 1.3.6 DIRTY - merge commit cannot be cleanly created
  - 1.3.7 UNSTABLE - failing required status checks
- 1.4 Pre-merge verification checklist
  - 1.4.1 Required checks before merge
  - 1.4.2 Verification script usage

### Merge Strategies

See [references/merge-strategies.md](references/merge-strategies.md):

- 2.1 Merge commit strategy
  - 2.1.1 When to use merge commits
  - 2.1.2 Commit history implications
- 2.2 Squash merge strategy
  - 2.2.1 When to use squash merge
  - 2.2.2 Commit message handling
- 2.3 Rebase merge strategy
  - 2.3.1 When to use rebase merge
  - 2.3.2 Linear history benefits
- 2.4 Branch protection implications
  - 2.4.1 Required status checks
  - 2.4.2 Required reviewers
  - 2.4.3 Allowed merge methods
- 2.5 Delete branch after merge
  - 2.5.1 Automatic branch deletion
  - 2.5.2 Manual branch deletion

### Auto-Merge Configuration

See [references/auto-merge.md](references/auto-merge.md):

- 3.1 Setting up auto-merge via GraphQL API
  - 3.1.1 EnablePullRequestAutoMerge mutation
  - 3.1.2 Required permissions
- 3.2 Requirements for auto-merge
  - 3.2.1 Repository settings
  - 3.2.2 Branch protection rules
  - 3.2.3 Required status checks
- 3.3 Canceling auto-merge
  - 3.3.1 DisablePullRequestAutoMerge mutation
  - 3.3.2 When auto-merge is automatically canceled
- 3.4 Auto-merge with required reviewers
  - 3.4.1 Approval requirements
  - 3.4.2 Review dismissal handling

## Common Workflows

### Workflow 1: Standard PR Merge

```bash
# 1. Verify not already merged
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo
# Exit 0 means not merged, continue

# 2. Check readiness
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo
# Exit 0 means ready

# 3. Merge with squash
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch

# 4. Verify merge completed
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo
# Exit 1 confirms merged
```

### Workflow 2: Auto-Merge Setup

```bash
# 1. Enable auto-merge (will merge when CI passes and reviews approved)
python scripts/amia_set_auto_merge.py --pr 123 --repo owner/repo --enable --merge-method SQUASH

# 2. Later, check if merged
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo
```

### Workflow 3: Emergency Merge (Skip CI)

```bash
# 1. Check readiness ignoring CI
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo --ignore-ci

# 2. If ready (exit 0), merge
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy merge
```

## Exit Codes (Standardized)

All scripts use standardized exit codes for consistent error handling:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Invalid parameters | Bad PR number, bad repo format |
| 2 | Resource not found | PR does not exist |
| 3 | API error | Network, rate limit, timeout |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | PR already merged (no action needed) |
| 6 | Not mergeable | PR closed, conflicts, CI failing, reviews needed |

### Per-Script Exit Code Details

| Script | Exit 5 (Idempotency) | Exit 6 (Not Mergeable) |
|--------|---------------------|------------------------|
| amia_test_pr_merged.py | PR already merged | N/A |
| amia_test_pr_merge_ready.py | N/A | Any blocking condition (see JSON for details) |
| amia_merge_pr.py | PR already merged | Conflicts, closed, not approved |
| amia_set_auto_merge.py | PR already merged | Cannot enable auto-merge |

## Examples

### Example 1: Complete PR Merge Workflow

```bash
# Check if PR is already merged
python scripts/amia_test_pr_merged.py --pr 123 --repo owner/repo
# Output: {"merged": false, "state": "OPEN"}

# Check if PR is ready to merge
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo
# Output: {"ready": true, "merge_state": "MERGEABLE"}

# Execute the merge
python scripts/amia_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch
# Output: {"success": true, "merged_at": "2025-01-30T10:00:00Z"}
```

### Example 2: Enable Auto-Merge for CI-Pending PR

```bash
# Enable auto-merge - PR will merge when CI passes
python scripts/amia_set_auto_merge.py --pr 456 --repo owner/repo --enable --merge-method SQUASH
# Output: {"auto_merge_enabled": true}
```

## Error Handling

### PR shows as not merged but merge failed

1. Run `amia_test_pr_merged.py` to get authoritative state
2. Check GraphQL output for actual merge state
3. If truly not merged, check `amia_test_pr_merge_ready.py` for blockers

### Auto-merge not triggering

1. Verify repository has auto-merge enabled in settings
2. Check branch protection rules allow auto-merge
3. Verify required status checks are configured
4. Use `amia_test_pr_merge_ready.py` to see blocking reasons

### Merge state showing UNKNOWN

This is temporary - GitHub is computing the merge state. Wait 5-10 seconds and retry. The scripts handle this with automatic retries.

### Protected branch preventing merge

Check:
1. Required status checks passing
2. Required number of approvals met
3. Allowed merge methods in branch protection
4. No CODEOWNERS blocking reviews

---

## SAFETY WARNING: Destructive Operations

### IRREVERSIBLE Operations

The following PR merge operations are **IRREVERSIBLE** or have significant impact:

| Operation | Risk | Mitigation |
|-----------|------|------------|
| `git push --force` | Overwrites remote history, loses commits | NEVER use on shared branches; requires explicit approval |
| Merge without PR | Bypasses review process, no audit trail | ALWAYS use PR workflow |
| Squash merge | Original commits are lost from branch history | Acceptable if commits were WIP; verify first |
| Delete branch after merge | Cannot recover branch pointer | Commits still exist; can recreate branch if needed |
| Force merge ignoring CI | May introduce broken code to main | Only with explicit user approval and documented reason |

### BEFORE ANY DESTRUCTIVE OPERATION

1. **Verify you have a backup branch**
   ```bash
   # Create backup before any risky operation
   git branch backup-pre-merge-$(date +%Y%m%d) HEAD
   ```

2. **Confirm with orchestrator** before:
   - Any `--force` push operations
   - Merging with failing CI (using `--ignore-ci`)
   - Merging with unresolved threads (using `--ignore-threads`)

3. **Log the operation details**
   ```bash
   echo "$(date): Merging PR #${PR_NUMBER} - Strategy: ${STRATEGY} - Flags: ${FLAGS}" >> merge-ops.log
   ```

### Safe Merge Checklist

- [ ] PR has been reviewed and approved
- [ ] All CI checks pass (or explicit approval to bypass)
- [ ] No unresolved review threads (or explicit approval to bypass)
- [ ] Branch is up-to-date with target branch
- [ ] Merge strategy selected (merge/squash/rebase)
- [ ] Branch deletion policy confirmed
- [ ] Verify merge with `amia_test_pr_merged.py` after completion

### Rollback After Bad Merge

If a merge introduces issues:

```bash
# Option 1: Revert the merge commit (creates new commit, preserves history)
git revert -m 1 <merge-commit-hash>
git push origin main

# Option 2: Reset to pre-merge state (DESTRUCTIVE - requires --force push)
# Only use if revert is not possible
git reset --hard <commit-before-merge>
git push --force origin main  # REQUIRES EXPLICIT APPROVAL

# Option 3: Create hotfix branch and new PR
git checkout -b hotfix/revert-pr-${PR_NUMBER}
git revert -m 1 <merge-commit-hash>
git push -u origin hotfix/revert-pr-${PR_NUMBER}
gh pr create --title "Revert PR #${PR_NUMBER}" --body "Reverting due to: [REASON]"
```

---

## Script Locations

All scripts are in the `scripts/` directory of this skill:

```
scripts/
├── amia_test_pr_merged.py      # Check if PR is merged
├── amia_test_pr_merge_ready.py # Check merge eligibility
├── amia_merge_pr.py            # Execute merge
└── amia_set_auto_merge.py      # Enable/disable auto-merge
```

Each script outputs JSON to stdout for easy parsing by automation tools.

## Resources

- [references/merge-state-verification.md](references/merge-state-verification.md) - GraphQL merge state verification
- [references/merge-strategies.md](references/merge-strategies.md) - Merge strategy selection guide
- [references/auto-merge.md](references/auto-merge.md) - Auto-merge configuration reference
