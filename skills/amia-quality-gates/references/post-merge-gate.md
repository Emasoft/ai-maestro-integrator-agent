# Post-Merge Gate

## Table of Contents

- [Purpose](#purpose)
- [Required Checks](#required-checks)
  - [1. Main Branch Build Success](#1-main-branch-build-success)
  - [2. No Regressions Detected](#2-no-regressions-detected)
  - [3. Deployment Success (if applicable)](#3-deployment-success-if-applicable)
- [Blocking Conditions](#blocking-conditions)
- [Gate Pass Procedure](#gate-pass-procedure)
- [Gate Fail Procedure](#gate-fail-procedure)
- [Revert Decision Matrix](#revert-decision-matrix)
- [Revert Procedure](#revert-procedure)
- [Hotfix vs Revert Decision](#hotfix-vs-revert-decision)
- [Monitoring Period](#monitoring-period)
- [Troubleshooting](#troubleshooting)
  - [False Positive Regression](#false-positive-regression)
  - [Deployment Failed but Code is Fine](#deployment-failed-but-code-is-fine)
  - [Main Branch was Already Broken](#main-branch-was-already-broken)
  - [Multiple Merges Simultaneously](#multiple-merges-simultaneously)

## Purpose

The Post-Merge Gate verifies that the merged code integrates cleanly into main and does not break the main branch or introduce regressions.

## Required Checks

### 1. Main Branch Build Success

**Check**: Main branch builds successfully after merge
**Command**: Monitor main branch CI status
**Pass Criteria**: Main CI pipeline completes successfully
**Failure Action**: Immediate escalation, consider revert

**Monitoring**:

```bash
# Check main branch status
gh run list --branch main --limit 1

# Watch main CI
gh run watch <RUN_ID>
```

### 2. No Regressions Detected

**Check**: Existing tests still pass, no new failures
**Command**: Compare main test results pre/post merge
**Pass Criteria**: No new test failures introduced
**Failure Action**: Immediate escalation, evaluate revert

### 3. Deployment Success (if applicable)

**Check**: Automated deployment succeeds
**Command**: Monitor deployment pipeline status
**Pass Criteria**: Deployment completes without errors
**Failure Action**: Rollback deployment, evaluate revert

## Blocking Conditions

These issues **always trigger immediate action**:

| Issue Type | Immediate Action | Follow-Up |
|------------|------------------|-----------|
| Main CI fails | Notify author/reviewer/AMOA | Evaluate revert vs hotfix |
| Test regression | Notify team | Revert if critical, hotfix if minor |
| Deployment fails | Rollback deployment | Investigate deployment issue |
| Production error spike | Alert on-call | Emergency response |

## Gate Pass Procedure

```bash
# Verify main branch health
gh run list --branch main --limit 1 --json conclusion -q '.[0].conclusion'
# Should return "success"

# Apply passed label to original PR
gh pr edit $PR_NUMBER --add-label "gate:post-merge-passed"

# Close linked issue with success message
gh issue close $ISSUE_NUMBER --comment "✅ Integration complete. Post-merge gate passed.

- Main branch build: SUCCESS
- Regressions: None detected
- Deployment: SUCCESS

Changes merged successfully."
```

## Gate Fail Procedure

```bash
# Apply failed label
gh pr edit $PR_NUMBER --add-label "gate:post-merge-failed"

# Immediate notification
gh pr comment $PR_NUMBER --body "🚨 **POST-MERGE GATE FAILED**

Main branch health check failed after merge.

**Issue**: [Describe failure - CI failure, regression, deployment issue]

@author @reviewer @amoa - Immediate attention required.

**Recommendation**: Evaluate revert vs hotfix within 30 minutes."

# Document in original issue
gh issue reopen $ISSUE_NUMBER
gh issue comment $ISSUE_NUMBER --body "Post-merge failure detected. See PR #${PR_NUMBER} for details.

Status: Evaluating revert options."

# Follow Escalation Path D
```

## Revert Decision Matrix

| Failure Severity | Revert? | Alternative |
|------------------|---------|-------------|
| Main branch broken | YES - Immediate | None (revert required) |
| Minor regression | NO | Hotfix within 2 hours |
| Deployment failed | MAYBE | Rollback deployment first, then decide |
| Flaky test failure | NO | Fix test, do not revert |

## Revert Procedure

```bash
# Create revert PR
gh pr create --title "Revert: <Original PR Title>" \
  --body "Reverts PR #${PR_NUMBER}

**Reason**: Post-merge gate failure
**Failure**: [Describe what failed]
**Impact**: [Describe production impact]

Original PR will be fixed and re-submitted."

# Fast-track revert through gates
# (Reverts bypass some gates if main is broken)

# Merge revert immediately
gh pr merge $REVERT_PR_NUMBER --admin --squash

# Document revert
gh issue comment $ISSUE_NUMBER --body "Reverted via PR #${REVERT_PR_NUMBER}

Author can fix issues and re-submit PR."
```

## Hotfix vs Revert Decision

**Choose Hotfix when**:

- Fix is trivial (< 10 lines)
- Hotfix can be deployed within 1 hour
- Impact is minor (no user-facing breakage)
- Team has high confidence in hotfix

**Choose Revert when**:

- Main branch is broken
- Fix is complex or uncertain
- Impact is severe
- Fix timeline > 1 hour
- Any doubt about hotfix safety

**Default**: When in doubt, revert. Reverts are safer.

## Monitoring Period

Post-merge monitoring continues for:

- **Immediate** (0-15 minutes): CI completion, deployment success
- **Short-term** (15 minutes - 2 hours): Error rate monitoring, performance metrics
- **Medium-term** (2-24 hours): Regression detection, user feedback

## Troubleshooting

### False Positive Regression

**Symptom**: Test failure on main, but unrelated to merged PR

**Resolution**:

1. Verify test was passing before merge
2. Check if flaky test (historical flakiness)
3. Check if parallel merge caused issue
4. If unrelated, do not revert - fix flaky test

### Deployment Failed but Code is Fine

**Symptom**: Code is correct, deployment infrastructure failed

**Resolution**:

1. Do not revert code
2. Rollback deployment
3. Fix deployment infrastructure
4. Re-deploy
5. Mark post-merge gate passed once deployment succeeds

### Main Branch was Already Broken

**Symptom**: Main CI was failing before this merge

**Resolution**:

1. Verify main status before merge timestamp
2. If main was already broken, not this PR's fault
3. Do not revert this PR
4. Escalate main branch health issue to team
5. Fix main branch root cause

### Multiple Merges Simultaneously

**Symptom**: Multiple PRs merged around same time, unclear which broke main

**Resolution**:

1. Review all recent merges (git log)
2. Revert most recent merge first
3. Test if main recovers
4. If not, revert next most recent
5. Identify culprit PR through process of elimination
6. Only revert necessary PRs
