# CI Failure Patterns — Detailed Guide

## Table of Contents

- [Failure Pattern Categories](#failure-pattern-categories)
- [Diagnosis Decision Tree](#diagnosis-decision-tree)
- [Quick Reference: Most Common Patterns](#quick-reference-most-common-patterns)
- [Diagnostic Scripts](#diagnostic-scripts)
- [Workflow: Diagnosing a CI Failure](#workflow-diagnosing-a-ci-failure)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Reference Document TOCs](#reference-document-tocs)

## Failure Pattern Categories

CI failures fall into six main categories:

| Category | Description | Reference Document |
|----------|-------------|-------------------|
| Cross-Platform | OS differences causing failures | `cross-platform-patterns.md` |
| Exit Codes | Shell/script exit code handling | `exit-code-patterns.md` |
| Syntax | Shell syntax, heredocs, quoting | `syntax-patterns.md` |
| Dependencies | Import paths, missing packages | `dependency-patterns.md` |
| Infrastructure | GitHub runners, labels, permissions | `github-infrastructure-patterns.md` |
| Language-Specific | Python, JS, Rust, Go peculiarities | `language-specific-patterns.md` |
| Bot Categories | PR author classification for automation | `bot-categories.md` |
| Claude PR Handling | Workflow for Claude Code Action PRs | `claude-pr-handling.md` |

**Category contents overview:**

- **Cross-Platform**: Temporary Path Differences, Path Separator Differences, Line Ending Differences, Case Sensitivity Differences
- **Exit Codes**: Exit Code Persistence, Common Exit Codes by Tool, GitHub Actions Exit Code Handling
- **Syntax**: Here-String and Heredoc Terminator Issues, Shell Quoting Differences, Command Substitution Syntax
- **Dependencies**: Module Import Path Issues, Missing Dependencies in CI, Version Mismatches
- **Infrastructure**: Missing Labels, Platform Exceptions and Documentation, Runner Architecture
- **Language-Specific**: Python CI Patterns, JavaScript/TypeScript CI Patterns, Rust CI Patterns, Go CI Patterns
- **Bot Categories**: Overview, Category Table, Detailed Category Definitions, Signal Interpretation Guide, Priority Matrix, Implementation Example, Best Practices, Troubleshooting
- **Claude PR Handling**: Overview, When to Use This Workflow, Claude Code Action Integration, Integration with Monitoring Cycle, Response Patterns for Claude, Complete Workflow Example, Troubleshooting, Best Practices

## Diagnosis Decision Tree

Follow this decision tree to identify the failure category:

```
START: CI Failure Occurred
|
+---> Does error mention path or file not found?
|   +---> YES -> Check Cross-Platform Patterns (temp paths, separators, case sensitivity)
|   +---> NO  v
|
+---> Does error show non-zero exit code?
|   +---> YES -> Check Exit Code Patterns (persistence, tool-specific codes)
|   +---> NO  v
|
+---> Does error mention syntax error or unexpected token?
|   +---> YES -> Check Syntax Patterns (heredocs, quoting, line endings)
|   +---> NO  v
|
+---> Does error mention import/require/module not found?
|   +---> YES -> Check Dependency Patterns (import resolution, versions)
|   +---> NO  v
|
+---> Does error mention GitHub-specific resources (labels, runners)?
|   +---> YES -> Check Infrastructure Patterns (labels, permissions, runners)
|   +---> NO  v
|
+---> Check Language-Specific Patterns for the failing language
```

## Quick Reference: Most Common Patterns

| Pattern | Symptom | Quick Fix |
|---------|---------|-----------|
| Temp path differences | "File not found" on temp files | Use `tempfile.gettempdir()` (Python) or `os.tmpdir()` (JS) |
| Path separator | `\` fails on Linux | Use `path.join()` or normalize paths |
| Exit code persistence | PowerShell shows wrong exit code | Add explicit `exit 0` at script end |
| Heredoc terminator | "Unexpected end of file" | Ensure terminator at column 0, no trailing spaces |
| Missing labels | "Label X not found" | Create labels via API before workflow runs |
| Module import | "ModuleNotFoundError" | Check relative imports, PYTHONPATH, package structure |

## Diagnostic Scripts

### amia_diagnose_ci_failure.py

Analyzes CI failure logs to identify patterns and suggest fixes.

```bash
# Analyze a log file
python scripts/amia_diagnose_ci_failure.py --log-file /path/to/ci.log

# Analyze from stdin
cat ci.log | python scripts/amia_diagnose_ci_failure.py --stdin

# Output as JSON
python scripts/amia_diagnose_ci_failure.py --log-file ci.log --json
```

### amia_detect_platform_issue.py

Scans source code for platform-specific patterns that may cause CI failures.

```bash
# Scan a directory
python scripts/amia_detect_platform_issue.py --path /path/to/project

# Scan specific file types
python scripts/amia_detect_platform_issue.py --path . --extensions .py .js .sh

# Output as JSON
python scripts/amia_detect_platform_issue.py --path . --json
```

## Workflow: Diagnosing a CI Failure

1. **Collect the failure log** from the CI system
2. **Run the diagnostic script**: `python scripts/amia_diagnose_ci_failure.py --log-file ci.log`
3. **Follow the decision tree** if the script doesn't identify the pattern
4. **Read the appropriate reference document** for detailed fix instructions
5. **Apply the fix** following the documented pattern
6. **Verify locally** before pushing (where possible)
7. **Run CI again** to confirm the fix

## Error Handling

### The diagnostic script doesn't identify my failure

Read the full error message and search for keywords in the reference documents. Common keywords:

- "not found", "no such file" -> Cross-Platform Patterns
- "exit code", "returned 1" -> Exit Code Patterns
- "syntax error", "unexpected" -> Syntax Patterns
- "import", "module", "require" -> Dependency Patterns
- "permission", "label", "runner" -> Infrastructure Patterns

### My fix works locally but still fails in CI

This usually indicates a cross-platform issue. Check:

1. Are you testing on the same OS as CI?
2. Are file paths hardcoded?
3. Are environment variables the same?

### CI passes sometimes but fails randomly

Check for:

1. Race conditions in tests
2. External service dependencies
3. Time-sensitive tests
4. Resource exhaustion on shared runners

## Examples

### Example 1: Diagnosing a Cross-Platform Path Failure

```bash
# CI log shows: FileNotFoundError: /tmp/build/output.txt
# Run diagnostic script
python scripts/amia_diagnose_ci_failure.py --log-file ci.log

# Output identifies cross-platform temp path issue
# Fix: Use tempfile.gettempdir() instead of hardcoded /tmp
```

### Example 2: Fixing a Heredoc Syntax Error

```bash
# CI log shows: syntax error near unexpected token `newline`
# Cause: Heredoc EOF terminator has trailing whitespace
# Fix: Ensure EOF is at column 0 with no trailing spaces
```

## Reference Document TOCs

### cross-platform-patterns.md

- 1.1 Temporary Path Differences (Windows $env:TEMP, Linux/macOS /tmp/$TMPDIR, language-specific solutions)
- 1.2 Path Separator Differences (forward vs backslash, normalization, platform-agnostic construction)
- 1.3 Line Ending Differences (CRLF vs LF, git autocrlf, fixing in CI)
- 1.4 Case Sensitivity Differences (by platform, common failures, enforcing consistent casing)

### exit-code-patterns.md

- 2.1 Exit Code Persistence (PowerShell $LASTEXITCODE, Bash $?, reliable handling)
- 2.2 Common Exit Codes by Tool (git, npm/yarn/pnpm, pytest, cargo)
- 2.3 GitHub Actions Exit Code Handling (step failure detection, continue-on-error, custom handling)

### syntax-patterns.md

- 3.1 Here-String and Heredoc Terminator Issues (PowerShell "@ at column 0, Bash EOF, YAML multiline)
- 3.2 Shell Quoting Differences (Bash, POSIX sh, Zsh, PowerShell)
- 3.3 Command Substitution Syntax (backticks vs $(), nesting)

### dependency-patterns.md

- 4.1 Module Import Path Issues (relative paths, language-specific resolution, working directory)
- 4.2 Missing Dependencies in CI (lock files, optional deps, dev vs production)
- 4.3 Version Mismatches (pinned conflicts, transitive deps, CI-specific requirements)

### github-infrastructure-patterns.md

- 5.1 Missing Labels (creating before workflow, API format, naming conventions)
- 5.2 Platform Exceptions (runner OS differences, pre-installed software, env vars)
- 5.3 Runner Architecture (x64 vs ARM, self-hosted, resource limits)

### language-specific-patterns.md

- 6.1 Python CI Patterns (venv issues, pip failures, pytest config)
- 6.2 JavaScript/TypeScript CI Patterns (node_modules caching, package managers, ESM vs CJS)
- 6.3 Rust CI Patterns (cargo build, target directory, cross-compilation)
- 6.4 Go CI Patterns (module resolution, version mismatches, CGO deps)

## Full Reference Document Index

Content moved from SKILL.md for compactness:

**Failure Pattern Categories:**

- `cross-platform-patterns.md` — OS-specific path, line ending, case sensitivity differences
- `exit-code-patterns.md` — Shell exit code handling and persistence
- `syntax-patterns.md` — Heredoc, quoting, command substitution issues
- `dependency-patterns.md` — Import paths, missing packages, version mismatches
- `github-infrastructure-patterns.md` — Runner labels, permissions, architecture
- `language-specific-patterns.md` — Python, JS/TS, Rust, Go CI peculiarities

**Automation & PR Handling:**

- `bot-categories.md` — PR author classification for automation
- `claude-pr-handling.md` — Claude Code Action PR workflow

**Debugging & Procedures:**

- `debug-procedures.md` — Systematic debugging workflow

**CI Best Practices:**

- `ci-concurrency-groups.md` — Concurrency group configuration
- `ci-gate-job-pattern.md` — Gate job patterns
- `ci-job-summaries.md` — Job summary generation
- `ci-linting-workflow.md` — Linting workflow setup
- `ci-minimum-permissions.md` — Minimum permissions configuration
- `ci-optimized-matrix.md` — Optimized matrix builds
- `ci-path-filtered-triggers.md` — Path-filtered triggers
- `ci-pr-auto-labeling.md` — PR auto-labeling
- `ci-security-scanning.md` — Security scanning setup

**Operations:**

- `op-apply-pattern-fix.md` — Apply a pattern fix
- `op-classify-pr-author.md` — Classify PR author
- `op-collect-ci-logs.md` — Collect CI logs
- `op-detect-platform-issues.md` — Detect platform issues
- `op-identify-failure-pattern.md` — Identify failure pattern
- `op-push-and-monitor.md` — Push and monitor CI
- `op-run-diagnostic-script.md` — Run diagnostic script
- `op-verify-fix-locally.md` — Verify fix locally
