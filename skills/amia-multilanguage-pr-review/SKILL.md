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

Modern repositories often contain code in multiple programming languages. A single repository might have:
- A Python backend with FastAPI
- A TypeScript frontend with React
- Rust binaries for performance-critical operations
- Go microservices
- Bash scripts for automation and CI/CD

Reviewing PRs in such repositories requires understanding which languages are affected and applying the appropriate review standards for each.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for running detection scripts
- Language-specific linters installed (ruff, mypy, ESLint, clippy, etc.)
- Git for local diff analysis

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Language Detection Report | JSON | List of detected languages with file counts and lines changed per language |
| Linter Recommendations | JSON | Recommended linters, install commands, and run commands for each detected language |
| Review Summary | Markdown | Comprehensive review findings organized by language with cross-language impact analysis |
| Linter Results | Text/JSON | Aggregated output from all language-specific linters (ruff, ESLint, clippy, etc.) |

## Instructions

1. Run `amia_detect_pr_languages.py` to identify all programming languages affected by the PR
2. For each detected language, read the corresponding review patterns document from the references directory
3. Execute `amia_get_language_linters.py` to obtain the appropriate linters and their commands for each language
4. Run all recommended linters against the changed files in their respective languages
5. Check for cross-language interface changes (API contracts, FFI boundaries, shared configuration)
6. Verify platform-specific code paths have appropriate guards and tests (see cross-platform-testing.md)
7. Compile linter results and findings into a comprehensive review summary organized by language
8. Write the final review comment with language-specific findings and cross-language impact analysis

## Challenges of Multilanguage Repositories

1. **Different coding standards**: Each language has its own conventions for naming, formatting, and structure
2. **Different testing frameworks**: pytest for Python, Jest for JavaScript, cargo test for Rust
3. **Different linting tools**: ruff/mypy for Python, ESLint for JavaScript, Clippy for Rust
4. **Cross-language interfaces**: FFI boundaries, API contracts, data serialization
5. **Platform-specific code**: Code paths that only run on certain operating systems

## When to Use This Skill

Use this skill when:
- Reviewing a PR that touches files in multiple programming languages
- Setting up review workflows for a polyglot repository
- Determining which linters and checkers to run for changed files
- Coordinating cross-language interface reviews

## Quick Reference: Language Detection

For detailed language detection methods, see [language-detection.md](references/language-detection.md):
- 1.1 Detecting language from file extensions
- 1.2 Detecting language from shebang lines
- 1.3 Using .gitattributes linguist hints
- 1.4 Understanding GitHub's language detection algorithm
- 1.5 Handling mixed-language files

## Quick Reference: Language-Specific Review Patterns

### Python Reviews
See [python-review-patterns.md](references/python-review-patterns.md):
- 2.1 Python code style and formatting checklist
- 2.2 Type hints verification and mypy compliance
- 2.3 Docstring standards (Google, NumPy, Sphinx)
- 2.4 Import organization and dependency management
- 2.5 Test framework patterns with pytest
- 2.6 Linting with ruff, mypy, and bandit

### JavaScript/TypeScript Reviews
See [javascript-review-patterns.md](references/javascript-review-patterns.md):
<!-- TOC: javascript-review-patterns.md -->
- JavaScript/TypeScript Review Patterns Reference
  - Table of Contents
    - Part 1: Style, Types, and Modules
    - Part 2: Testing and Linting
  - Quick Reference: When to Read Each Part
  - Summary Checklists
    - Code Style Quick Check
    - TypeScript Quick Check
    - Module System Quick Check
    - Testing Quick Check
    - Linting Quick Check
<!-- /TOC -->
- 3.1 JavaScript/TypeScript code style checklist
- 3.2 Type safety patterns in TypeScript
- 3.3 Module system considerations (ESM vs CommonJS)
- 3.4 Test framework patterns with Jest and Vitest
- 3.5 Linting with ESLint and Prettier

### Rust Reviews
See [rust-review-patterns.md](references/rust-review-patterns.md):
<!-- TOC: rust-review-patterns.md -->
- Rust Review Patterns Reference
  - Table of Contents
    - 4.1 Rust Code Style and Idioms
    - 4.2 Memory Safety Patterns and Ownership
    - 4.3 Error Handling with Result and Option
    - 4.4 Clippy Lints and Configuration
    - 4.5 Documentation Standards with rustdoc
  - Quick Reference: Review Focus by File Type
  - Quick Reference: Common Review Issues
<!-- /TOC -->
- 4.1 Rust code style and idioms checklist
- 4.2 Memory safety patterns and ownership
- 4.3 Error handling with Result and Option
- 4.4 Clippy lints and configuration
- 4.5 Documentation standards with rustdoc

