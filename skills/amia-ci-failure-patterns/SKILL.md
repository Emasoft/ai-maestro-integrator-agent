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

Systematically diagnose and fix CI/CD failures by recognizing common failure pattern categories and applying proven fixes. Use when workflows fail, tests pass locally but fail in CI, or platform-specific errors appear.

## Prerequisites

- Access to CI/CD logs from the failed pipeline
- `python3` available in PATH
- Repository access to view workflow files

## Instructions

1. Collect the CI failure log from the GitHub Actions workflow run
2. Run diagnostic: `python scripts/amia_diagnose_ci_failure.py --log-file ci.log`
3. If a pattern is identified, read the corresponding reference document for the fix
4. If not identified, follow the decision tree in `references/detailed-guide.md`
5. Apply the recommended fix to code or workflow configuration
6. Verify locally before pushing (when possible)
7. Push and monitor the CI run to confirm resolution

### Checklist

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

**Failure Pattern Categories:**

- `references/cross-platform-patterns.md` — OS-specific path, line ending, case sensitivity differences
- `references/exit-code-patterns.md` — Shell exit code handling and persistence
- `references/syntax-patterns.md` — Heredoc, quoting, command substitution issues
- `references/dependency-patterns.md` — Import paths, missing packages, version mismatches
- `references/github-infrastructure-patterns.md` — Runner labels, permissions, architecture
- `references/language-specific-patterns.md` — Python, JS/TS, Rust, Go CI peculiarities

**Automation & PR Handling:**

- `references/bot-categories.md` — PR author classification for automation
- `references/claude-pr-handling.md` — Claude Code Action PR workflow

**Debugging & Procedures:**

- `references/debug-procedures.md` — Systematic debugging workflow
- `references/detailed-guide.md` — Decision tree, quick reference table, error handling, examples

**CI Best Practices:**

- `references/ci-concurrency-groups.md` — Concurrency group configuration
- `references/ci-gate-job-pattern.md` — Gate job patterns
- `references/ci-job-summaries.md` — Job summary generation
- `references/ci-linting-workflow.md` — Linting workflow setup
- `references/ci-minimum-permissions.md` — Minimum permissions configuration
- `references/ci-optimized-matrix.md` — Optimized matrix builds
- `references/ci-path-filtered-triggers.md` — Path-filtered triggers
- `references/ci-pr-auto-labeling.md` — PR auto-labeling
- `references/ci-security-scanning.md` — Security scanning setup

**Operations:**

- `references/op-apply-pattern-fix.md` — Apply a pattern fix
- `references/op-classify-pr-author.md` — Classify PR author
- `references/op-collect-ci-logs.md` — Collect CI logs
- `references/op-detect-platform-issues.md` — Detect platform issues
- `references/op-identify-failure-pattern.md` — Identify failure pattern
- `references/op-push-and-monitor.md` — Push and monitor CI
- `references/op-run-diagnostic-script.md` — Run diagnostic script
- `references/op-verify-fix-locally.md` — Verify fix locally

## Examples

### Example 1: Cross-Platform Path Failure

```bash
# CI log shows: FileNotFoundError: /tmp/build/output.txt
python scripts/amia_diagnose_ci_failure.py --log-file ci.log
# Output: cross-platform temp path issue
# Fix: Use tempfile.gettempdir() instead of hardcoded /tmp
```
