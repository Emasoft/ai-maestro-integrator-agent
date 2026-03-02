# Multilanguage PR Review Skill

Review pull requests in repositories containing multiple programming languages (Python, TypeScript, Rust, Go, Bash) with language-specific linting and cross-platform testing.

## When to Use

- Reviewing PRs that touch files in multiple languages
- Setting up review workflows for polyglot repositories
- Determining which linters/checkers to run for changed files
- Coordinating cross-language interface reviews (FFI, API contracts)

## Main Features

| Feature | Description |
|---------|-------------|
| Language Detection | Auto-detect languages from extensions, shebangs, .gitattributes |
| Per-Language Review Patterns | Python, JS/TS, Rust, Go, Shell checklists |
| Cross-Platform Testing | CI matrix config, OS-specific test handling |
| Linter Routing | Get correct linters per language automatically |

## Quick Start

```bash
# Detect languages in a PR
python scripts/amia_detect_pr_languages.py --repo owner/repo --pr 123

# Get linters for detected languages
python scripts/amia_get_language_linters.py --languages python,typescript,rust
```

## Key References

| File | Purpose |
|------|---------|
| `references/language-detection.md` | How to detect languages in files |
| `references/python-review-patterns.md` | Python review checklist (ruff, mypy) |
| `references/javascript-review-patterns.md` | JS/TS review checklist (ESLint) |
| `references/rust-review-patterns.md` | Rust review checklist (Clippy) |
| `references/go-review-patterns.md` | Go review checklist (staticcheck) |
| `references/shell-review-patterns.md` | Shell review checklist (ShellCheck) |
| `references/cross-platform-testing.md` | Multi-OS CI configuration |

## Required Tools

- `gh` - GitHub CLI
- `git` - Version control
