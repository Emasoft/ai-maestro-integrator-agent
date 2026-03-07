---
name: amia-github-pr-context
description: Use when retrieving PR context including metadata, diff, and changed files for code review planning. Trigger with /review-pr [PR_NUMBER].
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  category: github
  tags: "pull-request, code-review, diff-analysis, github-api"
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub PR Context Skill

## Overview

This skill provides tools to retrieve comprehensive context about GitHub Pull Requests. Use this skill when you need to:

- **Understand a PR before reviewing**: Get the full picture of what changed, why, and how
- **Plan task delegation**: Know which files changed to assign subagents appropriately
- **Analyze merge readiness**: Check mergeable status, conflicts, and CI state
- **Extract specific metadata**: Get author, branch names, labels, reviewers

## Output

Each script produces structured output for different PR analysis needs:

| Script | Output Format | Key Fields | Use Case |
|--------|---------------|------------|----------|
| `amia_get_pr_context.py` | JSON | `number`, `title`, `state`, `author`, `mergeable`, `files[]`, `labels[]`, `reviewers[]` | Complete PR overview for review planning |
| `amia_get_pr_files.py` | JSON array | `filename`, `status`, `additions`, `deletions`, `patch` (optional) | File-level change tracking |
| `amia_get_pr_diff.py` | Unified diff text or JSON stats | Diff hunks or `files_changed`, `insertions`, `deletions` | Code change inspection |

All JSON outputs are pretty-printed and can be piped to `jq` for filtering.

## Instructions

Follow these numbered steps to retrieve and analyze GitHub PR context:

1. **Verify prerequisites are met**
   - Run `gh auth status` to confirm GitHub CLI authentication
   - Run `python3 --version` to confirm Python 3.8+ is available
   - Ensure you have read access to the target repository

2. **Identify which information you need**
   - Need full PR overview? → Use `amia_get_pr_context.py`
   - Need only changed files list? → Use `amia_get_pr_files.py`
   - Need actual code diff? → Use `amia_get_pr_diff.py`

