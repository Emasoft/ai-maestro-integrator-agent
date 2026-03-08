---
name: op-get-pr-context
description: Get full PR context including metadata, files, and status
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Get PR Context

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Run the Context Script](#step-1-run-the-context-script)
  - [Step 2: Parse the JSON Output](#step-2-parse-the-json-output)
  - [Step 3: Use Context for Review Planning](#step-3-use-context-for-review-planning)
- [Command Variants](#command-variants)
  - [Basic Context](#basic-context)
  - [Specific Repository](#specific-repository)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Context Fields Explained](#context-fields-explained)
  - [Mergeable Status](#mergeable-status)
  - [Review Decision](#review-decision)
  - [File Status](#file-status)
- [Example: Review Planning](#example-review-planning)
- [Extracting Specific Information](#extracting-specific-information)
  - [Get Just File Paths](#get-just-file-paths)
  - [Get Mergeable Status Only](#get-mergeable-status-only)
  - [Get Author](#get-author)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Retrieve comprehensive context about a Pull Request including metadata, changed files, mergeable status, and related information needed for review planning.

## When to Use

- At the start of any PR review
- When planning task delegation
- To understand PR scope and complexity
- Before making merge decisions

## Prerequisites

- GitHub CLI authenticated
- Access to repository
- PR exists

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| number | integer | PR number |
| title | string | PR title |
| body | string | PR description |
| state | string | open, closed, or merged |
| author | object | Author username and details |
| base_branch | string | Target branch |
| head_branch | string | Source branch |
| mergeable | string | MERGEABLE, CONFLICTING, or UNKNOWN |
| files | array | List of changed files |
| additions | integer | Total lines added |
| deletions | integer | Total lines deleted |
| labels | array | Applied labels |
| reviewers | array | Requested reviewers |
| review_decision | string | APPROVED, CHANGES_REQUESTED, etc. |

## Steps

### Step 1: Run the Context Script

```bash
python3 amia_get_pr_context.py --pr <NUMBER>
```

### Step 2: Parse the JSON Output

```json
{
  "number": 123,
  "title": "Add user authentication",
  "body": "This PR implements...",
  "state": "open",
  "author": {
    "login": "developer",
    "name": "Developer Name"
  },
  "base_branch": "main",
  "head_branch": "feature/auth",
  "mergeable": "MERGEABLE",
  "files_changed": 5,
  "additions": 250,
  "deletions": 30,
  "files": [
    {"path": "src/auth.py", "status": "added", "additions": 150, "deletions": 0},
    {"path": "src/user.py", "status": "modified", "additions": 50, "deletions": 20}
  ],
  "labels": ["enhancement", "ai-review"],
  "reviewers": ["reviewer1", "reviewer2"],
  "review_decision": "REVIEW_REQUIRED"
}
```

### Step 3: Use Context for Review Planning

Based on context:

- Assess scope (files changed, lines modified)
- Identify reviewers
- Check mergeable status
- Plan delegation based on file types

## Command Variants

### Basic Context

```bash
python3 amia_get_pr_context.py --pr 123
```

### Specific Repository

```bash
python3 amia_get_pr_context.py --pr 123 --repo owner/repo
```

## Alternative: Direct gh CLI

```bash
# Get comprehensive PR data
gh pr view 123 --json number,title,body,state,author,baseRefName,headRefName,mergeable,files,additions,deletions,labels,reviewRequests,reviewDecision
```

## Context Fields Explained

### Mergeable Status

| Value | Meaning | Action |
|-------|---------|--------|
| `MERGEABLE` | Can be merged cleanly | Proceed with review |
| `CONFLICTING` | Has merge conflicts | Author must resolve |
| `UNKNOWN` | Status being calculated | Wait and retry |

### Review Decision

| Value | Meaning |
|-------|---------|
| `APPROVED` | Has required approvals |
| `CHANGES_REQUESTED` | Changes requested by reviewer |
| `REVIEW_REQUIRED` | Awaiting review |

### File Status

| Value | Meaning |
|-------|---------|
| `added` | New file |
| `modified` | Existing file changed |
| `deleted` | File removed |
| `renamed` | File renamed (may also be modified) |
| `copied` | File copied from another |

## Example: Review Planning

```bash
# Get PR context
python3 amia_get_pr_context.py --pr 123

# Output analysis:
{
  "files_changed": 15,
  "additions": 500,
  "deletions": 100,
  "files": [
    {"path": "src/auth/login.py", ...},
    {"path": "src/auth/logout.py", ...},
    {"path": "src/db/user.py", ...},
    {"path": "tests/test_auth.py", ...}
  ]
}

# Planning:
# - 15 files = Medium PR (11-30 files)
# - Auth-focused: delegate security review
# - Has tests: verify test coverage
# - 500 additions: thorough review needed
```

## Extracting Specific Information

### Get Just File Paths

```bash
python3 amia_get_pr_context.py --pr 123 | jq -r '.files[].path'
```

### Get Mergeable Status Only

```bash
python3 amia_get_pr_context.py --pr 123 | jq -r '.mergeable'
```

### Get Author

```bash
python3 amia_get_pr_context.py --pr 123 | jq -r '.author.login'
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | PR not found |
| 3 | API error |
| 4 | Not authenticated |

## Error Handling

| Error | Action |
|-------|--------|
| PR not found | Verify PR number and repository |
| Access denied | Check repository permissions |
| Mergeable UNKNOWN | Wait briefly and retry |
| Large response | May need to paginate files |

## Related Operations

- [op-get-pr-files.md](op-get-pr-files.md) - Detailed file listing
- [op-get-pr-diff.md](op-get-pr-diff.md) - Actual code changes
- [op-analyze-pr-complexity.md](op-analyze-pr-complexity.md) - Complexity assessment
