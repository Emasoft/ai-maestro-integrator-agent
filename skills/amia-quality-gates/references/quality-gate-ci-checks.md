---
name: quality-gate-ci-checks
description: "Which CI checks to verify before approving a PR through pre-merge gate."
---

# CI Check Verification for Quality Gates

## Table of Contents

- [1. When to Check CI Status Before Approving a PR](#1-when-to-check-ci-status-before-approving-a-pr)
- [2. Which CI Checks Are Mandatory vs Advisory](#2-which-ci-checks-are-mandatory-vs-advisory)
  - [2.1 Mandatory checks that block the pre-merge gate](#21-mandatory-checks-that-block-the-pre-merge-gate)
  - [2.2 Advisory checks that produce warnings but do not block](#22-advisory-checks-that-produce-warnings-but-do-not-block)
  - [2.3 Determining mandatory vs advisory from repository settings](#23-determining-mandatory-vs-advisory-from-repository-settings)
- [3. How to Read the GitHub Checks API for Pass or Fail Status](#3-how-to-read-the-github-checks-api-for-pass-or-fail-status)
  - [3.1 Listing checks and querying the API](#31-listing-checks-and-querying-the-api)
  - [3.2 Interpreting the conclusion and status fields](#32-interpreting-the-conclusion-and-status-fields)
- [4. What to Do When a CI Check Is Skipped (Path-Filtered)](#4-what-to-do-when-a-ci-check-is-skipped-path-filtered)
- [5. What to Do When a CI Check Is Stale (Outdated, Needs Re-Run)](#5-what-to-do-when-a-ci-check-is-stale-outdated-needs-re-run)
- [6. What to Do When a CI Check Times Out](#6-what-to-do-when-a-ci-check-times-out)
- [7. How to Differentiate Infrastructure Flakes from Real Failures](#7-how-to-differentiate-infrastructure-flakes-from-real-failures)
- [8. Decision Table: CI Status to Gate Action Mapping](#8-decision-table-ci-status-to-gate-action-mapping)
- [9. Integration with the Gate Pipeline](#9-integration-with-the-gate-pipeline)
- [10. Troubleshooting](#10-troubleshooting)

---

## 1. When to Check CI Status Before Approving a PR

CI status verification is required whenever the PR reaches the **pre-merge gate**. It is also triggered when a reviewer approves a PR before CI completes, when new commits are pushed after CI passed, or when a re-run is requested after a prior failure. CI verification is a sub-step of the pre-merge gate (the third gate in the four-gate pipeline). For the full gate flow see [gate-pipeline.md](gate-pipeline.md). For the complete pre-merge gate procedure see [pre-merge-gate.md](pre-merge-gate.md).

---

## 2. Which CI Checks Are Mandatory vs Advisory

### 2.1 Mandatory checks that block the pre-merge gate

1. **Lint passed (all languages)**: Every linting job must show conclusion `success`.
2. **Tests passed (all matrix entries)**: Every test matrix entry must pass independently. If the matrix has 4 entries, all 4 must succeed.
3. **Security scan clean (no HIGH severity)**: No findings of HIGH or CRITICAL severity. MEDIUM/LOW produce warnings only.
4. **Coverage threshold met (if configured)**: Reported coverage must meet or exceed the configured threshold.
5. **Gate job shows success**: If the repository defines an aggregating gate job, it must show `success`.

### 2.2 Advisory checks that produce warnings but do not block

- Documentation build (spelling, link checks)
- Performance benchmarks (unless configured as mandatory)
- Code style suggestions beyond the linter
- Dependency license scanning (unless configured as mandatory)

### 2.3 Determining mandatory vs advisory from repository settings

```bash
gh api repos/{owner}/{repo}/branches/main/protection/required_status_checks --jq '.contexts[]'
```

Any check name returned is **mandatory**. All others are **advisory** unless documented otherwise in CONTRIBUTING.md.

---

## 3. How to Read the GitHub Checks API for Pass or Fail Status

### 3.1 Listing checks and querying the API

```bash
# Quick summary of all checks on a PR
gh pr checks $PR_NUMBER

# Detailed per-check status via API
PR_SHA=$(gh pr view $PR_NUMBER --json headRefOid --jq '.headRefOid')
gh api "repos/{owner}/{repo}/commits/$PR_SHA/check-runs" \
  --jq '.check_runs[] | {name: .name, status: .status, conclusion: .conclusion}'
```

### 3.2 Interpreting the conclusion and status fields

**status** field: `queued` (waiting), `in_progress` (running), `completed` (finished -- check `conclusion`).

**conclusion** field (when status is `completed`):
- `success` -- passed
- `failure` -- failed (test or validation error)
- `neutral` -- no pass/fail assertion
- `cancelled` -- cancelled before completion
- `skipped` -- skipped (see section 4)
- `timed_out` -- exceeded time limit (see section 6)
- `action_required` -- needs manual follow-up
- `stale` -- outdated results (see section 5)

**Gate rule**: Only `success` counts as a pass for mandatory checks.

---

## 4. What to Do When a CI Check Is Skipped (Path-Filtered)

A skip is **legitimate** if the CI workflow has path filters, the PR's changed files do not match those paths, and the check is not in the branch protection required list. Verify with `gh pr diff $PR_NUMBER --name-only` and compare against the workflow's `paths` key.

A skip is **illegitimate** if the PR modifies files that should trigger the check, or the check is required by branch protection. In that case, block the pre-merge gate and comment:

```bash
gh pr comment $PR_NUMBER --body "Pre-merge gate blocked: CI check '$CHECK_NAME' was skipped unexpectedly.
Possible causes: path filter too broad, workflow modified in this PR, or GitHub Actions issue.
Please investigate and re-trigger the workflow."
```

---

## 5. What to Do When a CI Check Is Stale (Outdated, Needs Re-Run)

A check is stale when it ran against a commit that is no longer the PR HEAD (new commits pushed after CI completed). Detect by comparing `head_sha` in check-run results against the current PR HEAD:

```bash
PR_HEAD=$(gh pr view $PR_NUMBER --json headRefOid --jq '.headRefOid')
gh api "repos/{owner}/{repo}/commits/$PR_HEAD/check-runs" \
  --jq '.check_runs[] | {name: .name, head_sha: .head_sha}'
```

Request re-run: `gh run rerun $RUN_ID` (find run ID with `gh run list --branch $PR_BRANCH --limit 5`). Do not approve the gate while any mandatory check is stale.

---

## 6. What to Do When a CI Check Times Out

A `timed_out` conclusion means the job exceeded its time limit. Check logs with `gh run view $RUN_ID --log-failed` and determine the cause:

- **Infrastructure issue** (runner slow, network stalled): Re-run. If successful, apply `gate:flaky-infra` label.
- **Code issue** (test or build genuinely too slow): Block the gate. Request optimization or timeout increase.
- **Resource exhaustion** (out of memory, disk full): Block the gate. Request investigation.

---

## 7. How to Differentiate Infrastructure Flakes from Real Failures

**Flake indicators**: Same test fails intermittently across unrelated PRs; one matrix entry fails while others pass on identical code; re-run without code changes passes; failure message references network or runner infrastructure.

**Real failure indicators**: Failing test exercises code modified in this PR; failure is consistent across re-runs; message references assertion, type, syntax, or logic errors; multiple matrix entries fail identically.

When a flake is identified, apply `gate:flaky-test` label, comment with evidence (failed run ID, passed re-run ID, same SHA), and open or update a tracking issue. Allow the gate to pass if re-run succeeds and all mandatory checks pass.

---

## 8. Decision Table: CI Status to Gate Action Mapping

| Check Type | Conclusion        | Gate Action                              | Label                  |
|------------|-------------------|------------------------------------------|------------------------|
| Mandatory  | `success`         | Pass (count toward approval)             | None                   |
| Mandatory  | `failure`         | Block gate, comment with details         | `gate:ci-failed`       |
| Mandatory  | `cancelled`       | Block gate, request re-run               | `gate:ci-cancelled`    |
| Mandatory  | `timed_out`       | Block gate, investigate (section 6)      | `gate:ci-timeout`      |
| Mandatory  | `skipped`         | Check if legitimate (section 4)          | `gate:ci-skipped`      |
| Mandatory  | `action_required` | Block gate, follow up on actions         | `gate:ci-action-needed`|
| Mandatory  | `stale`           | Block gate, request re-run (section 5)   | `gate:ci-stale`        |
| Mandatory  | `in_progress`     | Wait until completed                     | None                   |
| Mandatory  | `queued`          | Wait until completed                     | None                   |
| Advisory   | `success`         | No action                                | None                   |
| Advisory   | `failure`         | Warning comment, do not block            | `gate:advisory-warning`|
| Advisory   | Any other         | Warning comment, do not block            | `gate:advisory-warning`|

The pre-merge gate passes only when every mandatory check shows `success` on the current HEAD commit.

---

## 9. Integration with the Gate Pipeline

**Sequence within the pre-merge gate**:
1. Verify CI status (this document)
2. Verify changelog (see [quality-gate-changelog.md](quality-gate-changelog.md))
3. Verify no merge conflicts (see [pre-merge-gate.md](pre-merge-gate.md), section 2)
4. Verify valid approval (see [pre-merge-gate.md](pre-merge-gate.md), section 3)
5. Verify branch is up-to-date (see [pre-merge-gate.md](pre-merge-gate.md), section 4)

If CI verification fails, the remaining checks are still evaluated so all issues are surfaced in one pass, but the gate is blocked regardless.

---

## 10. Troubleshooting

### All checks stuck in `queued`

Check the repository's GitHub Actions concurrency limit, verify runner labels match available runners, and check if first-time contributor workflow approval is pending.

### Required check name missing from checks list

The workflow may not have triggered (check path filters and trigger events), the check name may not match branch protection rules, or the workflow file was deleted/renamed.

### Re-run fails with "workflow file changed"

Re-runs use the workflow from the original triggering commit. If the workflow was modified in the PR, push a new commit (`git commit --allow-empty`) to trigger a fresh run.

### Check shows passed but branch protection still blocks

The branch protection may require a check name that differs from the displayed name, or a "required reviews" policy is also blocking. Verify with:

```bash
gh api repos/{owner}/{repo}/branches/main/protection/required_status_checks --jq '.contexts[]'
```

Compare returned names against `gh pr checks` output.
