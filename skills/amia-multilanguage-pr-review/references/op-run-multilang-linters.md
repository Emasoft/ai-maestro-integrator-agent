---
name: op-run-multilang-linters
description: Execute linters for all detected languages and collect results
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Run Multilanguage Linters

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Output Structure](#output-structure)
- [Procedure](#procedure)
- [Command Examples](#command-examples)
  - [Python Linting](#python-linting)
  - [TypeScript/JavaScript Linting](#typescriptjavascript-linting)
  - [Rust Linting](#rust-linting)
  - [Go Linting](#go-linting)
  - [Shell Linting](#shell-linting)
- [Scope Linting to Changed Files](#scope-linting-to-changed-files)
- [Handling Linter Failures](#handling-linter-failures)
- [Aggregation Strategy](#aggregation-strategy)
- [Example Workflow](#example-workflow)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Execute the appropriate linters for each programming language detected in a PR. Collect and aggregate results from all linters for comprehensive code quality assessment.

## When to Use

- After detecting languages and getting linter commands
- As part of automated PR review pipeline
- When performing comprehensive code quality check

## Prerequisites

- Languages detected (op-detect-pr-languages)
- Linter commands retrieved (op-get-language-linters)
- Linters installed on the system
- Changed files accessible locally

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| Languages | Object | From op-detect-pr-languages |
| Linter commands | Object | From op-get-language-linters |
| Changed files | List | Files modified in the PR |
| Project root | Path | Root directory of the project |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `results` | Object | Linter results per language |
| `total_issues` | Integer | Total issues across all linters |
| `errors` | Integer | Count of error-level issues |
| `warnings` | Integer | Count of warning-level issues |
| `passed` | Boolean | True if no errors found |

## Output Structure

```json
{
  "results": {
    "python": {
      "ruff": {
        "exit_code": 1,
        "issues": 5,
        "output": "src/auth.py:10:1: E501 line too long..."
      },
      "mypy": {
        "exit_code": 0,
        "issues": 0,
        "output": "Success: no issues found"
      }
    },
    "typescript": {
      "eslint": {
        "exit_code": 1,
        "issues": 3,
        "output": "src/app.ts:5:1: error..."
      }
    }
  },
  "total_issues": 8,
  "errors": 5,
  "warnings": 3,
  "passed": false
}
```

## Procedure

1. **Checkout PR branch locally**

   ```bash
   gh pr checkout <PR_NUMBER>
   ```

2. **For each detected language, run its linters**

   ```bash
   # Python
   ruff check src/ tests/
   mypy --strict src/

   # TypeScript
   eslint src/

   # Bash
   shellcheck scripts/*.sh
   ```

3. **Collect exit codes and output**
   - Exit code 0 = pass
   - Exit code 1+ = issues found

4. **Aggregate results**
   - Count total issues
   - Categorize by severity
   - Determine overall pass/fail

5. **Format for review**

## Command Examples

### Python Linting

```bash
# Lint Python files
ruff check src/ tests/ --output-format=json > ruff_output.json

# Type check Python files
mypy --strict src/ --json-report mypy_output.json

# Security scan
bandit -r src/ -f json -o bandit_output.json
```

### TypeScript/JavaScript Linting

```bash
# Lint with ESLint
eslint src/ --format json > eslint_output.json

# Type check TypeScript
tsc --noEmit 2>&1 | tee tsc_output.txt
```

### Rust Linting

```bash
# Run Clippy
cargo clippy --all-targets --message-format=json > clippy_output.json

# Check formatting
cargo fmt --check
```

### Go Linting

```bash
# Static analysis
go vet ./... 2>&1 | tee govet_output.txt

# Advanced linting
staticcheck -f json ./... > staticcheck_output.json
```

### Shell Linting

```bash
# Lint shell scripts
shellcheck -f json scripts/*.sh > shellcheck_output.json
```

## Scope Linting to Changed Files

To lint only changed files (more efficient):

```bash
# Get list of changed Python files
CHANGED_PY=$(gh pr diff <PR_NUMBER> --name-only | grep '\.py$')

# Lint only changed files
ruff check $CHANGED_PY
```

## Handling Linter Failures

| Scenario | Action |
|----------|--------|
| Linter not found | Install using provided commands |
| Config file missing | Use default configuration |
| Too many errors | Consider using `--fix` flags first |
| Exit code non-zero | Capture output, continue with other linters |

## Aggregation Strategy

1. **Run ALL linters** even if some fail
2. **Capture output** from each linter
3. **Categorize issues** by severity (error/warning/info)
4. **Count totals** for summary
5. **Determine pass/fail** based on errors

## Example Workflow

```bash
# Full multilanguage linting workflow

# 1. Checkout PR
gh pr checkout 456

# 2. Get changed files by language
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 456

# 3. Run Python linters
ruff check src/ tests/
mypy --strict src/

# 4. Run TypeScript linters
eslint src/

# 5. Run Shell linters
shellcheck scripts/*.sh

# 6. Aggregate results
# (Collect exit codes and outputs)
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Linter crashes | Log error, continue with other linters |
| No files for language | Skip that language's linters |
| Timeout | Kill process, log partial results |

## Related Operations

- [op-detect-pr-languages.md](op-detect-pr-languages.md) - Detect languages
- [op-get-language-linters.md](op-get-language-linters.md) - Get linter commands
- [op-compile-multilang-review.md](op-compile-multilang-review.md) - Compile final review
