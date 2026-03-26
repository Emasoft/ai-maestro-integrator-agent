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

Reviews polyglot PRs by detecting languages, routing to language-specific patterns, and checking cross-language interfaces.

## Prerequisites

- GitHub CLI (`gh`) authenticated
- Python 3.8+ and language-specific linters (ruff, ESLint, clippy, etc.)
- Git for local diff analysis

## Instructions

1. Run `amia_detect_pr_languages.py` to identify affected languages
2. Read corresponding review patterns and run `amia_get_language_linters.py`
3. Execute linters against changed files
4. Check cross-language interfaces (API contracts, FFI, shared config)
5. Write review summary with per-language findings and cross-language impact

### Checklist

Copy this checklist and track your progress:

- [ ] Detect languages using amia_detect_pr_languages.py
- [ ] Read review patterns and run linters per language
- [ ] Check cross-language interface changes
- [ ] Verify platform-specific code has guards and tests
- [ ] Ensure CI covers all affected languages
- [ ] Verify docs updated if public APIs changed

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Language Detection | JSON | Detected languages with file counts and lines changed |
| Linter Recommendations | JSON | Linters, install commands, run commands per language |
| Review Summary | Markdown | Findings by language with cross-language analysis |
| Linter Results | Text/JSON | Aggregated linter output |

> **Output discipline:** All scripts support `--output-file <path>`.

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See the detailed guide in Resources.

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

Full reference: [detailed-guide](references/detailed-guide.md):
  - Challenges of Multilanguage Repositories
  - When to Use This Skill
  - Decision Tree: PR Review Approach
  - Included Scripts
    - amia_detect_pr_languages.py
    - amia_get_language_linters.py
  - Workflow Example
    - Cross-Language API Review
  - Common Pitfalls
  - Error Handling
    - Problem: Language detection returns unexpected results
    - Problem: Linter fails to run
    - Problem: Too many linting errors
    - Problem: Cross-platform test failures
  - Language-Specific Quick References
    - Python Reviews
    - JavaScript/TypeScript Reviews
    - Rust Reviews
    - Go Reviews
    - Shell Script Reviews
    - Cross-Platform Testing
  - Full Reference Document Index
