# Operation: Push and Monitor

## Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Stage and Commit Changes](#step-1-stage-and-commit-changes)
  - [Step 2: Push to Remote](#step-2-push-to-remote)
  - [Step 3: Monitor the Workflow Run](#step-3-monitor-the-workflow-run)
  - [Step 4: Wait for Completion](#step-4-wait-for-completion)
  - [Step 5: Verify Success](#step-5-verify-success)
  - [Step 6: Handle Results](#step-6-handle-results)
- [Commit Message Template](#commit-message-template)
- [Output](#output)
- [Monitoring Checklist](#monitoring-checklist)
- [Error Handling](#error-handling)
  - [Push rejected](#push-rejected)
  - [Workflow not triggered](#workflow-not-triggered)
  - [Same failure persists](#same-failure-persists)
  - [Different failure occurs](#different-failure-occurs)
- [Next Operations](#next-operations)
- [Time Expectations](#time-expectations)

## Purpose

This operation pushes the CI fix to the remote repository and monitors the workflow run to confirm the fix resolved the failure.

## Prerequisites

- Fix verified locally (see [op-verify-fix-locally.md](op-verify-fix-locally.md))
- Git configured with push access
- GitHub CLI (`gh`) installed for monitoring

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| branch | string | Yes | Branch to push to |
| commit_message | string | Yes | Descriptive commit message |
| pr_number | integer | No | PR number if fixing an existing PR |

## Procedure

### Step 1: Stage and Commit Changes

```bash
# Review changes
git diff

# Stage modified files
git add <modified_files>

# Commit with descriptive message
git commit -m "fix(ci): resolve <pattern-category> issue in <component>

- Applied fix for <specific-issue>
- Reference: amia-ci-failure-patterns/<reference-doc>
- Closes #<issue-number> (if applicable)"
```

### Step 2: Push to Remote

```bash
# Push to the branch
git push origin <branch>

# If branch doesn't exist on remote
git push -u origin <branch>
```

### Step 3: Monitor the Workflow Run

**Using GitHub CLI:**

```bash
# Watch the workflow run in real-time
gh run watch

# List recent runs
gh run list --branch <branch> --limit 5

# Get specific run status
gh run view <run-id>
```

**Using GitHub Web Interface:**

1. Navigate to repository Actions tab
2. Find the triggered workflow run
3. Watch the progress in real-time

### Step 4: Wait for Completion

Set up notification for completion:

```bash
# Watch and wait for completion (blocks until done)
gh run watch --exit-status

# Or poll periodically
while true; do
  STATUS=$(gh run list --branch <branch> --limit 1 --json status -q '.[0].status')
  if [ "$STATUS" = "completed" ]; then
    echo "Workflow completed"
    break
  fi
  echo "Status: $STATUS - waiting..."
  sleep 30
done
```

### Step 5: Verify Success

Check the workflow result:

```bash
# Get conclusion of most recent run
gh run list --branch <branch> --limit 1 --json conclusion -q '.[0].conclusion'

# Should output: success
```

### Step 6: Handle Results

**If successful:**

```bash
# Verify all checks passed
gh pr checks <pr-number>

# Add comment if on a PR
gh pr comment <pr-number> --body "CI fix verified: <pattern-category> issue resolved."
```

**If failed again:**

```bash
# Download new logs
gh run view <run-id> --log-failed > ci-failed-attempt2.log

# Return to diagnosis
python3 scripts/amia_diagnose_ci_failure.py --log-file ci-failed-attempt2.log
```

## Commit Message Template

Use this template for CI fix commits:

```
fix(ci): <short description of fix>

Problem:
- <description of CI failure>
- <pattern category identified>

Solution:
- <what was changed>
- <why this fixes the issue>

Reference: amia-ci-failure-patterns/<reference-document>
Tested: <local verification summary>
```

## Output

| Output | Type | Description |
|--------|------|-------------|
| commit_sha | string | SHA of the fix commit |
| run_id | integer | GitHub Actions workflow run ID |
| conclusion | string | Workflow conclusion (success/failure) |
| run_url | string | URL to the workflow run |

## Monitoring Checklist

```markdown
- [ ] Changes committed with descriptive message
- [ ] Pushed to remote branch
- [ ] Workflow run triggered
- [ ] Watching run progress
- [ ] Run completed
- [ ] Conclusion is "success"
- [ ] All PR checks passing (if applicable)
```

## Error Handling

### Push rejected

If push is rejected:

```bash
# Fetch and rebase
git fetch origin
git rebase origin/<branch>

# Resolve conflicts if any
# Then push again
git push origin <branch>
```

### Workflow not triggered

If no workflow runs after push:

1. Check workflow file syntax: `act -n` or yaml lint
2. Verify workflow trigger conditions match your branch
3. Check if workflow is disabled in repository settings
4. Verify you pushed to the correct branch

### Same failure persists

If the same failure occurs:

1. Download new logs and compare with original
2. Check if fix was actually deployed (verify commit SHA in logs)
3. Look for additional instances of the same pattern
4. Consider if there are multiple root causes

### Different failure occurs

If a new, different failure occurs:

1. This is progress - the original issue is fixed
2. Start fresh with [op-collect-ci-logs.md](op-collect-ci-logs.md) for new failure
3. Document that original fix was successful

## Next Operations

Based on outcome:

| Outcome | Next Operation |
|---------|----------------|
| Success | Close issue/PR, document fix |
| Same failure | [op-collect-ci-logs.md](op-collect-ci-logs.md) - re-diagnose |
| New failure | [op-collect-ci-logs.md](op-collect-ci-logs.md) - diagnose new issue |

## Time Expectations

| Phase | Typical Duration |
|-------|------------------|
| Push | < 1 minute |
| Workflow queue | 0-5 minutes |
| Workflow execution | 2-30 minutes (depends on workflow) |
| Total | 5-35 minutes |

Set appropriate timeouts for monitoring scripts based on your workflow duration.
