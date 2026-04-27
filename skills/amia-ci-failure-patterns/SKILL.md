---
name: amia-ci-failure-patterns
description: "Use when diagnosing CI/CD failures. Trigger with CI failure logs or pipeline errors. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
tags: "ci, cd, github-actions, debugging, cross-platform, devops"
metadata:
  version: 1.0.0
  author: Emasoft
  platforms: "linux, macos, windows"
  languages: "python, javascript, typescript, rust, go, bash, powershell"
agent: debug-specialist
context: fork
user-invocable: false
---

# CI Failure Patterns Skill

## Overview

Diagnose and fix CI/CD failures by recognizing common failure patterns and applying proven fixes.

## Prerequisites

- CI/CD logs from the failed pipeline
- `python3` available in PATH
- Repository access to view workflow files

## Instructions

1. Collect the CI failure log from the GitHub Actions run
2. Run diagnostic: `python scripts/amia_diagnose_ci_failure.py --log-file ci.log`
3. If a pattern is identified, read the corresponding reference document for the fix
4. If not, follow the decision tree in the detailed guide (see Resources)
5. Apply the fix, verify locally, push and confirm CI passes

### Checklist

Copy this checklist and track your progress:

- [ ] Collect CI failure log
- [ ] Run diagnostic script on the log
- [ ] Identify failure pattern (script output or decision tree)
- [ ] Read corresponding reference document
- [ ] Apply recommended fix
- [ ] Verify fix locally
- [ ] Push and confirm CI passes

## Output

| Output Type | Description |
|-------------|-------------|
| Diagnostic report | JSON/text from `amia_diagnose_ci_failure.py` with patterns and fixes |
| Platform scan | JSON/text from `amia_detect_platform_issue.py` with platform issues |
| Fix recommendations | Step-by-step instructions from reference documents |

> **Output discipline:** All scripts support `--output-file <path>`.

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See the detailed guide in Resources for common error scenarios.

## Examples

### Cross-Platform Path Failure

```bash
# CI log shows: FileNotFoundError: /tmp/build/output.txt
python scripts/amia_diagnose_ci_failure.py --log-file ci.log
# Output: cross-platform temp path issue
# Fix: Use tempfile.gettempdir() instead of hardcoded /tmp
```

## Resources

See `references/` directory — 27 documents. Full guide: [detailed-guide](references/detailed-guide.md):
  - Failure Pattern Categories
  - Diagnosis Decision Tree
  - Quick Reference: Most Common Patterns
  - Diagnostic Scripts
    - amia_diagnose_ci_failure.py
    - amia_detect_platform_issue.py
  - Workflow: Diagnosing a CI Failure
  - Error Handling
    - The diagnostic script doesn't identify my failure
    - My fix works locally but still fails in CI
    - CI passes sometimes but fails randomly
  - Examples
    - Example 1: Diagnosing a Cross-Platform Path Failure
    - Example 2: Fixing a Heredoc Syntax Error
  - Reference Document TOCs
    - cross-platform-patterns.md
    - exit-code-patterns.md
    - syntax-patterns.md
    - dependency-patterns.md
    - github-infrastructure-patterns.md
    - language-specific-patterns.md
  - Full Reference Document Index