3. **Run the appropriate script with required parameters**
   - Always provide `--pr NUMBER` (the PR number)
   - Optionally provide `--repo OWNER/REPO` (defaults to current directory's repo)
   - For diffs, optionally add `--stat` for summary or `--files` for specific files

4. **Parse the output based on your task**
   - For JSON outputs: pipe to `jq` or parse in your code
   - For diff outputs: analyze unified diff format or statistics
   - Check exit codes (0 = success, 1-4 = various errors)

5. **Handle errors appropriately**
   - Exit code 1: Fix invalid parameters
   - Exit code 2: Verify PR number and repository
   - Exit code 3: Check network, retry if rate limited
   - Exit code 4: Re-authenticate with `gh auth login`

6. **Extract specific information as needed**
   - For metadata fields, see [references/pr-metadata.md](references/pr-metadata.md)
     <!-- TOC: pr-metadata.md -->
     - PR Metadata JSON Structure
     - 1 Core identification fields (number, title, state)
     - 2 Author and assignee information
     <!-- /TOC -->
   - For diff analysis, see [references/diff-analysis.md](references/diff-analysis.md)
     <!-- TOC: diff-analysis.md -->
     - Understanding Diff Output
     - 1 Unified diff format explanation
     - 2 File headers and hunks
     <!-- /TOC -->

### Checklist

Copy this checklist and track your progress:

- [ ] Verify GitHub CLI is authenticated (`gh auth status`)
- [ ] Verify Python 3.8+ is available
- [ ] Confirm read access to the target repository
- [ ] Identify which information is needed (context/files/diff)
- [ ] Run the appropriate script with `--pr NUMBER` parameter
- [ ] Parse the JSON or diff output
- [ ] Check exit codes and handle any errors
- [ ] Extract specific metadata or diff information as needed

### When to Use This Skill

| Scenario | Use This Skill |
|----------|----------------|
| Starting a code review | Yes - get full PR context first |
| Need to know which files changed | Yes - use file listing script |
| Want to see actual code changes | Yes - use diff retrieval script |
| Need PR metadata (author, labels) | Yes - use context script |
| Creating a new PR | No - use git workflow skill instead |
| Commenting on a PR | Partially - get context first, then use gh CLI directly |

### Decision Tree: Which Script to Use

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

## Prerequisites

1. **GitHub CLI (gh)** must be installed and authenticated
2. **Python 3.8+** available in PATH
3. **Repository access** - you must have read access to the repository

Verify prerequisites:
```bash
# Check gh is authenticated
gh auth status

# Check Python version
python3 --version
```

## Script Reference Table

| Script | Purpose | Key Arguments | Output |
|--------|---------|---------------|--------|
| `amia_get_pr_context.py` | Full PR metadata and status | `--pr NUMBER`, `--repo OWNER/REPO` | JSON with metadata, files, mergeable status |
| `amia_get_pr_files.py` | List changed files | `--pr NUMBER`, `--repo OWNER/REPO`, `--include-patch` | JSON array of files with status |
| `amia_get_pr_diff.py` | Get code diff | `--pr NUMBER`, `--repo OWNER/REPO`, `--stat`, `--files` | Diff text or JSON stats |

## Exit Codes (Standardized)

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

## Output Discipline

All scripts support the `--output-file <path>` flag:
- **With flag**: Full JSON written to file; concise summary printed to stderr
- **Without flag**: Full JSON printed to stdout (backward compatible)

When invoking from agents or automated workflows, always pass `--output-file` to minimize token consumption.

## Examples

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

## Reference Documents

### PR Metadata Reference

For detailed information about PR metadata fields and how to extract specific information, see:

**[references/pr-metadata.md](references/pr-metadata.md)**

Contents:
- 1. PR Metadata JSON Structure
  - 1.1 Core identification fields (number, title, state)
  - 1.2 Author and assignee information
  - 1.3 Branch and merge information
  - 1.4 Labels, milestones, and projects
  - 1.5 Review and approval status
- 2. Extracting Specific Fields
  - 2.1 Getting PR title and description
  - 2.2 Finding the source and target branches
  - 2.3 Checking mergeable status and conflicts
  - 2.4 Listing reviewers and their decisions
- 3. Common Metadata Queries
  - 3.1 Is this PR ready to merge?
  - 3.2 Who needs to approve this PR?
  - 3.3 What labels are applied?

### Diff Analysis Reference

For detailed information about interpreting PR diffs and analyzing changes, see:

**[references/diff-analysis.md](references/diff-analysis.md)**

Contents:
- 1. Understanding Diff Output
  - 1.1 Unified diff format explanation
  - 1.2 File headers and hunks
  - 1.3 Addition, deletion, and context lines
- 2. File-Level Analysis
  - 2.1 Identifying file types by extension
  - 2.2 Detecting rename and copy operations
  - 2.3 Binary file changes
- 3. Change Statistics
  - 3.1 Lines added vs deleted
  - 3.2 Files by change type (added, modified, deleted)
  - 3.3 Estimating review complexity
- 4. Filtering and Focusing
  - 4.1 Filtering by file path patterns
  - 4.2 Ignoring generated files
  - 4.3 Focusing on specific directories

## Integration with Integrator Agent

When delegating PR review tasks, use this skill to gather context first:

```
1. Get PR context with amia_get_pr_context.py
2. Analyze which files changed with amia_get_pr_files.py
3. Delegate file-specific reviews to subagents based on file types
4. Aggregate results and post review summary
```

## Error Handling

| Problem | Cause | Solution |
|---------|-------|----------|
| "gh: command not found" | GitHub CLI not installed | Install with `brew install gh` or see gh docs |
| "not logged into any GitHub hosts" | gh not authenticated | Run `gh auth login` |
| "Could not resolve to a PullRequest" | Wrong PR number or repo | Verify PR exists with `gh pr view NUMBER` |
| Rate limit errors | Too many API calls | Wait for rate limit reset or use `--retry` |
| Permission denied | No repo access | Verify you have read access to the repository |

For additional troubleshooting, run scripts with `--verbose` flag for detailed logging.

## Resources

- [references/pr-metadata.md](references/pr-metadata.md) - PR metadata JSON structure and field extraction
  <!-- TOC: pr-metadata.md -->
  - PR Metadata JSON Structure
  - 1 Core identification fields (number, title, state)
  - 2 Author and assignee information
  <!-- /TOC -->
- [references/diff-analysis.md](references/diff-analysis.md) - Understanding and analyzing PR diffs
  <!-- TOC: diff-analysis.md -->
  - Understanding Diff Output
  - 1 Unified diff format explanation
  - 2 File headers and hunks
  <!-- /TOC -->
