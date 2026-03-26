# GitHub PR Merge Operations -- Detailed Guide

## Table of Contents

- [Decision Tree](#decision-tree-for-pr-merge-operations)
- [GraphQL Source of Truth](#graphql-is-the-source-of-truth)
- [Script Usage Details](#script-usage-details)
- [Common Workflows](#common-workflows)
- [Exit Codes Reference](#exit-codes-reference)
- [Error Handling](#error-handling)
- [Safety Warning](#safety-warning-destructive-operations)
- [Script Locations](#script-locations)

## GraphQL is the Source of Truth

**NEVER trust `gh pr view --json state` for merge state verification.**

The REST API and `gh pr view` can return stale data. GraphQL queries against the GitHub API provide the authoritative, real-time merge state. Always use GraphQL for:

- Checking if a PR is already merged
- Verifying merge eligibility (MergeStateStatus)
- Confirming merge completion

## Decision Tree for PR Merge Operations

```
START: Need to merge a PR
    |
    +-> Is PR already merged?
    |   Run: amia_test_pr_merged.py --pr <number> --repo <owner/repo>
    |       |
    |       +-> Exit 1 (merged) -> STOP: PR already merged
    |       |
    |       +-> Exit 0 (not merged) -> Continue
    |
    +-> Is PR ready to merge?
    |   Run: amia_test_pr_merge_ready.py --pr <number> --repo <owner/repo>
    |       |
    |       +-> Exit 0 (ready) -> Proceed to merge
    |       +-> Exit 1 (CI failing) -> Fix CI or use --ignore-ci
    |       +-> Exit 2 (conflicts) -> Resolve conflicts first
    |       +-> Exit 3 (threads) -> Resolve threads or use --ignore-threads
    |       +-> Exit 4 (reviews) -> Get required approvals
    |
    +-> Should merge now or auto-merge?
    |       |
    |       +-> Merge now:
    |       |   Run: amia_merge_pr.py --pr <number> --repo <owner/repo> \
    |       |        --strategy <merge|squash|rebase> [--delete-branch]
    |       |
    |       +-> Auto-merge when ready:
    |           Run: amia_set_auto_merge.py --pr <number> --repo <owner/repo> \
    |                --enable --merge-method <MERGE|SQUASH|REBASE>
    |
    +-> Verify merge completed:
        Run: amia_test_pr_merged.py --pr <number> --repo <owner/repo>
```

## Script Usage Details

### amia_test_pr_merged.py

Use BEFORE attempting any merge operation to avoid duplicate merge attempts, confusing error messages, and wasted API calls.

```bash
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

## Exit Codes Reference

All scripts use standardized exit codes:

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

This is temporary -- GitHub is computing the merge state. Wait 5-10 seconds and retry. The scripts handle this with automatic retries.

### Protected branch preventing merge

Check:

1. Required status checks passing
2. Required number of approvals met
3. Allowed merge methods in branch protection
4. No CODEOWNERS blocking reviews

## Safety Warning: Destructive Operations

### Irreversible Operations

| Operation | Risk | Mitigation |
|-----------|------|------------|
| `git push --force` | Overwrites remote history | NEVER use on shared branches; requires explicit approval |
| Merge without PR | Bypasses review process | ALWAYS use PR workflow |
| Squash merge | Original commits lost from branch | Acceptable if WIP; verify first |
| Delete branch after merge | Cannot recover branch pointer | Commits still exist; can recreate |
| Force merge ignoring CI | May introduce broken code | Only with explicit user approval |

### Before Any Destructive Operation

1. **Create a backup branch:**

   ```bash
   git branch backup-pre-merge-$(date +%Y%m%d) HEAD
   ```

2. **Confirm with orchestrator** before:
   - Any `--force` push operations
   - Merging with failing CI (using `--ignore-ci`)
   - Merging with unresolved threads (using `--ignore-threads`)

3. **Log the operation:**

   ```bash
   echo "$(date): Merging PR #${PR_NUMBER} - Strategy: ${STRATEGY}" >> merge-ops.log
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

```bash
# Option 1: Revert the merge commit (preserves history)
git revert -m 1 <merge-commit-hash>
git push origin main

# Option 2: Reset to pre-merge state (DESTRUCTIVE - requires --force push)
git reset --hard <commit-before-merge>
git push --force origin main  # REQUIRES EXPLICIT APPROVAL

# Option 3: Create hotfix branch and new PR
git checkout -b hotfix/revert-pr-${PR_NUMBER}
git revert -m 1 <merge-commit-hash>
git push -u origin hotfix/revert-pr-${PR_NUMBER}
gh pr create --title "Revert PR #${PR_NUMBER}" --body "Reverting due to: [REASON]"
```

## Script Locations

All scripts are in the `scripts/` directory of this skill:

```
scripts/
+-- amia_test_pr_merged.py      # Check if PR is merged
+-- amia_test_pr_merge_ready.py # Check merge eligibility
+-- amia_merge_pr.py            # Execute merge
+-- amia_set_auto_merge.py      # Enable/disable auto-merge
```

Each script outputs JSON to stdout for easy parsing by automation tools.

## Reference Documents Index

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
