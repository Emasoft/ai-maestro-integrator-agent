---
procedure: proc-handle-failed-pr
workflow-instruction: "Step 22 - Handling Failed PRs"
operation: op-apply-pattern-fix
description: "Apply the recommended fix based on identified CI failure pattern"
---

# Operation: Apply Pattern Fix


## Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Read the Reference Document Section](#step-1-read-the-reference-document-section)
  - [Step 2: Understand the Fix](#step-2-understand-the-fix)
  - [Step 3: Apply the Fix by Category](#step-3-apply-the-fix-by-category)
  - [Step 4: Validate the Fix Syntax](#step-4-validate-the-fix-syntax)
  - [Step 5: Document the Change](#step-5-document-the-change)
- [Quick Fix Reference](#quick-fix-reference)
- [Output](#output)
- [Verification](#verification)
- [Error Handling](#error-handling)
  - [Fix causes new errors](#fix-causes-new-errors)
  - [Fix doesn't match the pattern](#fix-doesnt-match-the-pattern)
- [Next Operation](#next-operation)

## Purpose

This operation applies the recommended fix for a CI failure based on the identified pattern category.

## Prerequisites

- Pattern category identified (see [op-identify-failure-pattern.md](op-identify-failure-pattern.md))
- Reference document section identified
- Repository checkout with write access

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| category | string | Yes | Pattern category (cross-platform, exit-code, syntax, dependency, infrastructure, language-specific) |
| section | string | Yes | Specific section in reference document |
| affected_files | list | Yes | Files that need modification |

## Procedure

### Step 1: Read the Reference Document Section

Open the specific reference document and section:

```bash
# Read the full reference document
cat references/<category>-patterns.md

# Or search for specific section
grep -A 50 "## <section-number>" references/<category>-patterns.md
```

### Step 2: Understand the Fix

Each reference section contains:

1. **Problem Description** - What causes this failure
2. **Detection** - How to identify this pattern
3. **Solution** - Step-by-step fix instructions
4. **Code Examples** - Before/after code samples

### Step 3: Apply the Fix by Category

#### Cross-Platform Fixes

For temp path issues:

```python
# BEFORE (fails on Windows)
output_path = "/tmp/output.txt"

# AFTER (cross-platform)
import tempfile
output_path = os.path.join(tempfile.gettempdir(), "output.txt")
```

For path separator issues:

```python
# BEFORE (fails on Windows)
path = "src/utils/helper.py"

# AFTER (cross-platform)
import os
path = os.path.join("src", "utils", "helper.py")
```

#### Exit Code Fixes

For PowerShell exit code persistence:

```powershell
# BEFORE (exit code may be stale)
some_command
# script ends without explicit exit

# AFTER (explicit exit)
some_command
exit 0
```

For Bash exit code handling:

```bash
# BEFORE (last command exit code used)
failing_command || true
another_command

# AFTER (explicit exit)
failing_command || true
another_command
exit 0
```

#### Syntax Fixes

For heredoc terminators:

```yaml
# BEFORE (terminator has leading spaces)
run: |
  cat <<EOF
  content here
  EOF

# AFTER (terminator at column 0)
run: |
  cat <<'EOF'
  content here
  EOF
```

#### Dependency Fixes

For Python import issues:

```python
# BEFORE (relative import fails in CI)
from .utils import helper

# AFTER (absolute import)
from mypackage.utils import helper
```

#### Infrastructure Fixes

For missing labels:

```bash
# Create label before workflow runs
gh label create "ai-review" --color "0E8A16" --description "PR needs AI review"
```

### Step 4: Validate the Fix Syntax

After making changes, validate syntax:

```bash
# Python files
python3 -m py_compile modified_file.py

# JavaScript files
node --check modified_file.js

# YAML files
python3 -c "import yaml; yaml.safe_load(open('workflow.yml'))"

# Shell scripts
shellcheck modified_script.sh
```

### Step 5: Document the Change

Add a comment explaining the fix:

```python
# Fix for CI failure: Use tempfile.gettempdir() for cross-platform
# temp path compatibility (Windows uses %TEMP%, Linux/macOS use /tmp)
import tempfile
output_path = os.path.join(tempfile.gettempdir(), "output.txt")
```

## Quick Fix Reference

| Category | Common Issue | Quick Fix |
|----------|-------------|-----------|
| Cross-Platform | Hardcoded /tmp | `tempfile.gettempdir()` |
| Cross-Platform | Path separators | `os.path.join()` or `pathlib.Path` |
| Exit Code | Stale exit code | Add explicit `exit 0` |
| Syntax | Heredoc terminator | Ensure at column 0, no trailing spaces |
| Dependency | Relative imports | Use absolute imports |
| Infrastructure | Missing labels | Create via `gh label create` |

## Output

| Output | Type | Description |
|--------|------|-------------|
| modified_files | list | Files that were modified |
| changes_summary | string | Description of changes made |
| validation_status | boolean | Whether syntax validation passed |

## Verification

After applying fixes:

1. **Syntax Check**: Run language-specific linters
2. **Unit Tests**: Run affected unit tests locally
3. **Dry Run**: If possible, run the CI workflow locally

```bash
# For GitHub Actions, use act (if installed)
act -j build --dry-run
```

## Error Handling

### Fix causes new errors

If the fix introduces new issues:

1. Revert the change: `git checkout -- <file>`
2. Re-read the reference document for alternative approaches
3. Check if there are platform-specific variations

### Fix doesn't match the pattern

If the suggested fix doesn't apply:

1. Re-check the pattern classification
2. Read the full reference section, not just the quick fix
3. Consider if multiple patterns are involved

## Next Operation

After applying the fix:
- [op-verify-fix-locally.md](op-verify-fix-locally.md) - Verify the fix locally before pushing
