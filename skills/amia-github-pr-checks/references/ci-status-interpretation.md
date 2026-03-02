# CI Status Interpretation Guide

This document provides detailed guidance on interpreting GitHub Pull Request check statuses, understanding the difference between check types, and handling results from various CI providers.

## Contents

- 1. Understanding GitHub Check Conclusions
  - 1.1 Complete list of conclusion values
  - 1.2 When each conclusion occurs
  - 1.3 How to respond to each conclusion
- 2. Required vs Optional Checks
  - 2.1 How branch protection defines required checks
  - 2.2 Identifying required checks programmatically
  - 2.3 Handling optional check failures
- 3. Check Run vs Check Suite
  - 3.1 Difference between check runs and check suites
  - 3.2 When to query which API endpoint
  - 3.3 Aggregating results from multiple providers
- 4. Common CI Providers
  - 4.1 GitHub Actions check naming conventions
  - 4.2 CircleCI integration patterns
  - 4.3 Jenkins GitHub plugin behavior
  - 4.4 Third-party status checks

---

## 1. Understanding GitHub Check Conclusions

### 1.1 Complete List of Conclusion Values

GitHub Checks API returns these possible `conclusion` values:

| Conclusion | Description |
|------------|-------------|
| `success` | The check completed successfully |
| `failure` | The check completed with failures |
| `neutral` | The check completed but is informational only |
| `cancelled` | The check was cancelled before completion |
| `skipped` | The check was skipped (condition not met) |
| `timed_out` | The check exceeded its time limit |
| `action_required` | The check requires manual intervention |
| `stale` | The check is outdated (new commit pushed) |
| `startup_failure` | The check failed to start (runner issue) |
| `null` | The check is still in progress (status: "in_progress" or "queued") |

### 1.2 When Each Conclusion Occurs

**success**
- All tests passed
- Build completed without errors
- Linting found no issues
- Security scan found no vulnerabilities

**failure**
- One or more tests failed
- Build compilation error
- Linting violations found
- Security vulnerabilities detected
- Code coverage below threshold

**neutral**
- Informational check (code coverage report)
- Optional advisory check
- Check configured to never fail

**cancelled**
- User manually cancelled the workflow
- Another workflow cancelled this one
- Concurrency group replaced this run

**skipped**
- Job condition evaluated to false
- Path filter excluded the job
- Dependent job failed (needs: condition)

**timed_out**
- Job exceeded `timeout-minutes` setting
- Step exceeded individual timeout
- Default 6-hour workflow limit reached

**action_required**
- Dependabot PR requires approval
- Manual approval step pending
- External review required

**stale**
- New commit pushed after check started
- Force push invalidated the check
- Check no longer relevant to current code

**startup_failure**
- Self-hosted runner unavailable
- Docker image pull failed
- Resource allocation failed

### 1.3 How to Respond to Each Conclusion

| Conclusion | Automated Response | Human Action Needed |
|------------|-------------------|---------------------|
| `success` | Proceed with merge/deploy | None |
| `failure` | Block merge, notify developer | Fix failing tests/code |
| `neutral` | Log informational result | Review if relevant |
| `cancelled` | Re-run if needed | Investigate if unexpected |
| `skipped` | Log skip reason | Verify skip conditions |
| `timed_out` | Re-run once, then escalate | Optimize CI performance |
| `action_required` | Notify appropriate reviewer | Complete required action |
| `stale` | Wait for new checks | Push or re-run |
| `startup_failure` | Alert ops team | Check runner health |

---

## 2. Required vs Optional Checks

### 2.1 How Branch Protection Defines Required Checks

Required checks are configured in repository settings under **Settings > Branches > Branch protection rules**.

Configuration options:
- **Require status checks to pass before merging**: Enables check requirements
- **Require branches to be up to date**: Forces rebase before merge
- **Status checks that are required**: List of check names

**Important**: Check names must match exactly, including case.

### 2.2 Identifying Required Checks Programmatically

Using gh CLI to get required checks:

```bash
# Get branch protection rules
gh api repos/OWNER/REPO/branches/main/protection \
  --jq '.required_status_checks.contexts[]'

# Get required checks with strict setting
gh api repos/OWNER/REPO/branches/main/protection \
  --jq '{
    strict: .required_status_checks.strict,
    checks: .required_status_checks.contexts
  }'
```

Using GraphQL for more detail:

```bash
gh api graphql -f query='
{
  repository(owner: "OWNER", name: "REPO") {
    branchProtectionRules(first: 10) {
      nodes {
        pattern
        requiredStatusChecks {
          context
        }
      }
    }
  }
}'
```

### 2.3 Handling Optional Check Failures

Optional checks that fail should:

1. **Not block merge**: Do not prevent PR from being merged
2. **Be visible**: Show warning in PR status
3. **Be logged**: Record for metrics and improvement
4. **Trigger notification**: Alert team for awareness

Decision matrix for optional check failures:

