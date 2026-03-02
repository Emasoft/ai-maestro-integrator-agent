# CI Failure Patterns Skill

Systematically diagnose and fix CI/CD pipeline failures across all platforms (Linux, macOS, Windows) and languages (Python, JavaScript, Rust, Go).

## When to Use

- CI workflow fails and you need to diagnose the cause
- Tests pass locally but fail in CI
- Platform-specific errors (Windows vs Linux vs macOS)
- Unclear exit codes or dependency failures
- GitHub Actions infrastructure issues (labels, permissions, runners)

## Main Features

| Category | What It Covers |
|----------|----------------|
| Cross-Platform | Temp paths, separators, line endings, case sensitivity |
| Exit Codes | Shell exit code handling, tool-specific codes |
| Syntax | Heredocs, quoting, command substitution |
| Dependencies | Import paths, missing packages, version mismatches |
| Infrastructure | GitHub runners, labels, permissions |
| Language-Specific | Python, JS/TS, Rust, Go peculiarities |
| Bot Categories | PR author classification for automation |
| Claude PR Handling | Claude Code Action PR workflow |

## Quick Start

1. Read [SKILL.md](SKILL.md) for the decision tree
2. Run diagnostic script: `python scripts/amia_diagnose_ci_failure.py --log-file ci.log`
3. Consult the appropriate reference in `references/`

## Included Scripts

- `amia_diagnose_ci_failure.py` - Analyzes CI logs to identify failure patterns
- `amia_detect_platform_issue.py` - Scans source code for cross-platform issues

## Reference Documents

- `cross-platform-patterns.md` - OS-specific path and environment differences
- `exit-code-patterns.md` - Exit code handling across shells
- `syntax-patterns.md` - Shell syntax, heredocs, quoting
- `dependency-patterns.md` - Import resolution and package issues
- `github-infrastructure-patterns.md` - Runners, labels, permissions
- `language-specific-patterns.md` - Python, JS, Rust, Go patterns
- `bot-categories.md` - PR author classification for automation
- `claude-pr-handling.md` - Claude Code Action PR workflow
