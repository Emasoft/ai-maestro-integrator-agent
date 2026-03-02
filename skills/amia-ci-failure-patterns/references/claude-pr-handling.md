# Claude Code Action PR Handling Workflow

## Table of Contents

- [Overview](#overview)
- [When to Use This Workflow](#when-to-use-this-workflow)
- [Claude Code Action Integration](#claude-code-action-integration)
  - [GitHub Actions Workflow Setup](#github-actions-workflow-setup)
  - [Step 1: Detect PRs Needing Review](#step-1-detect-prs-needing-review)
  - [Step 2: Collect Previous Claude Feedback](#step-2-collect-previous-claude-feedback)
  - [Step 3: Request Claude Review via @claude Mention](#step-3-request-claude-review-via-claude-mention)
  - [Step 4: Monitor Claude's Response](#step-4-monitor-claudes-response)
- [Integration with Monitoring Cycle](#integration-with-monitoring-cycle)
  - [Autonomous Monitoring Loop](#autonomous-monitoring-loop)
  - [ActionRequired Classification](#actionrequired-classification)
- [Response Patterns for Claude](#response-patterns-for-claude)
  - [Pattern 1: Simple Fix Request](#pattern-1-simple-fix-request)
  - [Pattern 2: Multiple Issues](#pattern-2-multiple-issues)
  - [Pattern 3: CI Failure Analysis](#pattern-3-ci-failure-analysis)
  - [Pattern 4: Code Review Request](#pattern-4-code-review-request)
- [Complete Workflow Example](#complete-workflow-example)
- [Troubleshooting](#troubleshooting)
  - [Claude Not Responding to Mentions](#claude-not-responding-to-mentions)
  - [Workflow Not Triggering](#workflow-not-triggering)
  - [Claude Provides Incomplete Review](#claude-provides-incomplete-review)
- [Best Practices](#best-practices)

## Overview

This document describes how to handle Pull Requests using Claude Code Action (`anthropics/claude-code-action@v1`). Claude Code Action is a GitHub Action that provides AI-powered code review, implementation, and PR management capabilities.

## When to Use This Workflow

Use this workflow when:
- A PR needs automated code review
- A PR has `CHANGES_REQUESTED` status and needs guidance
- Multiple review bots have provided feedback that needs synthesis
- You want to automate PR feedback and improvement cycles

## Claude Code Action Integration

### GitHub Actions Workflow Setup

Create a workflow file at `.github/workflows/claude-pr-review.yml`:

```yaml
name: Claude PR Review

on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
  pull_request_review:
    types: [submitted]
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

concurrency:
  group: claude-pr-${{ github.event.pull_request.number || github.event.issue.number }}
  cancel-in-progress: false

jobs:
  review:
    if: |
      (github.event_name == 'pull_request') ||
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude'))
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write

    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          track_progress: true
          prompt: |
            REPO: ${{ github.repository }}
            PR_NUMBER: ${{ github.event.pull_request.number || github.event.issue.number }}

            Review this PR and provide comprehensive feedback.
          claude_args: |
            --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Read,Glob,Grep"
```

### Step 1: Detect PRs Needing Review

Identify PRs that need Claude's attention:

```bash
# List all open PRs needing review
gh pr list --state open --json number,title,reviewDecision --jq '.[] | select(.reviewDecision != "APPROVED") | "\(.number)\t\(.title)"'

# Check specific PR status
gh pr view {number} --json reviewDecision --jq '.reviewDecision'
# Possible values: APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, null
```

### Step 2: Collect Previous Claude Feedback

When `CHANGES_REQUESTED`, gather previous Claude Code Action feedback:

```bash
#!/bin/bash
# Collect previous Claude Code Action feedback for synthesis

number=$1
output=""

# Get previous Claude reviews (from previous claude-code-action runs)
claude=$(gh pr view "$number" --json comments --jq '.comments[] | select(.author.login | test("github-actions")) | select(.body | contains("Claude")) | .body')
if [ -n "$claude" ]; then
    output+="## Previous Claude Feedback\n$claude\n\n"
fi

# Get inline review comments from Claude
inline_comments=$(gh api "repos/{owner}/{repo}/pulls/$number/comments" --jq '.[] | select(.user.login | test("github-actions")) | "\(.path):\(.line): \(.body)"')
if [ -n "$inline_comments" ]; then
    output+="## Inline Comments\n$inline_comments\n\n"
fi

echo -e "$output"
```

### Step 3: Request Claude Review via @claude Mention

To request Claude's review on a specific PR:

```bash
#!/bin/bash
# Request Claude review on a PR

number=$1
context=$2

# Post comment with @claude mention (triggers claude-mention.yml workflow)
gh pr comment "$number" --body "@claude Please review this PR with focus on:
$context

Provide inline comments for specific issues and a summary comment with overall assessment."
```

### Step 4: Monitor Claude's Response

Claude Code Action will:
1. Create a tracking comment showing progress
2. Post inline comments on specific code issues
3. Post a summary comment with overall assessment
4. Update the tracking comment when complete

```bash
# Check for Claude's response
gh pr view "$number" --json comments --jq '.comments[] | select(.body | contains("Claude Code")) | .body'
```

## Integration with Monitoring Cycle

### Autonomous Monitoring Loop

```bash
#!/bin/bash
# Integrated monitoring cycle with Claude Code Action

POLL_INTERVAL=120  # 2 minutes

while true; do
    echo "=== PR Monitoring Cycle $(date) ==="

    # Get all open PRs
    prs=$(gh pr list --state open --json number,reviewDecision)

    # Process each PR
    echo "$prs" | jq -c '.[]' | while read -r pr; do
        number=$(echo "$pr" | jq -r '.number')
        review=$(echo "$pr" | jq -r '.reviewDecision')

        # Handle CHANGES_REQUESTED PRs
        if [ "$review" = "CHANGES_REQUESTED" ]; then
            echo "PR #$number: Changes requested, requesting Claude synthesis"

            # 1. Collect feedback from all review bots
            feedback=$(collect_review_feedback "$number")

            # 2. Request Claude to synthesize and provide guidance
            gh pr comment "$number" --body "@claude Please analyze the following review feedback and provide clear, actionable guidance:

$feedback

Summarize the key issues and provide specific fixes for each."

            echo "PR #$number: Requested Claude synthesis"
        fi
    done

    sleep "$POLL_INTERVAL"
done
```

### ActionRequired Classification

PRs with `CHANGES_REQUESTED` should be added to the `ActionRequired` queue:

```bash
# Find PRs needing Claude's attention
action_required=()

for pr in $(gh pr list --state open --json number,reviewDecision -q '.[] | select(.reviewDecision == "CHANGES_REQUESTED") | .number'); do
    action_required+=("$pr")
done

echo "PRs requiring Claude action: ${action_required[*]}"
```

## Response Patterns for Claude

### Pattern 1: Simple Fix Request

```markdown
@claude Please fix the type error on line 42 of `src/handler.ts`:
- Expected type: `string`
- Received type: `number`

Provide the exact code change needed.
```

### Pattern 2: Multiple Issues

```markdown
@claude Please address the following issues:

1. **Type Error** (`src/handler.ts:42`)
   - Fix: Convert number to string

2. **Missing Test** (`tests/handler.test.ts`)
   - Add test case for empty input scenario

3. **Documentation** (`README.md`)
   - Update usage section with new parameter

Use inline comments for each issue location.
```

### Pattern 3: CI Failure Analysis

```markdown
@claude CI is failing with the following error:

```
Error: ModuleNotFoundError: No module named 'utils'
```

Please:
1. Identify the root cause
2. Provide the fix with exact file and line changes
3. Explain why this error occurred
```

### Pattern 4: Code Review Request

```markdown
@claude Please review this PR focusing on:
- Security implications (input validation, authentication)
- Performance considerations (algorithm complexity, caching)
- Code quality (naming, structure, error handling)

Provide inline comments for specific issues and a summary with overall assessment.
```

## Complete Workflow Example

```bash
#!/bin/bash
# Complete Claude Code Action PR handling workflow

handle_pr_with_claude() {
    local number="$1"

    echo "Processing PR #$number..."

    # Step 1: Check review status
    review_decision=$(gh pr view "$number" --json reviewDecision --jq '.reviewDecision')

    case "$review_decision" in
        "APPROVED")
            echo "PR #$number is approved, checking CI status..."
            ci_status=$(gh pr view "$number" --json statusCheckRollup --jq '[.statusCheckRollup[].conclusion] | all(. == "SUCCESS")')
            if [ "$ci_status" = "true" ]; then
                echo "PR #$number: All checks pass, eligible for merge"
            fi
            ;;

        "CHANGES_REQUESTED")
            echo "PR #$number has changes requested, requesting Claude review..."

            # Collect previous Claude feedback
            previous_feedback=""

            # Previous Claude reviews
            claude_reviews=$(gh pr view "$number" --json comments --jq '[.comments[] | select(.author.login | test("github-actions")) | select(.body | contains("Claude")) | .body] | join("\n")')
            [ -n "$claude_reviews" ] && previous_feedback+="## Previous Claude Feedback\n$claude_reviews\n\n"

            # Request Claude to address issues
            request="@claude Please review and address all outstanding issues in this PR.

$previous_feedback

Provide:
1. Summary of key issues
2. Prioritized list of fixes
3. Inline comments on specific code locations"

            gh pr comment "$number" --body "$(echo -e "$request")"
            echo "PR #$number: Requested Claude review"
            ;;

        "REVIEW_REQUIRED"|"null")
            echo "PR #$number: Requesting initial Claude review"
            gh pr comment "$number" --body "@claude Please provide an initial code review for this PR."
            ;;
    esac
}

# Main: Process all PRs needing attention
for number in $(gh pr list --state open --json number,reviewDecision --jq '.[] | select(.reviewDecision != "APPROVED") | .number'); do
    handle_pr_with_claude "$number"
done
```

## Troubleshooting

### Claude Not Responding to Mentions

**Cause**: The `claude-mention.yml` workflow may not be configured or the mention syntax is incorrect.

**Solution**:
1. Verify `.github/workflows/claude-mention.yml` exists and is correct
2. Check workflow runs in the Actions tab
3. Ensure `ANTHROPIC_API_KEY` secret is set
4. Use the correct mention format: `@claude` (lowercase)

### Workflow Not Triggering

**Cause**: Permissions or workflow configuration issues.

**Solution**:
1. Check repository Actions settings
2. Verify `pull-requests: write` permission
3. Ensure workflow file is on the default branch
4. Check for workflow run errors in the Actions tab

### Claude Provides Incomplete Review

**Cause**: Context or prompt may be insufficient.

**Solution**: Provide more specific guidance:
```markdown
@claude Please review this PR with specific focus on:
- Files changed: `src/handler.ts`, `src/utils.ts`
- Check for: null handling, type safety, error boundaries
- Output: Inline comments for issues, summary with severity levels
```

## Best Practices

1. **Use inline comments** - Claude provides better feedback when using `mcp__github_inline_comment__create_inline_comment`
2. **Be specific** - Include file names, line numbers, and exact concerns in your requests
3. **Enable progress tracking** - Use `track_progress: true` to see Claude's work in progress
4. **Synthesize bot feedback** - Combine feedback from multiple review bots before requesting Claude synthesis
5. **Monitor workflow runs** - Check GitHub Actions for any errors or timeouts
6. **Set appropriate timeouts** - Long reviews may need extended timeout settings