### Go Reviews
See [go-review-patterns.md](references/go-review-patterns.md):
- 5.1 Go code style and idioms checklist
- 5.2 Error handling patterns in Go
- 5.3 Package organization and naming
- 5.4 Test patterns with go test
- 5.5 Linting with golint, go vet, and staticcheck

### Shell Script Reviews
See [shell-review-patterns.md](references/shell-review-patterns.md):
- 6.1 Bash/Shell script review checklist
- 6.2 POSIX compatibility requirements
- 6.3 ShellCheck lints and fixes
- 6.4 Cross-platform considerations for macOS and Linux

## Quick Reference: Cross-Platform Testing
See [cross-platform-testing.md](references/cross-platform-testing.md):
<!-- TOC: cross-platform-testing.md -->
### Part 1: Testing on Multiple Operating Systems
- 7.1.1 Platform categories and key differences
- 7.1.2 Common platform issues (file paths, line endings, permissions, case sensitivity)
- 7.1.3 Testing matrix dimensions
- 7.1.4 Platform detection in tests (Python and TypeScript)

### Part 2: CI Matrix Configuration for GitHub Actions
- 7.2.1 Basic matrix configuration (os, python-version)
- 7.2.2 Extended matrix with include/exclude
- 7.2.3 Node.js matrix example
- 7.2.4 Rust matrix example
- 7.2.5 Conditional steps based on matrix

### Part 3: Platform-Specific Test Skips and Annotations
- 7.3.1 Python (pytest) platform skips and custom markers
- 7.3.2 JavaScript (Jest/Vitest) conditional tests
- 7.3.3 Rust conditional compilation for tests
- 7.3.4 Go build tags and runtime skips

### Part 4: Using Docker for Reproducible Builds
- 7.4.1 Multi-platform Docker build with multi-stage
- 7.4.2 GitHub Actions with Docker services
- 7.4.3 Multi-architecture builds (amd64, arm64)
- 7.4.4 Docker Compose for testing
- 7.4.5 Development containers (devcontainer)
- 7.4.6 Docker testing checklist
<!-- /TOC -->
- 7.1 Testing on multiple operating systems
- 7.2 CI matrix configuration for GitHub Actions
- 7.3 Platform-specific test skips and annotations
- 7.4 Using Docker for reproducible builds

**Contents:**
- Testing on Multiple Operating Systems
- Platform categories and key differences
- Common platform issues (file paths, line endings, permissions, case sensitivity)
- Testing matrix dimensions
- Platform detection in tests (Python and TypeScript)
- CI Matrix Configuration for GitHub Actions
- Basic matrix configuration (os, python-version)
- Extended matrix with include/exclude
- Node.js matrix example
- Rust matrix example
- Conditional steps based on matrix
- Platform-Specific Test Skips and Annotations
- Python (pytest) platform skips and custom markers
- JavaScript (Jest/Vitest) conditional tests
- Rust conditional compilation for tests
- Go build tags and runtime skips
- Using Docker for Reproducible Builds
- Multi-platform Docker build with multi-stage
- GitHub Actions with Docker services
- Multi-architecture builds (amd64, arm64)
- Docker Compose for testing
- Development containers (devcontainer)
- Docker testing checklist

## Decision Tree: PR Review Approach

```
START: New PR to review
  |
  v
[1] Run amia_detect_pr_languages.py to identify languages
  |
  v
[2] For each detected language:
  |
  +---> Is it Python? ---> Read python-review-patterns.md, run ruff + mypy
  |
  +---> Is it JavaScript/TypeScript? ---> Read javascript-review-patterns.md, run ESLint
  |
  +---> Is it Rust? ---> Read rust-review-patterns.md, run cargo clippy
  |
  +---> Is it Go? ---> Read go-review-patterns.md, run go vet + staticcheck
  |
  +---> Is it Bash/Shell? ---> Read shell-review-patterns.md, run ShellCheck
  |
  v
[3] Check for cross-language interfaces:
  |
  +---> API contracts between services? ---> Verify schema compatibility
  |
  +---> FFI boundaries? ---> Check type mappings and safety
  |
  +---> Shared configuration? ---> Ensure consistency
  |
  v
[4] Check for platform-specific code:
  |
  +---> Multiple OS targets? ---> Read cross-platform-testing.md
  |
  v
[5] Run amia_get_language_linters.py for each language to get linter commands
  |
  v
[6] Execute all linters and compile results
  |
  v
[7] Write review summary with findings per language
  |
  v
END
```

## Included Scripts

### amia_detect_pr_languages.py
Detects programming languages in a PR's changed files.

**Usage**:
```bash
# Detect languages in PR #123
python scripts/amia_detect_pr_languages.py --repo owner/repo --pr 123

# Detect languages in local diff
python scripts/amia_detect_pr_languages.py --diff-file changes.diff
```

