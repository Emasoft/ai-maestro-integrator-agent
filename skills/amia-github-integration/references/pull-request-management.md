# Pull Request Management

## Table of Contents

- [Use-Case TOC](#use-case-toc)
- [Creating Pull Requests](#creating-pull-requests)
  - [Basic PR Creation Syntax](#basic-pr-creation-syntax)
  - [Parameters](#parameters)
  - [Examples](#examples)
- [Linking PRs to Issues](#linking-prs-to-issues)
  - [Linking Keywords](#linking-keywords)
  - [Example PR Body with Multiple Issue Links](#example-pr-body-with-multiple-issue-links)
  - [Automatic PR Creation from Issues](#automatic-pr-creation-from-issues)
- [Monitoring PR Status](#monitoring-pr-status)
  - [Check Your PRs](#check-your-prs)
  - [View Detailed PR Information](#view-detailed-pr-information)
  - [Monitor CI/CD Checks](#monitor-cicd-checks)
- [Handling Failed Checks](#handling-failed-checks)
  - [View Failed Check Details](#view-failed-check-details)
  - [Common Failure Patterns](#common-failure-patterns)
  - [Re-running Checks](#re-running-checks)
  - [Manual Check Re-run](#manual-check-re-run)
- [Merging Pull Requests](#merging-pull-requests)
  - [Merge Strategies](#merge-strategies)
  - [Auto-merge](#auto-merge)
  - [Merge with Commit Message](#merge-with-commit-message)
- [PR Workflow Automation](#pr-workflow-automation)
  - [Automated PR Creation Script](#automated-pr-creation-script)
  - [Automated PR Merge Script](#automated-pr-merge-script)
- [Best Practices](#best-practices)

## Use-Case TOC
- When you need to create a pull request → [Creating Pull Requests](#creating-pull-requests)
- When you need to link PR to an issue → [Linking PRs to Issues](#linking-prs-to-issues)
- When you need to monitor PR status → [Monitoring PR Status](#monitoring-pr-status)
- When PR checks fail → [Handling Failed Checks](#handling-failed-checks)
- When you need to merge a PR → [Merging Pull Requests](#merging-pull-requests)
- When you need to automate PR workflow → [PR Workflow Automation](#pr-workflow-automation)

## Creating Pull Requests

Pull requests should be created automatically from agent tasks or manually when work is complete.

### Basic PR Creation Syntax

```bash
gh pr create \
  --title "Title of the pull request" \
  --body "Description and context" \
  --head "feature/branch-name" \
  --base "main" \
  --assignee "@username"
```

### Parameters

- `--title`: Short, descriptive title (required)
  - Should match or reference the issue title
  - Format: "Action + Object" (e.g., "Add OAuth authentication")

- `--body`: Detailed description (required)
  - Explain what changed and why
  - Include "Closes #123" to link to issue
  - List testing performed
  - Highlight breaking changes

- `--head`: Source branch (required)
  - Branch containing your changes
  - Convention: `feature/issue-123` or `bugfix/issue-456`

- `--base`: Target branch (default: "main")
  - Usually "main" or "develop"
  - For release branches: `--base "release/v1.2"`

- `--assignee`: Person responsible for the PR
  - Usually the PR author
  - Can assign multiple reviewers

- `--draft`: Create as draft PR
  - Use for work-in-progress
  - Prevents accidental merging
  - Allows early feedback

### Examples

**Example 1: Feature PR with Issue Linking**
```bash
gh pr create \
  --title "Add OAuth authentication for Google login" \
  --body "This PR implements OAuth 2.0 authentication.

**Changes:**
- Added OAuth controller and routes
- Implemented callback handler
- Added session management with Redis
- Updated user model to support OAuth

**Closes #42**

**Testing:**
- Manual testing completed with Google OAuth
- Unit tests: 15 new tests, all passing
- Integration tests: 3 new tests, all passing

**Breaking Changes:** None" \
  --head "feature/issue-42-oauth" \
  --base "main" \
  --assignee "@backend-dev"
```

**Example 2: Bug Fix PR**
```bash
gh pr create \
  --title "Fix null pointer exception in user profile" \
  --body "Fixes null pointer when user has no avatar.

**Root Cause:**
Avatar URL was not checked for null before rendering.

**Fix:**
Added null check and default avatar fallback.

**Fixes #89**

**Testing:**
- Verified fix with user without avatar
- Added regression test
- All existing tests passing" \
  --head "bugfix/issue-89-null-avatar" \
  --base "main"
```

**Example 3: Draft PR for Work in Progress**
```bash
gh pr create \
  --title "[WIP] Add OAuth authentication" \
  --body "Work in progress - OAuth authentication implementation.

**Completed:**
- OAuth controller structure
- Route definitions

**TODO:**
- Implement callback handler
- Add session management
- Write tests

**Related to #42** (will close when complete)" \
  --head "feature/issue-42-oauth" \
  --base "main" \
  --draft
```

## Linking PRs to Issues

GitHub automatically closes issues when PRs containing specific keywords are merged.

### Linking Keywords

Use these keywords in the PR body:
- `Closes #123` - Closes issue when PR merges
- `Fixes #123` - Closes issue when PR merges
- `Resolves #123` - Closes issue when PR merges
- `Related to #123` - Links but doesn't close

**Important:**
- Keywords are case-insensitive
- Must use exact keyword (not "Close", "Fix", "Resolve")
- Can link multiple issues in one PR

### Example PR Body with Multiple Issue Links

```
This PR implements the authentication system.

**Closes #42** (main feature)
**Closes #43** (session management)
**Fixes #44** (security vulnerability)
**Related to #38** (authentication epic)
```

### Automatic PR Creation from Issues

Create PR automatically with issue title and number:

```bash
ISSUE_NUM=42
ISSUE_TITLE=$(gh issue view $ISSUE_NUM --json title --jq '.title')

gh pr create \
  --title "$ISSUE_TITLE" \
  --body "Closes #$ISSUE_NUM" \
  --head "feature/issue-$ISSUE_NUM" \
  --base "main"
```

## Monitoring PR Status

Monitor pull request status throughout the review process.

### Check Your PRs

```bash
# List all your open PRs
gh pr list --author "@me"

# List PRs assigned to you for review
gh pr list --assignee "@me"

# View detailed PR status
gh pr status
```

**Example Output:**
```
Current branch
  #42  Add OAuth authentication [feature/issue-42-oauth]
   - Checks passing
   - Review required
   - 2 approvals received

Created by you
  #38  Fix navigation bug [bugfix/issue-38]
   - Checks failing
   - 1/3 checks failed
   - Review pending

Requesting a code review from you
  #35  Update dependencies [deps/update-react]
   - All checks passed
   - Awaiting your review
```

### View Detailed PR Information

```bash
gh pr view <pr_number> --json commits,reviewDecisions,statusCheckRollup
```

**Useful Fields:**
- `commits`: List of commits in the PR
- `reviewDecisions`: Review approvals/rejections
- `statusCheckRollup`: CI/CD check results

### Monitor CI/CD Checks

```bash
# View checks for specific PR
gh pr checks <pr_number>

# Watch checks in real-time (refreshes every 10s)
gh pr checks <pr_number> --watch
```

**Example Output:**
```
All checks were successful
✓ build                1m2s  https://github.com/...
✓ test                 2m15s https://github.com/...
✓ lint                 0m30s https://github.com/...
```

## Handling Failed Checks

When CI/CD checks fail, investigate and fix the issue.

### View Failed Check Details

```bash
# View check details
gh pr checks <pr_number>

# View check logs
gh run view <run_id> --log
```

### Common Failure Patterns

**Pattern 1: Test Failures**
```bash
# View failed tests
gh run view <run_id> --log | grep FAILED

# Re-run failed tests locally
npm test  # or pytest, cargo test, etc.
```

**Pattern 2: Lint Failures**
```bash
# Run linter locally
npm run lint  # or flake8, cargo clippy, etc.

# Auto-fix lint issues
npm run lint:fix
```

**Pattern 3: Build Failures**
```bash
# View build logs
gh run view <run_id> --log | grep ERROR

# Build locally to reproduce
npm run build
```

### Re-running Checks

After fixing issues, push changes to re-run checks:

```bash
git add .
git commit -m "Fix test failures"
git push
```

Checks will automatically re-run on push.

### Manual Check Re-run

Re-run specific checks without new commits:

```bash
gh run rerun <run_id>

# Re-run only failed checks
gh run rerun <run_id> --failed
```

## Merging Pull Requests

When all checks pass and reviews are approved, merge the PR.

### Merge Strategies

**1. Squash Merge (Recommended)**
```bash
gh pr merge <pr_number> --squash --delete-branch
```

**Benefits:**
- Creates single commit in history
- Cleaner history
- Easier to revert if needed

**2. Merge Commit**
```bash
gh pr merge <pr_number> --merge --delete-branch
```

**Benefits:**
- Preserves all commits
- Full history retained
- Useful for large features

**3. Rebase Merge**
```bash
gh pr merge <pr_number> --rebase --delete-branch
```

**Benefits:**
- Linear history
- No merge commits
- Cleanest history

### Auto-merge

Enable auto-merge to automatically merge when checks pass:

```bash
gh pr merge <pr_number> --auto --squash --delete-branch
```

PR will merge automatically when:
- All required checks pass
- All required reviews are approved
- No merge conflicts exist

### Merge with Commit Message

Customize the merge commit message:

```bash
gh pr merge <pr_number> \
  --squash \
  --delete-branch \
  --subject "Add OAuth authentication" \
  --body "Implements OAuth 2.0 for Google login. Closes #42"
```

## PR Workflow Automation

Automate the entire PR workflow from creation to merge.

### Automated PR Creation Script

```bash
#!/bin/bash
# auto-create-pr.sh - Create PR from current branch

BRANCH=$(git branch --show-current)
ISSUE_NUM=$(echo $BRANCH | grep -oP 'issue-\K\d+')

if [ -z "$ISSUE_NUM" ]; then
  echo "Error: Branch name must contain 'issue-N'"
  exit 1
fi

ISSUE_TITLE=$(gh issue view $ISSUE_NUM --json title --jq '.title')

gh pr create \
  --title "$ISSUE_TITLE" \
  --body "Closes #$ISSUE_NUM" \
  --head "$BRANCH" \
  --base "main" \
  --assignee "@me"
```

**Usage:**
```bash
git checkout -b feature/issue-42-oauth
# ... make changes ...
git commit -m "Implement OAuth"
git push -u origin feature/issue-42-oauth
./auto-create-pr.sh
```

### Automated PR Merge Script

```bash
#!/bin/bash
# auto-merge-pr.sh - Merge PR when ready

PR_NUM=$1

if [ -z "$PR_NUM" ]; then
  echo "Usage: ./auto-merge-pr.sh <pr_number>"
  exit 1
fi

# Check if PR is ready
CHECKS=$(gh pr checks $PR_NUM --json state --jq '.[].state' | grep -c "SUCCESS")
REVIEWS=$(gh pr view $PR_NUM --json reviewDecisions --jq '[.reviewDecisions[] | select(.state == "APPROVED")] | length')

if [ "$CHECKS" -ge 1 ] && [ "$REVIEWS" -ge 1 ]; then
  echo "PR is ready to merge"
  gh pr merge $PR_NUM --squash --delete-branch
else
  echo "PR not ready: $CHECKS checks passing, $REVIEWS approvals"
  gh pr merge $PR_NUM --auto --squash --delete-branch
  echo "Auto-merge enabled"
fi
```

**Usage:**
```bash
./auto-merge-pr.sh 42
```

## Best Practices

1. **Create PRs early** - Use draft PRs for work-in-progress
2. **Link to issues** - Always use "Closes #123" syntax
3. **Write clear descriptions** - Explain what, why, and how
4. **Keep PRs small** - Easier to review, faster to merge
5. **Respond to reviews promptly** - Address feedback quickly
6. **Squash merge** - Keep history clean and linear
7. **Delete branches** - Clean up after merge
8. **Monitor checks** - Fix failures immediately
