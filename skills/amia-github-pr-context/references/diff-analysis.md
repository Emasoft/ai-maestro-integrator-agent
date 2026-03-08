# Diff Analysis Reference

This document explains how to retrieve, interpret, and analyze GitHub Pull Request diffs using the integrator-agent scripts.

## Table of Contents

- 1. Understanding Diff Output
  - 1.1 Unified diff format explanation
  - 1.2 File headers and hunks
  - 1.3 Addition, deletion, and context lines
- 1. File-Level Analysis
  - 2.1 Identifying file types by extension
  - 2.2 Detecting rename and copy operations
  - 2.3 Binary file changes
- 1. Change Statistics
  - 3.1 Lines added vs deleted
  - 3.2 Files by change type (added, modified, deleted)
  - 3.3 Estimating review complexity
- 1. Filtering and Focusing
  - 4.1 Filtering by file path patterns
  - 4.2 Ignoring generated files
  - 4.3 Focusing on specific directories

---

## 1. Understanding Diff Output

### 1.1 Unified Diff Format Explanation

The unified diff format is the standard output from `git diff` and GitHub's diff API. It shows changes in a compact, readable format.

**Basic Structure:**

```diff
diff --git a/path/to/file.py b/path/to/file.py
index abc1234..def5678 100644
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,8 @@ def existing_function():
     context line (unchanged)
     context line (unchanged)
-    old line (removed)
+    new line (added)
+    another new line (added)
     context line (unchanged)
```

**Line Prefixes:**

| Prefix | Meaning | Color (in terminals) |
|--------|---------|---------------------|
| ` ` (space) | Context line - unchanged | Default |
| `-` | Deletion - line removed | Red |
| `+` | Addition - line added | Green |
| `\` | No newline at end of file | Gray |

### 1.2 File Headers and Hunks

Each file in a diff has a header followed by one or more "hunks" (sections of changes).

**File Header Breakdown:**

```diff
diff --git a/src/auth.py b/src/auth.py
index abc1234..def5678 100644
--- a/src/auth.py
+++ b/src/auth.py
```

| Line | Description |
|------|-------------|
| `diff --git a/... b/...` | Identifies the file being compared |
| `index abc1234..def5678` | Git blob hashes (old..new) |
| `100644` | File mode (permissions) |
| `--- a/src/auth.py` | Original file path |
| `+++ b/src/auth.py` | New file path |

**Hunk Header Breakdown:**

```diff
@@ -10,7 +10,8 @@ def existing_function():
```

Format: `@@ -OLD_START,OLD_COUNT +NEW_START,NEW_COUNT @@ CONTEXT`

| Part | Meaning |
|------|---------|
| `-10,7` | In old file: starts at line 10, shows 7 lines |
| `+10,8` | In new file: starts at line 10, shows 8 lines |
| `def existing_function():` | Nearest function/class for context |

### 1.3 Addition, Deletion, and Context Lines

**Context Lines (space prefix):**

Context lines are unchanged lines shown for reference. By default, 3 lines of context are shown before and after each change.

```diff
     # This is an unchanged line (context)
     # Another unchanged line (context)
-    old_code()  # This line was removed
+    new_code()  # This line was added
     # More context after the change
