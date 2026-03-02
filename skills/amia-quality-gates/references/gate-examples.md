# Quality Gate Examples

## Table of Contents

- [Example 1: Pre-Review Gate Success](#example-1-pre-review-gate-success)
- [Example 2: Review Gate Failure (Low Confidence)](#example-2-review-gate-failure-low-confidence)
- [Example 3: Pre-Merge Gate Failure (Merge Conflict)](#example-3-pre-merge-gate-failure-merge-conflict)
- [Example 4: Post-Merge Gate Failure (Main Branch Broken)](#example-4-post-merge-gate-failure-main-branch-broken)
- [Example 5: Gate Override Application](#example-5-gate-override-application)

This document provides practical examples of quality gate enforcement across all four gates.

## Example 1: Pre-Review Gate Success

**Scenario**: New PR opened with passing checks.

**Actions**:
```bash
# Check PR tests
gh pr checks $PR_NUMBER

# All passing, apply label
gh pr edit $PR_NUMBER --add-label "gate:pre-review-passed"

# Comment on PR
gh pr comment $PR_NUMBER --body "✅ Pre-review gate passed. Ready for code review."
```

## Example 2: Review Gate Failure (Low Confidence)

**Scenario**: Code review yields 65% confidence score.

**Actions**:
```bash
# Apply failed label
gh pr edit $PR_NUMBER --add-label "gate:review-failed"

# Request changes via review
gh pr review $PR_NUMBER --request-changes --body "**Review Gate: FAILED**

Confidence Score: 65% (threshold: 80%)

Issues identified:
- Insufficient test coverage (Coverage: 45%, expected: 80%)
- Missing error handling in payment processing
- No documentation for new API endpoints

Please address these issues and request re-review."
```

## Example 3: Pre-Merge Gate Failure (Merge Conflict)

**Scenario**: PR has merge conflicts with main.

**Actions**:
```bash
# Apply failed label
gh pr edit $PR_NUMBER --add-label "gate:pre-merge-failed"

# Notify author
gh pr comment $PR_NUMBER --body "❌ Pre-merge gate failed: Merge conflicts detected

Please rebase your branch:
\`\`\`bash
git fetch origin
git rebase origin/main
git push --force-with-lease
\`\`\`

Re-run gate checks after resolving conflicts."
```

## Example 4: Post-Merge Gate Failure (Main Branch Broken)

**Scenario**: Main CI fails after merge.

**Actions**:
```bash
# Apply failed label
gh pr edit $PR_NUMBER --add-label "gate:post-merge-failed"

# Immediate escalation
gh pr comment $PR_NUMBER --body "🚨 **POST-MERGE GATE FAILED**: Main branch CI broken

@author @reviewer @eoa - Immediate attention required.

Failure: Main branch tests failing in auth module

Recommend: Evaluate revert vs hotfix within 30 minutes."

# Document in issue
gh issue comment $ISSUE_NUMBER --body "Post-merge failure detected. Evaluating revert options."
```

## Example 5: Gate Override Application

**Scenario**: Urgent hotfix needs pre-merge gate override.

**Actions**:
```bash
# Document override
gh pr comment $PR_NUMBER --body "**GATE OVERRIDE**

Gate: Pre-Merge Gate
Reason: Critical security hotfix for CVE-2024-XXXX
Approved by: @maintainer
Risk mitigation:
  - Manual testing completed
  - Hotfix branch will be monitored post-deploy
  - Follow-up PR will add automated tests
Follow-up: Issue #XYZ tracks test coverage addition"

# Apply override label
gh pr edit $PR_NUMBER --add-label "gate:override-applied"

# Proceed with merge
gh pr merge $PR_NUMBER --squash
```
