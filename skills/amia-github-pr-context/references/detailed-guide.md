# GitHub PR Context Skill — Detailed Guide

## Table of Contents

- [When to Use This Skill](#when-to-use-this-skill)
- [Decision Tree: Which Script to Use](#decision-tree-which-script-to-use)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Integration with Integrator Agent](#integration-with-integrator-agent)
- [Detailed Examples](#detailed-examples)

## When to Use This Skill

| Scenario | Use This Skill |
|----------|----------------|
| Starting a code review | Yes - get full PR context first |
| Need to know which files changed | Yes - use file listing script |
| Want to see actual code changes | Yes - use diff retrieval script |
| Need PR metadata (author, labels) | Yes - use context script |
| Creating a new PR | No - use git workflow skill instead |
| Commenting on a PR | Partially - get context first, then use gh CLI directly |

## Decision Tree: Which Script to Use

```
Need PR information?
├── Need full context (metadata + files + status)?
│   └── Use: amia_get_pr_context.py
│
├── Need only the list of changed files?
│   └── Use: amia_get_pr_files.py
│
├── Need to see the actual code diff?
│   ├── Want summary statistics only?
│   │   └── Use: amia_get_pr_diff.py --stat
│   ├── Want diff for specific files?
│   │   └── Use: amia_get_pr_diff.py --files file1.py file2.py
│   └── Want full diff?
│       └── Use: amia_get_pr_diff.py
```

## Exit Codes

All scripts use standardized exit codes for consistent error handling:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Output is valid JSON/text |
| 1 | Invalid parameters | Bad PR number, missing required args |
| 2 | Resource not found | PR does not exist |
| 3 | API error | Network, rate limit, timeout |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | N/A for these scripts |
| 6 | Not mergeable | N/A for these scripts |

## Error Handling

| Problem | Cause | Solution |
|---------|-------|----------|
| "gh: command not found" | GitHub CLI not installed | Install with `brew install gh` or see gh docs |
| "not logged into any GitHub hosts" | gh not authenticated | Run `gh auth login` |
| "Could not resolve to a PullRequest" | Wrong PR number or repo | Verify PR exists with `gh pr view NUMBER` |
| Rate limit errors | Too many API calls | Wait for rate limit reset or use `--retry` |
| Permission denied | No repo access | Verify you have read access to the repository |

For additional troubleshooting, run scripts with `--verbose` flag for detailed logging.

## Integration with Integrator Agent

When delegating PR review tasks, use this skill to gather context first:

1. Get PR context with `amia_get_pr_context.py`
2. Analyze which files changed with `amia_get_pr_files.py`
3. Delegate file-specific reviews to subagents based on file types
4. Aggregate results and post review summary

## Detailed Examples

### Get Full PR Context

```bash
# Get context for PR #123 in current repo
python3 amia_get_pr_context.py --pr 123

# Get context for PR in specific repo
python3 amia_get_pr_context.py --pr 456 --repo owner/repo-name
```

### List Changed Files

```bash
# List files changed in PR #123
python3 amia_get_pr_files.py --pr 123

# Include patch/diff for each file
python3 amia_get_pr_files.py --pr 123 --include-patch
```

### Get Diff

```bash
# Get full diff
python3 amia_get_pr_diff.py --pr 123

# Get statistics summary only
python3 amia_get_pr_diff.py --pr 123 --stat

# Get diff for specific files only
python3 amia_get_pr_diff.py --pr 123 --files src/main.py tests/test_main.py
```

### Extracting Specific Information

After getting PR context, use `jq` to extract fields:

```bash
# Get PR title
python3 amia_get_pr_context.py --pr 123 | jq -r '.title'

# Check if mergeable
python3 amia_get_pr_context.py --pr 123 | jq -r '.mergeable'

# List reviewers
python3 amia_get_pr_context.py --pr 123 | jq -r '.reviewers[]'
```