```

**Understanding Multi-Line Changes:**

```diff
-def calculate(x, y):
-    return x + y
+def calculate(x: int, y: int) -> int:
+    """Add two integers."""
+    result = x + y
+    return result
```

This shows a function being rewritten:

- 2 lines removed (old implementation)
- 4 lines added (new implementation with type hints and docstring)

**Net Change Calculation:**

- Lines removed: count lines starting with `-`
- Lines added: count lines starting with `+`
- Net change: additions - deletions

---

## 2. File-Level Analysis

### 2.1 Identifying File Types by Extension

When analyzing a PR, categorizing files by type helps prioritize review effort.

**Using amia_get_pr_files.py:**

```bash
# Get all changed files with their extensions
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | "\(.filename) (\(.filename | split(".") | last))"'
```

**Common File Type Categories:**

| Category | Extensions | Review Priority |
|----------|------------|-----------------|
| Source Code | .py, .js, .ts, .go, .rs, .java, .cpp | High |
| Tests | _test.py, .test.js, .spec.ts | High |
| Configuration | .json, .yaml, .toml, .ini | Medium |
| Documentation | .md, .rst, .txt | Low |
| Generated | .lock, package-lock.json | Low (usually skip) |
| Build | Makefile, Dockerfile, .github/workflows/* | Medium |

**Group Files by Category:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  group_by(
    if .filename | test("\\.(py|js|ts|go|rs)$") then "source"
    elif .filename | test("test|spec") then "tests"
    elif .filename | test("\\.(json|yaml|toml)$") then "config"
    elif .filename | test("\\.(md|rst|txt)$") then "docs"
    else "other"
    end
  ) | .[] | "\(.[0] | if .filename | test("\\.(py|js|ts|go|rs)$") then "SOURCE" elif .filename | test("test|spec") then "TESTS" elif .filename | test("\\.(json|yaml|toml)$") then "CONFIG" elif .filename | test("\\.(md|rst|txt)$") then "DOCS" else "OTHER" end): \(map(.filename) | join(", "))"'
```

### 2.2 Detecting Rename and Copy Operations

GitHub tracks file renames and copies, which is important for understanding refactoring.

**File Status Values:**

| Status | Meaning |
|--------|---------|
| `added` | New file created |
| `modified` | Existing file changed |
| `deleted` | File removed |
| `renamed` | File moved/renamed (with optional changes) |
| `copied` | File duplicated (with optional changes) |

**Checking for Renames:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | select(.status == "renamed") |
  "\(.previous_filename) → \(.filename) (similarity: \(.similarity // "unknown")%)"'
```

**Example Output:**

```
src/old_name.py → src/new_name.py (similarity: 95%)
lib/utils.js → src/utils/helpers.js (similarity: 80%)
```

**Similarity Score:**

- 100%: Pure rename, no content changes
- 90-99%: Minor changes after rename
- Below 90%: Significant changes (might be better viewed as delete + add)

### 2.3 Binary File Changes

Binary files (images, compiled files, etc.) show differently in diffs.

**Identifying Binary Files:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | select(.binary == true) | .filename'
```

**Binary Diff Output Example:**

```diff
diff --git a/images/logo.png b/images/logo.png
Binary files a/images/logo.png and b/images/logo.png differ
```

**Size Change for Binary Files:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | select(.binary == true) |
  "\(.filename): \(.previous_size // 0) → \(.size) bytes"'
```

---

## 3. Change Statistics

### 3.1 Lines Added vs Deleted

Get a quick overview of change volume.

**Using amia_get_pr_diff.py with --stat:**

```bash
python3 amia_get_pr_diff.py --pr 123 --stat
```

**Example Output:**

```json
{
  "total_additions": 245,
  "total_deletions": 89,
  "files_changed": 12,
  "files": [
    {"filename": "src/auth.py", "additions": 120, "deletions": 45},
    {"filename": "tests/test_auth.py", "additions": 85, "deletions": 12},
    {"filename": "README.md", "additions": 40, "deletions": 32}
  ]
}
```

**Per-File Statistics:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | "\(.filename): +\(.additions) -\(.deletions)"' | sort -t: -k2 -rn
```

**Example Output (sorted by most changes):**

```
src/auth.py: +120 -45
tests/test_auth.py: +85 -12
README.md: +40 -32
config.json: +5 -2
```

### 3.2 Files by Change Type

Understand what types of changes are happening.

```bash
# Count files by status
python3 amia_get_pr_files.py --pr 123 | jq -r '
  group_by(.status) | .[] | "\(.[0].status): \(length) files"'
```

**Example Output:**

```
added: 3 files
modified: 8 files
deleted: 1 files
```

**List Each Category:**

```bash
# New files only
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | select(.status == "added") | .filename'

# Deleted files only
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | select(.status == "deleted") | .filename'
```

### 3.3 Estimating Review Complexity

Use heuristics to estimate how complex a PR is to review.

**Complexity Factors:**

| Factor | Weight | Why |
|--------|--------|-----|
| Total lines changed | High | More changes = more review time |
| Number of files | Medium | Context switching |
| New files added | Medium | Need to understand new architecture |
| Test coverage | Positive | Tests help verify correctness |
| Large single-file changes | High risk | Hard to review 500+ line changes |