| Check Type | Failure Impact | Recommended Action |
|------------|---------------|-------------------|
| Lint warnings | Low | Merge, create follow-up issue |
| Coverage decrease | Medium | Review, decide per case |
| Performance regression | Medium | Review, benchmark manually |
| Documentation | Low | Merge, update docs separately |
| Integration tests | High | Block merge despite optional |

---

## 3. Check Run vs Check Suite

### 3.1 Difference Between Check Runs and Check Suites

**Check Suite**:
- Container for multiple check runs
- Created per CI app per commit
- Has aggregate status
- One per GitHub App per commit SHA

**Check Run**:
- Individual job or test result
- Belongs to exactly one check suite
- Has detailed output and annotations
- Multiple per check suite

Hierarchy:
```
Commit SHA
└── Check Suite (GitHub Actions)
    ├── Check Run: build
    ├── Check Run: test
    └── Check Run: lint
└── Check Suite (CircleCI)
    ├── Check Run: build-and-test
    └── Check Run: deploy-preview
```

### 3.2 When to Query Which API Endpoint

**Use Check Runs API when you need**:
- Individual job details
- Specific check output/annotations
- Re-run a specific job
- Check logs URL

```bash
# Get check runs for a commit
gh api repos/OWNER/REPO/commits/SHA/check-runs

# Get specific check run
gh api repos/OWNER/REPO/check-runs/CHECK_RUN_ID
```

**Use Check Suites API when you need**:
- Aggregate status for an app
- Re-run all checks from an app
- List all apps running checks

```bash
# Get check suites for a commit
gh api repos/OWNER/REPO/commits/SHA/check-suites

# Re-run a check suite
gh api repos/OWNER/REPO/check-suites/SUITE_ID/rerequest -X POST
```

**Use PR Checks via gh CLI for simplicity**:
```bash
# Combines check runs and commit statuses
gh pr checks PR_NUMBER --json name,status,conclusion
```

### 3.3 Aggregating Results from Multiple Providers

When aggregating results from multiple CI providers:

1. **Collect all check runs**:
   ```bash
   gh api repos/OWNER/REPO/commits/SHA/check-runs --jq '.check_runs[]'
   ```

2. **Collect legacy status checks** (older integrations):
   ```bash
   gh api repos/OWNER/REPO/commits/SHA/statuses --jq '.[]'
   ```

3. **Combine and deduplicate**:
   - Match by context/name
   - Take most recent status
   - Prefer check runs over legacy statuses

4. **Calculate aggregate status**:
   ```python
   def aggregate_status(checks):
       if any(c['conclusion'] == 'failure' for c in checks):
           return 'failure'
       if any(c['status'] == 'in_progress' for c in checks):
           return 'pending'
       if any(c['conclusion'] in ['cancelled', 'timed_out'] for c in checks):
           return 'error'
       if all(c['conclusion'] == 'success' for c in checks):
           return 'success'
       return 'mixed'
   ```

---

## 4. Common CI Providers

### 4.1 GitHub Actions Check Naming Conventions

GitHub Actions creates check runs with this naming pattern:

```
{workflow_name} / {job_name}
```

Examples:
- `CI / build`
- `CI / test (ubuntu-latest)`
- `Release / publish`

Matrix jobs include matrix values:
- `CI / test (ubuntu-latest, 3.9)`
- `CI / test (windows-latest, 3.11)`

**Matching in branch protection**:
- Use exact name: `CI / build`
- Wildcards not supported in GitHub UI
- API allows pattern matching

### 4.2 CircleCI Integration Patterns

CircleCI creates check runs named after workflow jobs:

```
ci/circleci: {job_name}
```

Examples:
- `ci/circleci: build`
- `ci/circleci: test`
- `ci/circleci: deploy`

**Key differences from GitHub Actions**:
- Prefix `ci/circleci:` always present
- No workflow name in check name
- Approval jobs show as `action_required`

### 4.3 Jenkins GitHub Plugin Behavior

Jenkins with GitHub plugin creates status checks:

```
continuous-integration/jenkins/{job_type}
```

Examples:
- `continuous-integration/jenkins/branch`
- `continuous-integration/jenkins/pr-merge`

**Note**: Jenkins uses legacy Status API by default, not Checks API. Check if the plugin version supports Checks API.

### 4.4 Third-Party Status Checks

Common third-party check patterns:

| Provider | Check Name Pattern |
|----------|-------------------|
| Travis CI | `continuous-integration/travis-ci/pr` |
| Codecov | `codecov/project`, `codecov/patch` |
| SonarCloud | `SonarCloud Code Analysis` |
| Vercel | `Vercel`, `Vercel - {project}` |
| Netlify | `netlify/{site}/deploy-preview` |
| AWS CodeBuild | `CodeBuild:{project}` |

**Identifying check provider**:
```bash
# Check the app that created the check run
gh api repos/OWNER/REPO/commits/SHA/check-runs \
  --jq '.check_runs[] | {name, app: .app.name}'
```
