---
name: op-document-failure
description: Document gate failure reasons in PR comments
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Document Gate Failure


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Documentation Structure](#documentation-structure)
- [<Gate Name> Gate Failed](#gate-name-gate-failed)
  - [Summary](#summary)
  - [Issues Found](#issues-found)
  - [Required Actions](#required-actions)
  - [Next Steps](#next-steps)
- [Steps](#steps)
  - [Step 1: Categorize Issues by Severity](#step-1-categorize-issues-by-severity)
  - [Step 2: Format Issue Details](#step-2-format-issue-details)
  - [Step 3: Create Comment](#step-3-create-comment)
- [<GATE> Gate Failed](#gate-gate-failed)
  - [Summary](#summary)
  - [Critical Issues (Must Fix)](#critical-issues-must-fix)
  - [Major Issues (Should Fix)](#major-issues-should-fix)
  - [Required Actions](#required-actions)
  - [Next Steps](#next-steps)
  - [Step 4: Add Code Suggestions (Optional)](#step-4-add-code-suggestions-optional)
- [Templates by Gate Type](#templates-by-gate-type)
  - [Pre-Review Gate Failure](#pre-review-gate-failure)
- [Pre-Review Gate Failed](#pre-review-gate-failed)
  - [CI Check Failures](#ci-check-failures)
  - [Test Failures](#test-failures)
  - [Linting Errors](#linting-errors)
  - [Required Actions](#required-actions)
  - [Review Gate Failure](#review-gate-failure)
- [Review Gate Failed](#review-gate-failed)
  - [Dimension Scores](#dimension-scores)
  - [Critical Issues](#critical-issues)
  - [Pre-Merge Gate Failure](#pre-merge-gate-failure)
- [Pre-Merge Gate Failed](#pre-merge-gate-failed)
  - [Blocking Issues](#blocking-issues)
  - [Resolution Steps](#resolution-steps)
- [Example](#example)
- [Review Gate Failed](#review-gate-failed)
  - [Summary](#summary)
  - [Critical Issues (Must Fix)](#critical-issues-must-fix)
  - [Major Issues (Should Fix)](#major-issues-should-fix)
  - [Required Actions](#required-actions)
  - [Next Steps](#next-steps)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Create clear, actionable documentation of gate failures in PR comments so authors and reviewers understand exactly what needs to be fixed.

## When to Use

- When any quality gate fails
- When requesting changes on a PR
- When providing feedback that blocks progression

## Prerequisites

- Gate failure identified
- Specific issues catalogued
- Remediation steps known

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| gate | string | Yes | Which gate failed |
| issues | array | Yes | List of issues found |
| severity_map | object | No | Severity for each issue |

## Output

| Field | Type | Description |
|-------|------|-------------|
| comment_url | string | URL to the created comment |
| issues_documented | integer | Count of issues documented |

## Documentation Structure

```markdown
## <Gate Name> Gate Failed

**Date**: <TIMESTAMP>
**Reviewer**: <AGENT_NAME>

### Summary
<Brief overview of why gate failed>

### Issues Found

#### Critical Issues (Must Fix)
| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| 1 | file:line | description | how to fix |

#### Major Issues (Should Fix)
| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| 1 | file:line | description | how to fix |

#### Minor Issues (Consider Fixing)
| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| 1 | file:line | description | how to fix |

### Required Actions
- [ ] Action 1
- [ ] Action 2

### Next Steps
1. Fix the issues listed above
2. Push updated code
3. Request re-review
```

## Steps

### Step 1: Categorize Issues by Severity

| Severity | Definition | Must Fix? |
|----------|------------|-----------|
| Critical | Blocks functionality or security | Yes |
| Major | Significant quality/maintainability issue | Yes |
| Minor | Style/preference/optimization | No |

### Step 2: Format Issue Details

For each issue, include:
- **Location**: `file_path:line_number`
- **Issue**: Clear description of the problem
- **Impact**: Why this matters
- **Suggested Fix**: How to resolve it

### Step 3: Create Comment

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## <GATE> Gate Failed

**Date**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

### Summary
This PR did not pass the <GATE> gate due to <REASON>.

### Critical Issues (Must Fix)

| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
<CRITICAL_ISSUES_TABLE>

### Major Issues (Should Fix)

| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
<MAJOR_ISSUES_TABLE>

### Required Actions
<CHECKLIST>

### Next Steps
1. Address all critical and major issues
2. Push updated code to this branch
3. The gate will automatically re-run

If you have questions, comment on this PR or reach out to the reviewer.
EOF
)"
```

### Step 4: Add Code Suggestions (Optional)

For specific code issues, use GitHub's suggestion feature:

```bash
gh pr review <NUMBER> --comment --body '```suggestion
<CORRECTED_CODE>
```'
```

## Templates by Gate Type

### Pre-Review Gate Failure

```markdown
## Pre-Review Gate Failed

### CI Check Failures

| Check | Status | Details |
|-------|--------|---------|
| Tests | FAILED | 3 tests failing in `test_auth.py` |
| Lint | FAILED | 5 linting errors |
| Build | PASSED | - |

### Test Failures
```
test_auth.py::test_login_invalid_password FAILED
test_auth.py::test_token_expiry FAILED
test_auth.py::test_refresh_token FAILED
```

### Linting Errors
```
src/auth.py:42:1: E302 expected 2 blank lines
src/auth.py:67:80: E501 line too long
```

### Required Actions
- [ ] Fix failing tests
- [ ] Run `ruff format` to fix linting
- [ ] Push updated code
```

### Review Gate Failure

```markdown
## Review Gate Failed

**Confidence Score**: 72% (Required: 80%)

### Dimension Scores

| Dimension | Score | Status |
|-----------|-------|--------|
| Security | 65% | **BLOCKING** |
| Functional | 80% | OK |
| Testing | 70% | Warning |
| ... | ... | ... |

### Critical Issues

1. **SQL Injection Vulnerability** (Security)
   - Location: `src/db/queries.py:42`
   - Issue: User input concatenated into SQL query
   - Fix: Use parameterized queries
   ```python
   # Bad
   query = f"SELECT * FROM users WHERE id = {user_id}"

   # Good
   query = "SELECT * FROM users WHERE id = ?"
   cursor.execute(query, (user_id,))
   ```
```

### Pre-Merge Gate Failure

```markdown
## Pre-Merge Gate Failed

### Blocking Issues

| Issue | Details |
|-------|---------|
| Merge Conflicts | Conflicts in `src/main.py`, `config/settings.py` |
| CI Failing | Test suite failing on latest commit |

### Resolution Steps

1. **Resolve merge conflicts**:
   ```bash
   git fetch origin
   git merge origin/main
   # Resolve conflicts in affected files
   git add .
   git commit -m "Resolve merge conflicts"
   git push
   ```

2. **Investigate CI failure**:
   - Check CI logs (check your CI/CD pipeline dashboard for build logs)
   - Fix any issues and push
```

## Example

```bash
# Document review gate failure
gh pr comment 123 --body "$(cat <<'EOF'
## Review Gate Failed

**Date**: 2025-02-05T14:30:00Z
**Confidence Score**: 68%

### Summary
This PR failed the review gate primarily due to security concerns and insufficient test coverage.

### Critical Issues (Must Fix)

| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| 1 | src/api/auth.py:42 | Hardcoded API key | Move to environment variable |
| 2 | src/db/user.py:87 | SQL injection risk | Use parameterized queries |

### Major Issues (Should Fix)

| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| 1 | src/handlers/upload.py | No input validation | Add file type/size checks |
| 2 | tests/ | Low coverage (45%) | Add unit tests for new code |

### Required Actions
- [ ] Remove hardcoded credentials
- [ ] Fix SQL injection vulnerability
- [ ] Add input validation
- [ ] Increase test coverage to >70%

### Next Steps
1. Address all critical issues (blocking)
2. Address major issues
3. Push updated code
4. Request re-review

Questions? Comment on this PR.
EOF
)"
```

## Error Handling

| Error | Action |
|-------|--------|
| Comment too long | Split into multiple comments |
| Formatting issues | Use plain text fallback |
| Cannot comment | Check permissions, retry |

## Related Operations

- [op-escalate-failure.md](op-escalate-failure.md) - Escalation after documenting
- [op-apply-gate-label.md](op-apply-gate-label.md) - Apply failure label