**Complexity Score Script:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  {
    total_changes: (map(.additions + .deletions) | add),
    file_count: length,
    new_files: [.[] | select(.status == "added")] | length,
    large_files: [.[] | select(.additions + .deletions > 300)] | length,
    has_tests: any(.[]; .filename | test("test|spec"))
  } |
  "Complexity Score:
   - Total changes: \(.total_changes) lines
   - Files changed: \(.file_count)
   - New files: \(.new_files)
   - Large changes (>300 lines): \(.large_files)
   - Includes tests: \(.has_tests)

   Estimated review time: \(
     if .total_changes < 100 then "15-30 minutes (small)"
     elif .total_changes < 500 then "30-60 minutes (medium)"
     elif .total_changes < 1000 then "1-2 hours (large)"
     else "2+ hours (very large, consider splitting)"
     end
   )"'
```

---

## 4. Filtering and Focusing

### 4.1 Filtering by File Path Patterns

Focus on specific parts of the codebase.

**Using amia_get_pr_diff.py with --files:**

```bash
# Get diff for specific files only
python3 amia_get_pr_diff.py --pr 123 --files src/auth.py src/models/user.py

# Get diff for files matching a pattern (use shell expansion or jq filtering)
python3 amia_get_pr_files.py --pr 123 | jq -r '
  .[] | select(.filename | test("^src/")) | .filename' |
  xargs python3 amia_get_pr_diff.py --pr 123 --files
```

**Filter Files by Pattern:**

```bash
# Only Python files
python3 amia_get_pr_files.py --pr 123 | jq -r '
  [.[] | select(.filename | test("\\.py$"))] | .[] | .filename'

# Only files in src/ directory
python3 amia_get_pr_files.py --pr 123 | jq -r '
  [.[] | select(.filename | startswith("src/"))] | .[] | .filename'

# Exclude test files
python3 amia_get_pr_files.py --pr 123 | jq -r '
  [.[] | select(.filename | test("test|spec") | not)] | .[] | .filename'
```

### 4.2 Ignoring Generated Files

Generated files should usually be skipped during review.

**Common Generated File Patterns:**

| Pattern | Type |
|---------|------|
| `package-lock.json`, `yarn.lock` | JS package locks |
| `poetry.lock`, `Pipfile.lock` | Python package locks |
| `*.min.js`, `*.min.css` | Minified assets |
| `dist/`, `build/`, `out/` | Build outputs |
| `*.pb.go`, `*_pb2.py` | Protocol buffer generated |
| `*.generated.*` | Various generated files |
| `__pycache__/`, `*.pyc` | Python bytecode |

**Filter Out Generated Files:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  [.[] | select(
    (.filename | test("lock\\.json$|\\.lock$|node_modules|dist/|build/|\\.min\\.(js|css)$|__pycache__|_pb2\\.py$|\\.pb\\.go$")) | not
  )] | .[] | "\(.filename): +\(.additions) -\(.deletions)"'
```

### 4.3 Focusing on Specific Directories

When reviewing large PRs, focus on one area at a time.

**Group Files by Top-Level Directory:**

```bash
python3 amia_get_pr_files.py --pr 123 | jq -r '
  group_by(.filename | split("/")[0]) |
  .[] |
  {
    directory: .[0].filename | split("/")[0],
    file_count: length,
    additions: map(.additions) | add,
    deletions: map(.deletions) | add
  } |
  "\(.directory)/: \(.file_count) files (+\(.additions) -\(.deletions))"'
```

**Example Output:**

```
src/: 8 files (+180 -67)
tests/: 3 files (+95 -12)
docs/: 1 files (+40 -32)
```

**Get Diff for One Directory:**

```bash
# Get only src/ changes
FILES=$(python3 amia_get_pr_files.py --pr 123 | jq -r '
  [.[] | select(.filename | startswith("src/"))] | .[].filename')
python3 amia_get_pr_diff.py --pr 123 --files $FILES
```

**Review Order Recommendation:**

1. Start with configuration changes (understand context)
2. Review source code changes (main logic)
3. Review test changes (verify coverage)
4. Skim documentation changes (usually straightforward)
5. Skip generated/lock files (verify they match expected changes)
