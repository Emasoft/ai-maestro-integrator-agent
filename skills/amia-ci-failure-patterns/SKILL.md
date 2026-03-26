---
name: amia-ci-failure-patterns
description: "Use when diagnosing CI/CD failures. Trigger with CI failure logs or pipeline errors."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  tags: "ci, cd, github-actions, debugging, cross-platform, devops"
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
4. If not, follow the decision tree in [detailed-guide](references/detailed-guide.md)
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

## Reference Documents

See `references/` directory for all reference documents. Full index in [detailed-guide](references/detailed-guide.md).

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See [detailed-guide](references/detailed-guide.md) for common error scenarios.

## Examples

### Cross-Platform Path Failure

```bash
# CI log shows: FileNotFoundError: /tmp/build/output.txt
python scripts/amia_diagnose_ci_failure.py --log-file ci.log
# Output: cross-platform temp path issue
# Fix: Use tempfile.gettempdir() instead of hardcoded /tmp
```

## Resources

See `references/` directory — 27 documents covering patterns, operations, and CI best practices.