**Output**: JSON with language breakdown and file counts.

### amia_get_language_linters.py
Returns recommended linters and commands for a given language.

**Usage**:
```bash
# Get linters for Python
python scripts/amia_get_language_linters.py --language python

# Get linters for multiple languages
python scripts/amia_get_language_linters.py --languages python,javascript,rust
```

**Output**: JSON with linter names, install commands, and run commands.

## Workflow Example

When reviewing a PR in a multilanguage repository:

```bash
# Step 1: Detect languages in the PR
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 456

# Example output:
# {
#   "languages": {
#     "python": {"files": 12, "lines_changed": 450},
#     "typescript": {"files": 5, "lines_changed": 200},
#     "bash": {"files": 2, "lines_changed": 50}
#   },
#   "primary_language": "python"
# }

# Step 2: Get linters for detected languages
python scripts/amia_get_language_linters.py --languages python,typescript,bash

# Example output:
# {
#   "python": {
#     "linters": ["ruff", "mypy"],
#     "commands": {
#       "ruff": "ruff check .",
#       "mypy": "mypy --strict ."
#     }
#   },
#   ...
# }

# Step 3: Read the appropriate review patterns for each language
# Step 4: Run linters and compile results
# Step 5: Write comprehensive review
```

## Common Pitfalls

1. **Ignoring generated files**: Many repos have generated code (protobuf, OpenAPI). Identify and skip these.
2. **Over-linting vendored code**: Third-party vendored code should be excluded from linting.
3. **Missing cross-language impacts**: A Python change might break a TypeScript client consuming its API.
4. **Platform assumptions**: Code working on Linux might fail on macOS due to path handling.
5. **Different Python versions**: A repo might support Python 3.8-3.12 with different type hint syntax.

## Examples

### Example 1: Detect Languages and Run Linters

```bash
# Detect languages in PR
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 456
# Output: {"languages": {"python": {"files": 12}, "typescript": {"files": 5}}}

# Get recommended linters
python scripts/amia_get_language_linters.py --languages python,typescript
# Output: {"python": {"linters": ["ruff", "mypy"]}, "typescript": {"linters": ["eslint"]}}

# Run linters for each language
ruff check src/python/
eslint src/typescript/
```

### Example 2: Cross-Language API Review

```bash
# Detect languages
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 789

# If both Python (backend) and TypeScript (frontend) changed,
# verify API contracts are consistent between them
# Check OpenAPI/JSON schema compatibility
```

## Error Handling

### Problem: Language detection returns unexpected results
**Solution**: Check .gitattributes for linguist overrides. Some files may be marked with `linguist-language` or `linguist-detectable=false`.

### Problem: Linter fails to run
**Solution**: Ensure the linter is installed. Use amia_get_language_linters.py to get install commands.

### Problem: Too many linting errors
**Solution**: For legacy codebases, consider using `--fix` flags where available (ruff --fix, eslint --fix) and reviewing the automated fixes.

### Problem: Cross-platform test failures
**Solution**: Read cross-platform-testing.md section 7.3 for platform-specific skip annotations.

## Checklist: Multilanguage PR Review

Copy this checklist and track your progress:

- [ ] Detect all languages in the PR using amia_detect_pr_languages.py
- [ ] Read the review patterns document for each detected language
- [ ] Run appropriate linters for each language
- [ ] Check for cross-language interface changes
- [ ] Verify platform-specific code has appropriate guards
- [ ] Ensure tests exist for new functionality in each language
- [ ] Check CI configuration covers all affected languages
- [ ] Verify documentation is updated if public APIs changed

## Resources

- [references/language-detection.md](references/language-detection.md) - Language detection methods
- [references/python-review-patterns.md](references/python-review-patterns.md) - Python review checklist
- [references/javascript-review-patterns.md](references/javascript-review-patterns.md) - JavaScript/TypeScript review
  **Contents:** JavaScript/TypeScript Code Style Checklist, Type Safety Patterns in TypeScript, Module System Considerations (ESM vs CommonJS), Test Framework Patterns with Jest and Vitest, Linting with ESLint and Prettier
- [references/rust-review-patterns.md](references/rust-review-patterns.md) - Rust review checklist
  **Contents:** Rust Code Style and Idioms, Memory Safety Patterns and Ownership, Error Handling with Result and Option, Clippy Lints and Configuration, Documentation Standards with rustdoc
- [references/go-review-patterns.md](references/go-review-patterns.md) - Go review checklist
- [references/shell-review-patterns.md](references/shell-review-patterns.md) - Shell script review
- [references/cross-platform-testing.md](references/cross-platform-testing.md) - Multi-OS testing
