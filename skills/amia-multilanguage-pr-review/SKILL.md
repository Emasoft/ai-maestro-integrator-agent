---
name: amia-multilanguage-pr-review
description: Use when reviewing PRs in multilanguage repositories. Routes reviews to appropriate language checkers. Trigger with /review-multilang [PR_NUMBER].
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
  category: code-review
  complexity: advanced
  requires_tools: "gh, git"
  supported_languages: "python, javascript, typescript, rust, go, bash, shell"
agent: code-reviewer
context: fork
user-invocable: false
---

# Multilanguage PR Review Skill

## Overview

Reviews PRs in polyglot repositories by detecting affected languages, routing to language-specific review patterns, running appropriate linters, and checking cross-language interfaces. For detailed workflows and decision trees, see `references/detailed-guide.md`.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for detection scripts
- Language-specific linters installed (ruff, mypy, ESLint, clippy, etc.)
- Git for local diff analysis

## Instructions

1. Run `amia_detect_pr_languages.py` to identify all languages affected by the PR
2. For each detected language, read the corresponding review patterns from references
3. Run `amia_get_language_linters.py` to get linter commands for each language
4. Execute all recommended linters against changed files
5. Check cross-language interface changes (API contracts, FFI, shared config)
6. Verify platform-specific code paths have guards and tests
7. Write review summary with per-language findings and cross-language impact

### Checklist

Copy this checklist and track your progress:

- [ ] Detect all languages using amia_detect_pr_languages.py
- [ ] Read review patterns for each detected language
- [ ] Run appropriate linters per language
- [ ] Check cross-language interface changes
- [ ] Verify platform-specific code has guards
- [ ] Ensure tests exist for new functionality per language
- [ ] Check CI covers all affected languages
- [ ] Verify docs updated if public APIs changed

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Language Detection | JSON | Detected languages with file counts and lines changed |
| Linter Recommendations | JSON | Linters, install commands, run commands per language |
| Review Summary | Markdown | Findings by language with cross-language analysis |
| Linter Results | Text/JSON | Aggregated linter output |

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

**Language Detection:**

- `references/language-detection.md` — detection methods overview
- `references/language-detection-part1-extensions-shebang.md` — file extensions and shebang detection
- `references/language-detection-part2-gitattributes-algorithm.md` — gitattributes and GitHub algorithm
- `references/language-detection-part3-mixed-language.md` — mixed-language file handling

**Language-Specific Review Patterns:**

- `references/python-review-patterns.md` — Python review overview
- `references/python-review-patterns-part1-style-types-docstrings.md` — style, types, docstrings
- `references/python-review-patterns-part2-imports-tests-linting.md` — imports, tests, linting
- `references/javascript-review-patterns.md` — JS/TS review overview
- `references/javascript-review-patterns-part1-style-types-modules.md` — style, types, modules
- `references/javascript-review-patterns-part2-testing-linting.md` — testing, linting
- `references/rust-review-patterns.md` — Rust review overview
- `references/go-review-patterns.md` — Go review overview
- `references/shell-review-patterns.md` — Shell script review overview

**Cross-Platform and Security:**

- `references/cross-platform-testing.md` — multi-OS testing overview
- `references/security-review-patterns.md` — security review patterns

**Operations:**

- `references/op-detect-pr-languages.md` — language detection operation
- `references/op-get-language-linters.md` — linter lookup operation
- `references/op-run-multilang-linters.md` — run linters operation
- `references/op-review-cross-language.md` — cross-language review operation
- `references/op-compile-multilang-review.md` — compile review operation
- `references/detailed-guide.md` — decision trees, workflows, error handling, pitfalls

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

### Example 1: Detect and Lint a Multilanguage PR

```bash
# Detect languages
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 456
# Get linters
python scripts/amia_get_language_linters.py --languages python,typescript
# Run linters
ruff check src/python/
eslint src/typescript/
```

## Resources

See `references/` directory for all reference documents.
