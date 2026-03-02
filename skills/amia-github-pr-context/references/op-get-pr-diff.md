---
name: op-get-pr-diff
description: Get the actual code diff for a PR
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Get PR Diff


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Run the Diff Script](#step-1-run-the-diff-script)
  - [Step 2: Review the Output](#step-2-review-the-output)
- [Command Variants](#command-variants)
  - [Full Diff](#full-diff)
  - [Statistics Only](#statistics-only)
  - [Specific Files](#specific-files)
  - [Combine with Other Tools](#combine-with-other-tools)
- [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
- [Understanding Unified Diff Format](#understanding-unified-diff-format)
  - [Hunk Header Explained](#hunk-header-explained)
- [Filtering Diff Output](#filtering-diff-output)
  - [Find Added Lines](#find-added-lines)
  - [Find Removed Lines](#find-removed-lines)
  - [Find Files with Specific Changes](#find-files-with-specific-changes)
- [Example: Security Review](#example-security-review)
- [Example: Test Coverage Check](#example-test-coverage-check)
- [Large Diffs](#large-diffs)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Retrieve the actual code changes (diff) for a Pull Request to review the specific modifications made.

## When to Use

- During code review to see actual changes
- To analyze what code was modified
- To understand the implementation details
- To find specific patterns or issues

## Prerequisites

- GitHub CLI authenticated
- Access to repository
- PR exists

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| repo | string | No | Repository in owner/repo format |
| stat | boolean | No | Return statistics instead of full diff |
| files | array | No | Limit diff to specific files |

## Output

**For full diff**: Unified diff text format
**For --stat**: JSON with statistics

```json
{
  "files_changed": 5,
  "insertions": 150,
  "deletions": 30,
  "files": [
    {"name": "src/auth.py", "insertions": 100, "deletions": 20},
    {"name": "src/user.py", "insertions": 50, "deletions": 10}
  ]
}
```

## Steps

### Step 1: Run the Diff Script

```bash
# Full diff
python3 amia_get_pr_diff.py --pr <NUMBER>

# Statistics only
python3 amia_get_pr_diff.py --pr <NUMBER> --stat

# Specific files
python3 amia_get_pr_diff.py --pr <NUMBER> --files src/auth.py tests/test_auth.py
```

### Step 2: Review the Output

For full diff, output is unified diff format:
```diff
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,5 +10,15 @@
 def login(user, password):
-    return check_password(user, password)
+    # Validate inputs first
+    if not user or not password:
+        raise ValidationError("Missing credentials")
+
+    # Check password with rate limiting
+    result = check_password(user, password)
+    log_attempt(user, result)
+    return result
```

## Command Variants

### Full Diff

```bash
python3 amia_get_pr_diff.py --pr 123
```

### Statistics Only

```bash
python3 amia_get_pr_diff.py --pr 123 --stat
```

### Specific Files

```bash
python3 amia_get_pr_diff.py --pr 123 --files src/auth.py src/user.py
```

### Combine with Other Tools

```bash
# Get diff and count additions/deletions
python3 amia_get_pr_diff.py --pr 123 | grep -c "^+"
python3 amia_get_pr_diff.py --pr 123 | grep -c "^-"
```

## Alternative: Direct gh CLI

```bash
# Full diff
gh pr diff 123

# Name only
gh pr diff 123 --name-only

# Statistics
gh pr diff 123 --stat
```

## Understanding Unified Diff Format

```diff
diff --git a/file.py b/file.py      # File being diffed
index abc123..def456 100644          # Git blob references
--- a/file.py                        # Original file marker
+++ b/file.py                        # Modified file marker
@@ -10,5 +10,15 @@                   # Hunk header (line numbers)
 context line                         # Unchanged context (space prefix)
-removed line                         # Deleted line (- prefix)
+added line                           # Added line (+ prefix)
```

### Hunk Header Explained

`@@ -10,5 +10,15 @@`
- `-10,5` = Original file: starts at line 10, shows 5 lines
- `+10,15` = Modified file: starts at line 10, shows 15 lines

## Filtering Diff Output

### Find Added Lines

```bash
python3 amia_get_pr_diff.py --pr 123 | grep "^+"
```

### Find Removed Lines

```bash
python3 amia_get_pr_diff.py --pr 123 | grep "^-"
```

### Find Files with Specific Changes

```bash
python3 amia_get_pr_diff.py --pr 123 | grep -B 5 "TODO"
```

## Example: Security Review

```bash
# Look for potential security issues in diff
python3 amia_get_pr_diff.py --pr 123 | grep -E "(password|secret|key|token|api_key)" -i

# Check for hardcoded values
python3 amia_get_pr_diff.py --pr 123 | grep -E "^\+.*=.*['\"][a-zA-Z0-9]{20,}['\"]"

# Find SQL queries
python3 amia_get_pr_diff.py --pr 123 | grep -E "(SELECT|INSERT|UPDATE|DELETE|DROP)" -i
```

## Example: Test Coverage Check

```bash
# Get diff for test files only
python3 amia_get_pr_diff.py --pr 123 --files $(gh pr view 123 --json files --jq '.files[].path | select(test("test"))')

# Count new test functions
python3 amia_get_pr_diff.py --pr 123 | grep -c "^\+.*def test_"
```

## Large Diffs

For large PRs:
- Use `--stat` first to understand scope
- Use `--files` to review section by section
- Consider requesting PR split if diff > 1000 lines

```bash
# Check size first
python3 amia_get_pr_diff.py --pr 123 --stat

# If large, review in sections
python3 amia_get_pr_diff.py --pr 123 --files src/auth/
python3 amia_get_pr_diff.py --pr 123 --files src/db/
python3 amia_get_pr_diff.py --pr 123 --files tests/
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
| Diff too large | Use --stat or --files to limit |
| Binary file in diff | Shown as "Binary files differ" |
| File not found | Verify file path in PR |

## Related Operations

- [op-get-pr-context.md](op-get-pr-context.md) - Full PR context
- [op-get-pr-files.md](op-get-pr-files.md) - File listing
- [diff-analysis.md](diff-analysis.md) - Detailed diff analysis guide
