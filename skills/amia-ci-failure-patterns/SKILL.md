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

This skill teaches you how to systematically diagnose and fix Continuous Integration (CI) failures. CI pipelines fail for predictable reasons that fall into identifiable pattern categories. By recognizing these patterns, you can quickly identify root causes and apply proven fixes.

## Prerequisites

Before using this skill, ensure:
1. Access to CI/CD logs from the failed pipeline
2. `python3` available in PATH for running diagnostic scripts
3. Repository access to view workflow files

## Instructions

Follow these steps to diagnose and fix CI failures:

1. Collect the CI failure log from the GitHub Actions workflow run
2. Run the diagnostic script: `python scripts/amia_diagnose_ci_failure.py --log-file ci.log`
3. If the script identifies a pattern, read the corresponding reference document for the fix
4. If the script doesn't identify the pattern, follow the Diagnosis Decision Tree to determine the failure category
5. Read the appropriate reference document for detailed diagnosis and fix instructions
6. Apply the recommended fix to your code or workflow configuration
7. Verify the fix locally (when possible) before pushing to CI
8. Push the changes and monitor the CI run to confirm the fix resolved the issue

### Checklist

Copy this checklist and track your progress:

- [ ] Collect CI failure log from GitHub Actions workflow run
- [ ] Run diagnostic script: `python scripts/amia_diagnose_ci_failure.py --log-file ci.log`
- [ ] Identify failure pattern (from script output or Decision Tree)
- [ ] Read the corresponding reference document for the identified pattern
- [ ] Apply the recommended fix to code or workflow configuration
- [ ] Verify the fix locally before pushing (if possible)
- [ ] Push changes to trigger new CI run
- [ ] Monitor CI run and confirm the fix resolved the issue

Use this skill when:
- A CI workflow fails and you need to diagnose the cause
- Tests pass locally but fail in CI
- You see platform-specific errors (Windows vs Linux vs macOS)
- Exit codes indicate failure but the error message is unclear
- Dependency installation fails in CI but works locally
- GitHub Actions infrastructure issues occur (labels, permissions, runners)

## Output

This skill produces the following outputs:

| Output Type | Description |
|-------------|-------------|
| Diagnostic report | JSON or text report from `amia_diagnose_ci_failure.py` identifying failure patterns and suggested fixes |
| Platform issue scan | JSON or text report from `amia_detect_platform_issue.py` listing platform-specific code patterns that may cause CI failures |
| Fix recommendations | Step-by-step instructions from reference documents for resolving identified failure patterns |
| Verification steps | Commands and procedures to verify fixes locally before pushing to CI |

## Failure Pattern Categories

CI failures fall into six main categories:

| Category | Description | Reference Document |
|----------|-------------|-------------------|
| Cross-Platform | OS differences causing failures | [cross-platform-patterns.md](references/cross-platform-patterns.md) |
| Exit Codes | Shell/script exit code handling | [exit-code-patterns.md](references/exit-code-patterns.md) |
| Syntax | Shell syntax, heredocs, quoting | [syntax-patterns.md](references/syntax-patterns.md) |
| Dependencies | Import paths, missing packages | [dependency-patterns.md](references/dependency-patterns.md) |
| Infrastructure | GitHub runners, labels, permissions | [github-infrastructure-patterns.md](references/github-infrastructure-patterns.md) |
| Language-Specific | Python, JS, Rust, Go peculiarities | [language-specific-patterns.md](references/language-specific-patterns.md) |
| Bot Categories | PR author classification for automation | [bot-categories.md](references/bot-categories.md) |
| Claude PR Handling | Workflow for Claude Code Action PRs | [claude-pr-handling.md](references/claude-pr-handling.md) |

**Category contents overview:**
- **Cross-Platform**: 1 Temporary Path Differences, 2 Path Separator Differences, 3 Line Ending Differences, 4 Case Sensitivity Differences
- **Exit Codes**: 1 Exit Code Persistence, 2 Common Exit Codes by Tool, 3 GitHub Actions Exit Code Handling
- **Syntax**: 1 Here-String and Heredoc Terminator Issues, 2 Shell Quoting Differences, 3 Command Substitution Syntax
- **Dependencies**: 1 Module Import Path Issues, 2 Missing Dependencies in CI, 3 Version Mismatches
- **Infrastructure**: 1 Missing Labels, 2 Platform Exceptions and Documentation, 3 Runner Architecture
- **Language-Specific**: 1 Python CI Patterns, 2 JavaScript/TypeScript CI Patterns, 3 Rust CI Patterns, 4 Go CI Patterns
- **Bot Categories**: Overview, Category Table, Detailed Category Definitions, Signal Interpretation Guide, Priority Matrix, Implementation Example, Best Practices, Troubleshooting
- **Claude PR Handling**: Overview, When to Use This Workflow, Claude Code Action Integration, Integration with Monitoring Cycle, Response Patterns for Claude, Complete Workflow Example, Troubleshooting, Best Practices

