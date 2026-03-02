---
procedure: proc-handle-failed-pr
workflow-instruction: "Step 22 - Handling Failed PRs"
operation: op-identify-failure-pattern
description: "Use decision tree to manually identify CI failure pattern category"
---

# Operation: Identify Failure Pattern


## Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Extract the Primary Error Message](#step-1-extract-the-primary-error-message)
  - [Step 2: Follow the Decision Tree](#step-2-follow-the-decision-tree)
  - [Step 3: Record the Classification](#step-3-record-the-classification)
  - [Step 4: Verify Classification](#step-4-verify-classification)
- [Decision Tree Quick Reference](#decision-tree-quick-reference)
- [Output](#output)
- [Example Classifications](#example-classifications)
  - [Example 1: Path Error](#example-1-path-error)
  - [Example 2: Exit Code Error](#example-2-exit-code-error)
  - [Example 3: Import Error](#example-3-import-error)
- [Error Handling](#error-handling)
  - [No category matches](#no-category-matches)
  - [Multiple categories could apply](#multiple-categories-could-apply)
- [Next Operation](#next-operation)

## Purpose

This operation uses the Diagnosis Decision Tree to manually classify a CI failure when the diagnostic script does not identify the pattern automatically.

## Prerequisites

- CI failure logs collected (see [op-collect-ci-logs.md](op-collect-ci-logs.md))
- Diagnostic script returned no patterns (see [op-run-diagnostic-script.md](op-run-diagnostic-script.md))

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| error_message | string | Yes | The primary error message from CI logs |
| log_context | string | Yes | Lines surrounding the error |

## Procedure

### Step 1: Extract the Primary Error Message

Find the first error in the log:

```bash
# Find GitHub Actions error annotations
grep "##\[error\]" ci.log | head -5

# Or find common error patterns
grep -i "error\|failed\|exception" ci.log | head -10
```

### Step 2: Follow the Decision Tree

Work through each question in order:

```
START: CI Failure Occurred
|
+---> Question 1: Does error mention path or file not found?
|     |
|     +---> YES: Category = Cross-Platform Patterns
|     |           Keywords: "not found", "no such file", "path", "directory"
|     |           Reference: cross-platform-patterns.md
|     |
|     +---> NO: Continue to Question 2
|
+---> Question 2: Does error show non-zero exit code?
|     |
|     +---> YES: Category = Exit Code Patterns
|     |           Keywords: "exit code", "returned 1", "failed with"
|     |           Reference: exit-code-patterns.md
|     |
|     +---> NO: Continue to Question 3
|
+---> Question 3: Does error mention syntax error or unexpected token?
|     |
|     +---> YES: Category = Syntax Patterns
|     |           Keywords: "syntax error", "unexpected", "unterminated"
|     |           Reference: syntax-patterns.md
|     |
|     +---> NO: Continue to Question 4
|
+---> Question 4: Does error mention import/require/module not found?
|     |
|     +---> YES: Category = Dependency Patterns
|     |           Keywords: "import", "require", "module", "package"
|     |           Reference: dependency-patterns.md
|     |
|     +---> NO: Continue to Question 5
|
+---> Question 5: Does error mention GitHub-specific resources?
|     |
|     +---> YES: Category = Infrastructure Patterns
|     |           Keywords: "label", "runner", "permission", "workflow"
|     |           Reference: github-infrastructure-patterns.md
|     |
|     +---> NO: Continue to Question 6
|
+---> Question 6: Check Language-Specific Patterns
      |
      Reference: language-specific-patterns.md
      Check section for the failing language (Python, JS, Rust, Go)
```

### Step 3: Record the Classification

Document your classification:

| Field | Value |
|-------|-------|
| Error Message | (copy the primary error) |
| Matching Question | (Question 1-6) |
| Category | (identified pattern category) |
| Keywords Found | (which keywords matched) |
| Reference | (reference document to read) |

### Step 4: Verify Classification

Cross-check by reading the reference document table of contents:

```bash
# View the reference document TOC
head -50 references/<category>-patterns.md
```

Confirm the error matches one of the documented patterns.

## Decision Tree Quick Reference

| Error Contains | Category | Reference |
|----------------|----------|-----------|
| "not found", "no such file", path issues | Cross-Platform | cross-platform-patterns.md |
| "exit code", "returned 1", "failed" | Exit Code | exit-code-patterns.md |
| "syntax error", "unexpected token" | Syntax | syntax-patterns.md |
| "import", "require", "module" | Dependency | dependency-patterns.md |
| "label", "runner", "permission" | Infrastructure | github-infrastructure-patterns.md |
| Language-specific keywords | Language-Specific | language-specific-patterns.md |

## Output

| Output | Type | Description |
|--------|------|-------------|
| category | string | Identified pattern category |
| reference | string | Path to reference document |
| keywords | list | Keywords that led to classification |
| confidence | string | Self-assessed confidence (high/medium/low) |

## Example Classifications

### Example 1: Path Error

```
Error: FileNotFoundError: [Errno 2] No such file or directory: '/tmp/build/output.txt'

Classification:
- Question 1: YES (mentions "not found" and path)
- Category: Cross-Platform
- Keywords: "No such file or directory", "/tmp/"
- Reference: cross-platform-patterns.md, Section 1.1 (Temp paths)
```

### Example 2: Exit Code Error

```
Error: Process completed with exit code 1.

Classification:
- Question 1: NO
- Question 2: YES (mentions exit code)
- Category: Exit Code
- Keywords: "exit code 1"
- Reference: exit-code-patterns.md, Section 2.1
```

### Example 3: Import Error

```
Error: ModuleNotFoundError: No module named 'mypackage.utils'

Classification:
- Question 1: NO (not a file path issue)
- Question 2: NO
- Question 3: NO
- Question 4: YES (module not found)
- Category: Dependency
- Keywords: "ModuleNotFoundError", "module"
- Reference: dependency-patterns.md, Section 4.1
```

## Error Handling

### No category matches

If none of the questions lead to a clear category:

1. Check if the error is environment-specific (runner config, secrets)
2. Search the error message in GitHub Issues
3. Check if it is a transient infrastructure failure (retry the workflow)

### Multiple categories could apply

Choose the category that matches the **root cause**, not the symptom:

- "File not found" during import = Dependency (root cause is import, not file)
- "Syntax error" in heredoc = Syntax (root cause is heredoc format)

## Next Operation

After identifying the pattern:
- [op-apply-pattern-fix.md](op-apply-pattern-fix.md) - Apply the recommended fix
