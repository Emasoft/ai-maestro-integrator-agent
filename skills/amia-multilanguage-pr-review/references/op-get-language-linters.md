# Operation: Get Language Linters

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Output Structure](#output-structure)
- [Procedure](#procedure)
- [Command](#command)
- [Example](#example)
- [Language Linter Reference](#language-linter-reference)
  - [Python](#python)
  - [JavaScript/TypeScript](#javascripttypescript)
  - [Rust](#rust)
  - [Go](#go)
  - [Shell/Bash](#shellbash)
- [Linter Installation](#linter-installation)
- [Customizing Linter Commands](#customizing-linter-commands)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Retrieve the appropriate linters, type checkers, and static analysis tools for each programming language detected in a PR. This includes install commands and run commands.

## When to Use

- After detecting languages in a PR (op-detect-pr-languages)
- When setting up automated review pipeline
- When configuring CI checks for a multilanguage repo

## Prerequisites

- Languages detected from PR
- Python 3.8+ for running script

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--language` | String | Alt | Single language to get linters for |
| `--languages` | String | Alt | Comma-separated list of languages |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `<language>` | Object | Linter configuration for each language |
| `linters` | Array | List of recommended linters |
| `install` | Object | Install commands for each linter |
| `commands` | Object | Run commands for each linter |

## Output Structure

```json
{
  "python": {
    "linters": ["ruff", "mypy", "bandit"],
    "install": {
      "ruff": "pip install ruff",
      "mypy": "pip install mypy",
      "bandit": "pip install bandit"
    },
    "commands": {
      "ruff": "ruff check .",
      "mypy": "mypy --strict .",
      "bandit": "bandit -r src/"
    }
  },
  "typescript": {
    "linters": ["eslint", "tsc"],
    "install": {
      "eslint": "npm install eslint",
      "tsc": "npm install typescript"
    },
    "commands": {
      "eslint": "eslint src/",
      "tsc": "tsc --noEmit"
    }
  }
}
```

## Procedure

1. Run the linter lookup script with detected languages
2. Parse the JSON output
3. Verify linters are installed (or install them)
4. Use commands to run linters on changed files

## Command

```bash
# Get linters for a single language
python scripts/amia_get_language_linters.py --language python

# Get linters for multiple languages
python scripts/amia_get_language_linters.py --languages python,typescript,bash
```

## Example

```bash
# After detecting python, typescript, and bash in a PR
python scripts/amia_get_language_linters.py --languages python,typescript,bash

# Output shows recommended linters for each language
```

## Language Linter Reference

### Python

| Linter | Purpose | Command |
|--------|---------|---------|
| ruff | Linting + formatting | `ruff check .` |
| mypy | Type checking | `mypy --strict .` |
| bandit | Security checks | `bandit -r src/` |
| black | Formatting (legacy) | `black --check .` |

### JavaScript/TypeScript

| Linter | Purpose | Command |
|--------|---------|---------|
| eslint | Linting | `eslint src/` |
| prettier | Formatting | `prettier --check .` |
| tsc | Type checking (TS) | `tsc --noEmit` |

### Rust

| Linter | Purpose | Command |
|--------|---------|---------|
| clippy | Linting | `cargo clippy --all-targets` |
| rustfmt | Formatting | `cargo fmt --check` |

### Go

| Linter | Purpose | Command |
|--------|---------|---------|
| go vet | Static analysis | `go vet ./...` |
| staticcheck | Linting | `staticcheck ./...` |
| gofmt | Formatting | `gofmt -d .` |

### Shell/Bash

| Linter | Purpose | Command |
|--------|---------|---------|
| shellcheck | Linting | `shellcheck scripts/*.sh` |
| shfmt | Formatting | `shfmt -d .` |

## Linter Installation

The script provides install commands for each linter:

```bash
# Install Python linters
pip install ruff mypy bandit

# Install Node linters
npm install -g eslint prettier typescript

# Install Rust linters (via rustup)
rustup component add clippy rustfmt

# Install Go linters
go install honnef.co/go/tools/cmd/staticcheck@latest

# Install Shell linters
brew install shellcheck shfmt  # macOS
apt install shellcheck shfmt   # Ubuntu
```

## Customizing Linter Commands

The default commands may need customization for your project:

```bash
# Default ruff
ruff check .

# Customized for specific paths
ruff check src/ tests/ --config pyproject.toml

# Default mypy
mypy --strict .

# Customized with config
mypy --config-file mypy.ini src/
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Linter not installed | Use install command from output |
| Unknown language | Empty object returned |
| Linter command fails | Check linter configuration in project |

## Related Operations

- [op-detect-pr-languages.md](op-detect-pr-languages.md) - Detect languages first
- [op-run-multilang-linters.md](op-run-multilang-linters.md) - Execute the linters
- [op-compile-multilang-review.md](op-compile-multilang-review.md) - Compile results