## Diagnosis Decision Tree

Follow this decision tree to identify the failure category:

```
START: CI Failure Occurred
│
├─► Does error mention path or file not found?
│   ├─► YES → Check Cross-Platform Patterns (temp paths, separators, case sensitivity)
│   └─► NO ↓
│
├─► Does error show non-zero exit code?
│   ├─► YES → Check Exit Code Patterns (persistence, tool-specific codes)
│   └─► NO ↓
│
├─► Does error mention syntax error or unexpected token?
│   ├─► YES → Check Syntax Patterns (heredocs, quoting, line endings)
│   └─► NO ↓
│
├─► Does error mention import/require/module not found?
│   ├─► YES → Check Dependency Patterns (import resolution, versions)
│   └─► NO ↓
│
├─► Does error mention GitHub-specific resources (labels, runners)?
│   ├─► YES → Check Infrastructure Patterns (labels, permissions, runners)
│   └─► NO ↓
│
└─► Check Language-Specific Patterns for the failing language
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

This skill includes two Python scripts for automated diagnosis:

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

## Output Discipline

All scripts support the `--output-file <path>` flag:
- **With flag**: Full JSON written to file; concise summary printed to stderr
- **Without flag**: Full JSON printed to stdout (backward compatible)

When invoking from agents or automated workflows, always pass `--output-file` to minimize token consumption.

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

## Error Handling

### The diagnostic script doesn't identify my failure

Read the full error message and search for keywords in the reference documents. Common keywords:
- "not found", "no such file" → Cross-Platform Patterns
- "exit code", "returned 1" → Exit Code Patterns
- "syntax error", "unexpected" → Syntax Patterns
- "import", "module", "require" → Dependency Patterns
- "permission", "label", "runner" → Infrastructure Patterns

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

## Resources

- [references/cross-platform-patterns.md](references/cross-platform-patterns.md) - OS-specific path and behavior differences
  <!-- TOC: cross-platform-patterns.md -->
  - 1.1 Temporary Path Differences
    - 1.1.1 Windows temp path handling ($env:TEMP)
    - 1.1.2 Linux/macOS temp path handling (/tmp, $TMPDIR)
    - 1.1.3 Language-specific solutions (Python, JavaScript, Bash, PowerShell)
  - 1.2 Path Separator Differences
    - 1.2.1 Forward slash vs backslash behavior
    - 1.2.2 Path normalization techniques
    - 1.2.3 Platform-agnostic path construction
  - 1.3 Line Ending Differences
    - 1.3.1 CRLF vs LF detection
    - 1.3.2 Git autocrlf configuration
    - 1.3.3 Fixing line ending issues in CI
  - 1.4 Case Sensitivity Differences
    - 1.4.1 Filesystem case sensitivity by platform
    - 1.4.2 Common case-related CI failures
    - 1.4.3 Enforcing consistent casing
  <!-- /TOC -->
- [references/exit-code-patterns.md](references/exit-code-patterns.md) - Shell exit code handling
  <!-- TOC: exit-code-patterns.md -->
  - 2.1 Exit Code Persistence
    - 2.1.1 PowerShell $LASTEXITCODE behavior
    - 2.1.2 Bash $? behavior and pitfalls
    - 2.1.3 Solutions for reliable exit code handling
  - 2.2 Common Exit Codes by Tool
    - 2.2.1 Git exit codes
    - 2.2.2 npm/yarn/pnpm exit codes
    - 2.2.3 pytest exit codes
    - 2.2.4 cargo exit codes
  - 2.3 GitHub Actions Exit Code Handling
    - 2.3.1 Step failure detection
    - 2.3.2 continue-on-error behavior
    - 2.3.3 Custom exit code handling
  <!-- /TOC -->
- [references/syntax-patterns.md](references/syntax-patterns.md) - Heredoc and quoting issues
  <!-- TOC: syntax-patterns.md -->
  - 3.1 Here-String and Heredoc Terminator Issues
    - 3.1.1 PowerShell here-string requirements ("@ at column 0)
    - 3.1.2 Bash heredoc requirements (EOF at column 0)
    - 3.1.3 YAML multiline string indentation
  - 3.2 Shell Quoting Differences
    - 3.2.1 Bash quoting rules
    - 3.2.2 POSIX sh quoting rules
    - 3.2.3 Zsh quoting differences
    - 3.2.4 PowerShell quoting rules
  - 3.3 Command Substitution Syntax
    - 3.3.1 Backticks vs $() differences
    - 3.3.2 Nested command substitution
  <!-- /TOC -->
- [references/dependency-patterns.md](references/dependency-patterns.md) - Import and package issues
  <!-- TOC: dependency-patterns.md -->
  - 4.1 Module Import Path Issues
    - 4.1.1 Relative path calculation
    - 4.1.2 Language-specific import resolution
    - 4.1.3 Working directory assumptions
  - 4.2 Missing Dependencies in CI
    - 4.2.1 Lock file synchronization
    - 4.2.2 Optional dependencies
    - 4.2.3 Development vs production dependencies
  - 4.3 Version Mismatches
    - 4.3.1 Pinned version conflicts
    - 4.3.2 Transitive dependency issues
    - 4.3.3 CI-specific version requirements
  <!-- /TOC -->
- [references/github-infrastructure-patterns.md](references/github-infrastructure-patterns.md) - Runner and label issues
  <!-- TOC: github-infrastructure-patterns.md -->
  - 5.1 Missing Labels
    - 5.1.1 Creating labels before workflow uses them
    - 5.1.2 Label API format and authentication
    - 5.1.3 Label naming conventions
  - 5.2 Platform Exceptions and Documentation
    - 5.2.1 Runner operating system differences
    - 5.2.2 Pre-installed software differences
    - 5.2.3 Environment variable differences
  - 5.3 Runner Architecture
    - 5.3.1 x64 vs ARM runner differences
    - 5.3.2 Self-hosted runner considerations
    - 5.3.3 Runner resource limits
  <!-- /TOC -->
- [references/language-specific-patterns.md](references/language-specific-patterns.md) - Python, JS, Rust, Go patterns
  <!-- TOC: language-specific-patterns.md -->
  - 6.1 Python CI Patterns
    - 6.1.1 Virtual environment issues
    - 6.1.2 pip installation failures
    - 6.1.3 pytest configuration issues
  - 6.2 JavaScript/TypeScript CI Patterns
    - 6.2.1 node_modules caching issues
    - 6.2.2 npm vs yarn vs pnpm differences
    - 6.2.3 ESM vs CommonJS issues
  - 6.3 Rust CI Patterns
    - 6.3.1 cargo build failures
    - 6.3.2 Target directory management
    - 6.3.3 Cross-compilation issues
  - 6.4 Go CI Patterns
    - 6.4.1 Module resolution issues
    - 6.4.2 Go version mismatches
    - 6.4.3 CGO dependencies
  <!-- /TOC -->
- [references/bot-categories.md](references/bot-categories.md) - PR author classification
  - **Contents:** Overview, Category Table, Detailed Category Definitions, Signal Interpretation Guide, Priority Matrix, Implementation Example, Best Practices, Troubleshooting
- [references/claude-pr-handling.md](references/claude-pr-handling.md) - Claude Code Action integration
  - **Contents:** Overview, When to Use This Workflow, Claude Code Action Integration, Integration with Monitoring Cycle, Response Patterns for Claude, Complete Workflow Example, Troubleshooting, Best Practices
- [references/debug-procedures.md](references/debug-procedures.md) - Systematic debugging workflow
  <!-- TOC: debug-procedures.md -->
  - 1 When a CI/CD pipeline fails and needs systematic diagnosis
  - 2 When identifying which failure pattern category applies
  - 3 When performing deep root cause analysis by category
  <!-- /TOC -->

## See Also

- GitHub Actions documentation: https://docs.github.com/en/actions
- CI/CD best practices: Use matrix builds to test all platforms
- Error handling: Always use explicit exit codes
