# Operation: Get PR Files

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Run the Files Script](#step-1-run-the-files-script)
  - [Step 2: Parse the Output](#step-2-parse-the-output)
  - [Step 3: Analyze File Distribution](#step-3-analyze-file-distribution)
- [Command Variants](#command-variants)
  - [Basic File List](#basic-file-list)
  - [Include Patch Content](#include-patch-content)
  - [Specific Repository](#specific-repository)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [File Status Values](#file-status-values)
- [Analyzing File Distribution](#analyzing-file-distribution)
  - [By Directory](#by-directory)
  - [By File Type](#by-file-type)
  - [By Change Magnitude](#by-change-magnitude)
- [Example: Review Delegation](#example-review-delegation)
- [Example: With Patch Content](#example-with-patch-content)
- [Large PRs (>100 files)](#large-prs-100-files)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Retrieve the list of files changed in a Pull Request, including status (added/modified/deleted), line changes, and optionally the patch content.

## When to Use

- To understand the scope of changes
- To plan file-by-file review delegation
- To identify which areas of codebase are affected
- Before fetching full diff

## Prerequisites

- GitHub CLI authenticated
- Access to repository
- PR exists

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| repo | string | No | Repository in owner/repo format |
| include_patch | boolean | No | Include diff patch for each file |

## Output

Array of file objects:

| Field | Type | Description |
|-------|------|-------------|
| filename | string | Full path to file |
| status | string | added, modified, deleted, renamed, copied |
| additions | integer | Lines added |
| deletions | integer | Lines deleted |
| changes | integer | Total lines changed |
| patch | string | Diff patch (if requested) |
| previous_filename | string | For renamed files, original name |

## Steps

### Step 1: Run the Files Script

```bash
python3 amia_get_pr_files.py --pr <NUMBER>
```

### Step 2: Parse the Output

```json
[
  {
    "filename": "src/auth/login.py",
    "status": "modified",
    "additions": 25,
    "deletions": 10,
    "changes": 35
  },
  {
    "filename": "src/auth/logout.py",
    "status": "added",
    "additions": 50,
    "deletions": 0,
    "changes": 50
  },
  {
    "filename": "old_file.py",
    "status": "deleted",
    "additions": 0,
    "deletions": 100,
    "changes": 100
  }
]
```

### Step 3: Analyze File Distribution

Categorize files for review planning:

- By directory/module
- By file type
- By change magnitude

## Command Variants

### Basic File List

```bash
python3 amia_get_pr_files.py --pr 123
```

### Include Patch Content

```bash
python3 amia_get_pr_files.py --pr 123 --include-patch
```

### Specific Repository

```bash
python3 amia_get_pr_files.py --pr 123 --repo owner/repo
```

## Alternative: Direct gh CLI

```bash
# Get file list
gh pr view 123 --json files --jq '.files[]'

# Get files with details
gh pr diff 123 --name-only
```

## File Status Values

| Status | Description | Review Focus |
|--------|-------------|--------------|
| `added` | New file created | Review entirely |
| `modified` | Existing file changed | Review changes |
| `deleted` | File removed | Verify deletion is intentional |
| `renamed` | File moved/renamed | Check for modifications |
| `copied` | File duplicated | Review copy correctness |

## Analyzing File Distribution

### By Directory

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '.[].filename' | cut -d'/' -f1-2 | sort | uniq -c
```

Output:

```
  3 src/auth
  2 src/db
  5 tests/unit
```

### By File Type

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '.[].filename' | rev | cut -d'.' -f1 | rev | sort | uniq -c
```

Output:

```
  7 py
  2 md
  1 json
```

### By Change Magnitude

```bash
python3 amia_get_pr_files.py --pr 123 | jq '.[] | select(.changes > 50)'
```

## Example: Review Delegation

```bash
# Get files
python3 amia_get_pr_files.py --pr 123

# Output:
[
  {"filename": "src/auth/login.py", "status": "modified", "changes": 35},
  {"filename": "src/auth/oauth.py", "status": "added", "changes": 150},
  {"filename": "src/db/user.py", "status": "modified", "changes": 20},
  {"filename": "tests/test_auth.py", "status": "modified", "changes": 80}
]

# Delegation plan:
# - src/auth/* files -> Security reviewer
# - src/db/* files -> Database reviewer
# - tests/* files -> Test reviewer
```

## Example: With Patch Content

```bash
python3 amia_get_pr_files.py --pr 123 --include-patch

# Output (truncated):
[
  {
    "filename": "src/auth/login.py",
    "status": "modified",
    "additions": 25,
    "deletions": 10,
    "patch": "@@ -10,5 +10,20 @@\n def login(user, password):\n-    return check_password(user, password)\n+    validated = validate_input(user, password)\n+    if not validated:\n+        raise ValidationError()"
  }
]
```

## Large PRs (>100 files)

For very large PRs:

1. GitHub API paginates at 100 files
2. Script handles pagination automatically
3. Consider requesting PR be split if >100 files

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
| Too many files | Results are paginated automatically |
| Large patches | Use --no-patch for overview first |
| Binary files | Marked as binary, no patch available |

## Related Operations

- [op-get-pr-context.md](op-get-pr-context.md) - Full PR context
- [op-get-pr-diff.md](op-get-pr-diff.md) - Complete diff
- [op-analyze-pr-complexity.md](op-analyze-pr-complexity.md) - Complexity assessment
