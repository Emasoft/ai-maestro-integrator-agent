# Bot Categories for PR Review

## Table of Contents

- [Overview](#overview)
- [Category Table](#category-table)
- [Detailed Category Definitions](#detailed-category-definitions)
  - [1. Claude Code Action (60-80% Reliability)](#1-claude-code-action-60-80-reliability)
  - [2. Human (Variable Reliability)](#2-human-variable-reliability)
- [Signal Interpretation Guide](#signal-interpretation-guide)
  - [Understanding Reliability Percentages](#understanding-reliability-percentages)
  - [Decision Matrix](#decision-matrix)
- [Priority Matrix](#priority-matrix)
- [Implementation Example](#implementation-example)
  - [Classifying PR Authors](#classifying-pr-authors)
  - [Handling PRs by Category](#handling-prs-by-category)
- [Claude Code Action Workflow Setup](#claude-code-action-workflow-setup)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
  - [Issue: Claude Code Action not responding](#issue-claude-code-action-not-responding)
  - [Issue: Claude provides incomplete review](#issue-claude-provides-incomplete-review)
  - [Issue: Misclassified reviewer](#issue-misclassified-reviewer)

## Overview

When monitoring Pull Requests in automated CI/CD pipelines, different types of PR authors require different handling strategies. This document defines the bot categories and their signal reliability for automated decision-making.

## Category Table

| Category | Identification | Signal Reliability | Response Strategy |
|----------|----------------|-------------------|-------------------|
| `claude-code-action` | `github-actions[bot]` with "Claude" in body, or `@claude` mentions | 60-80% | Verify before acting, synthesize feedback |
| `human` | All other authors | Variable | Process with priority, always address concerns |

## Detailed Category Definitions

### 1. Claude Code Action (60-80% Reliability)

**Definition**: Claude Code Action is a GitHub Action that provides AI-powered code review and implementation capabilities. It runs as `github-actions[bot]` and responds to `@claude` mentions.

**Identification**:
- Comments from `github-actions[bot]` containing "Claude Code"
- Inline review comments from `github-actions[bot]`
- Responses to `@claude` mentions

**Response Strategy**:
- Verify all suggestions before implementing
- Synthesize feedback before responding
- Use `@claude` mentions to trigger review and fixes
- Do not auto-merge without human approval

**Typical Actions**:
```bash
# Request Claude Code Action review
gh pr comment {number} --body "@claude Please review this PR focusing on:
- Security implications
- Performance considerations
- Code quality
- Test coverage

Provide inline comments for specific issues and a summary with overall assessment."

# Request specific fix
gh pr comment {number} --body "@claude Please fix the type error on line 42.
Expected type: string
Received type: number"
```

### 2. Human (Variable Reliability)

**Definition**: Any author not identified as Claude Code Action. Requires appropriate review and cannot be fully automated.

**Examples**:
- Individual developers
- External contributors
- Other bots (not Claude Code Action)

**Response Strategy**:
- Process with priority (P1)
- Always address questions and concerns
- Let humans resolve their own threads
- Requires human approval for all changes

## Signal Interpretation Guide

### Understanding Reliability Percentages

| Reliability | Meaning | Automation Level |
|-------------|---------|------------------|
| **60-80%** | Requires verification before acting | Semi-automated |
| **Variable** | Cannot be fully automated | Manual review required |

### Decision Matrix

| Author Category | CI Passes | CI Fails | Changes Requested |
|-----------------|-----------|----------|-------------------|
| `claude-code-action` | Verify suggestions | Synthesize & @claude | Evaluate & decide |
| `human` | Wait for approval | Notify human | Address concerns |

## Priority Matrix

| Priority | Source | Rationale |
|----------|--------|-----------|
| **P0** | Security-related comments (any source) | Security issues require immediate attention |
| **P1** | Human reviewers | Domain expertise, stakeholder requirements |
| **P2** | Claude Code Action | AI suggestions require verification |

## Implementation Example

### Classifying PR Authors

```bash
#!/bin/bash
# Classify a PR author/commenter into categories

classify_reviewer() {
    local author="$1"
    local comment_body="$2"

    # Check if it's Claude Code Action (runs as github-actions[bot])
    if [[ "$author" == "github-actions[bot]" ]] && [[ "$comment_body" == *"Claude"* ]]; then
        echo "claude-code-action"
    else
        echo "human"
    fi
}

# Usage
author=$(gh api repos/{owner}/{repo}/issues/comments/{comment_id} --jq '.user.login')
body=$(gh api repos/{owner}/{repo}/issues/comments/{comment_id} --jq '.body')
category=$(classify_reviewer "$author" "$body")
echo "Author '$author' classified as: $category"
```

### Handling PRs by Category

```bash
#!/bin/bash
# Handle PR based on author category

handle_pr_by_category() {
    local number="$1"
    local category="$2"

    case "$category" in
        claude-code-action)
            # Synthesize feedback and evaluate suggestions
            echo "Evaluating Claude Code Action feedback for PR #$number..."
            # Verify suggestions before implementing
            ;;
        human)
            # Process with priority, address concerns
            echo "PR #$number has human reviewer feedback - process with priority"
            ;;
    esac
}
```

## Claude Code Action Workflow Setup

To enable Claude Code Action in your repository:

1. Add `ANTHROPIC_API_KEY` secret to repository settings
2. Create `.github/workflows/claude-mention.yml`:

```yaml
name: Claude Mention Response
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          track_progress: true
```

## Best Practices

1. **Always verify Claude suggestions** - AI may miss context or make incorrect assumptions
2. **Process human feedback with priority** - Human reviewers have domain expertise
3. **Log all automated actions** - Maintain audit trail for debugging
4. **Security comments are always P0** - Regardless of source, security issues are critical
5. **Let humans resolve their own threads** - Do not auto-resolve human reviewer threads

## Troubleshooting

### Issue: Claude Code Action not responding

**Solution**: Verify the following:
1. The workflow `.github/workflows/claude-mention.yml` exists and is correct
2. Check workflow runs in the Actions tab for errors
3. Ensure `ANTHROPIC_API_KEY` secret is set in repository settings
4. Use the correct mention format: `@claude` (lowercase)

### Issue: Claude provides incomplete review

**Solution**: Provide more specific guidance in the @claude mention:
```bash
gh pr comment {number} --body "@claude Please review this PR with specific focus on:
- Files changed: src/handler.ts, src/utils.ts
- Check for: null handling, type safety, error boundaries
- Output: Inline comments for issues, summary with severity levels"
```

### Issue: Misclassified reviewer

**Solution**: The classify_reviewer function checks for `github-actions[bot]` with "Claude" in the comment body. If Claude Code Action is not being detected, verify:
1. The comment author is `github-actions[bot]`
2. The comment body contains "Claude" or "Claude Code"
