# Multilanguage PR Review — Detailed Guide

## Contents

- [Challenges of Multilanguage Repositories](#challenges-of-multilanguage-repositories)
- [When to Use This Skill](#when-to-use-this-skill)
- [Decision Tree: PR Review Approach](#decision-tree-pr-review-approach)
- [Included Scripts](#included-scripts)
- [Workflow Example](#workflow-example)
- [Common Pitfalls](#common-pitfalls)
- [Error Handling](#error-handling)
- [Language-Specific Quick References](#language-specific-quick-references)

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

# Step 3: Read the appropriate review patterns for each language
# Step 4: Run linters and compile results
# Step 5: Write comprehensive review
```

### Cross-Language API Review

```bash
# Detect languages
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 789

# If both Python (backend) and TypeScript (frontend) changed,
# verify API contracts are consistent between them
# Check OpenAPI/JSON schema compatibility
```

## Common Pitfalls

1. **Ignoring generated files**: Many repos have generated code (protobuf, OpenAPI). Identify and skip these.
2. **Over-linting vendored code**: Third-party vendored code should be excluded from linting.
3. **Missing cross-language impacts**: A Python change might break a TypeScript client consuming its API.
4. **Platform assumptions**: Code working on Linux might fail on macOS due to path handling.
5. **Different Python versions**: A repo might support Python 3.8-3.12 with different type hint syntax.

## Error Handling

### Problem: Language detection returns unexpected results

**Solution**: Check .gitattributes for linguist overrides. Some files may be marked with `linguist-language` or `linguist-detectable=false`.

### Problem: Linter fails to run

**Solution**: Ensure the linter is installed. Use amia_get_language_linters.py to get install commands.

### Problem: Too many linting errors

**Solution**: For legacy codebases, consider using `--fix` flags where available (ruff --fix, eslint --fix) and reviewing the automated fixes.

### Problem: Cross-platform test failures

**Solution**: Read cross-platform-testing.md section 7.3 for platform-specific skip annotations.

## Language-Specific Quick References

### Python Reviews

See `python-review-patterns.md` for:
- Python code style and formatting checklist
- Type hints verification and mypy compliance
- Docstring standards (Google, NumPy, Sphinx)
- Import organization and dependency management
- Test framework patterns with pytest
- Linting with ruff, mypy, and bandit

### JavaScript/TypeScript Reviews

See `javascript-review-patterns.md` for:
- Code style checklist
- Type safety patterns in TypeScript
- Module system considerations (ESM vs CommonJS)
- Test framework patterns with Jest and Vitest
- Linting with ESLint and Prettier

### Rust Reviews

See `rust-review-patterns.md` for:
- Code style and idioms checklist
- Memory safety patterns and ownership
- Error handling with Result and Option
- Clippy lints and configuration
- Documentation standards with rustdoc

### Go Reviews

See `go-review-patterns.md` for:
- Code style and idioms checklist
- Error handling patterns
- Package organization and naming
- Test patterns with go test
- Linting with golint, go vet, and staticcheck

### Shell Script Reviews

See `shell-review-patterns.md` for:
- Bash/Shell script review checklist
- POSIX compatibility requirements
- ShellCheck lints and fixes
- Cross-platform considerations for macOS and Linux

### Cross-Platform Testing

See `cross-platform-testing.md` for:
- Testing on multiple operating systems
- CI matrix configuration for GitHub Actions
- Platform-specific test skips and annotations
- Using Docker for reproducible builds
