---
name: ci-linting-workflow
description: "How to set up a parallel language-specific linting workflow with pinned versions and GitHub annotation output."
---

# CI Linting Workflow

## Table of Contents

- 5.1 Why Linting Should Be a Separate Workflow
  - 5.1.1 Independence from test and build jobs
  - 5.1.2 Fast feedback for developers
- 5.2 Pinning Linter Versions
  - 5.2.1 Why pinning matters for reproducibility
  - 5.2.2 Where to pin: CI config, pre-commit config, and package config in sync
  - 5.2.3 Version pinning strategy across environments
- 5.3 Separate Check vs Format Steps
  - 5.3.1 Why both steps matter
  - 5.3.2 Check mode detects violations; format mode shows what would change
  - 5.3.3 Each step can fail independently for clear diagnostics
- 5.4 GitHub Annotation Output Format
  - 5.4.1 Ruff output format for GitHub annotations
  - 5.4.2 ESLint output format for GitHub annotations
  - 5.4.3 Biome CI mode vs check mode
  - 5.4.4 How annotations appear in pull request diffs
- 5.5 Complete YAML Example: Parallel Lint Jobs
  - 5.5.1 Python linting with ruff
  - 5.5.2 JavaScript/TypeScript linting with ESLint or Biome
  - 5.5.3 Gate job aggregating lint results
- 5.6 Path Filters for Lint Workflows
  - 5.6.1 Including linter configuration files in triggers
  - 5.6.2 Separating Python and JS/TS path triggers

---

## 5.1 Why Linting Should Be a Separate Workflow

### 5.1.1 Independence from Test and Build Jobs

Linting does not depend on installing project dependencies, compiling code, or
setting up databases. It operates purely on source files and linter configuration.
Running lint as part of the test workflow means lint results are delayed until
dependencies are installed and the test environment is ready.

A separate lint workflow starts immediately, runs in under 60 seconds for most
projects, and reports results before the test workflow even finishes installing
dependencies.

### 5.1.2 Fast Feedback for Developers

Developers get lint feedback within 30-60 seconds of pushing. This fast feedback
loop encourages fixing style issues immediately rather than accumulating them for
a later cleanup. By the time the developer reads the lint results, the longer
test workflow is still running.

---

## 5.2 Pinning Linter Versions

### 5.2.1 Why Pinning Matters for Reproducibility

Linter versions can change behavior between releases. A new ruff or ESLint release
may flag code that previously passed, causing CI failures unrelated to any code
change. Pinning ensures that CI results are reproducible and that failures always
correspond to actual code issues.

### 5.2.2 Where to Pin: CI Config, Pre-Commit Config, and Package Config in Sync

Linter versions should be identical in all of these locations:

| Location | File | Example |
|----------|------|---------|
| CI workflow | `.github/workflows/lint.yml` | `pip install ruff==0.8.4` |
| Pre-commit | `.pre-commit-config.yaml` | `rev: v0.8.4` |
| Project config | `pyproject.toml` | `ruff = "==0.8.4"` in dev dependencies |

For JavaScript/TypeScript:

| Location | File | Example |
|----------|------|---------|
| CI workflow | `.github/workflows/lint.yml` | `npx eslint@9.17.0` or `npx @biomejs/biome@1.9.4` |
| Package config | `package.json` | `"eslint": "9.17.0"` or `"@biomejs/biome": "1.9.4"` |

### 5.2.3 Version Pinning Strategy Across Environments

1. Choose a single source of truth for the linter version (usually the project
   configuration file: `pyproject.toml` for Python, `package.json` for JS/TS)
2. Reference that version in CI by installing from the project config:
   ```yaml
   - name: Install linter from project config
     run: pip install -e ".[lint]"
   ```
   or for JavaScript:
   ```yaml
   - name: Install dependencies
     run: npm ci
   ```
3. Update versions in one place; CI and pre-commit inherit automatically

---

## 5.3 Separate Check vs Format Steps

### 5.3.1 Why Both Steps Matter

A check step runs the linter in read-only mode and reports violations. A format
check verifies that code matches the formatter's expected style. These are
conceptually different:

- **Lint check**: Detects code quality issues (unused imports, unreachable code,
  security patterns, complexity)
- **Format check**: Detects style inconsistencies (indentation, spacing, line
  length, quote style)

### 5.3.2 Check Mode Detects Violations; Format Mode Shows What Would Change

For ruff:
```bash
# Lint check -- reports violations
ruff check src/ tests/

# Format check -- exits non-zero if any file would be reformatted
ruff format --check src/ tests/
```

For ESLint:
```bash
# Lint check
npx eslint src/ --max-warnings=0

# Format check (if using ESLint for formatting)
npx eslint src/ --fix-dry-run
```

For Biome:
```bash
# Lint and format check in CI mode
npx @biomejs/biome ci src/
```

### 5.3.3 Each Step Can Fail Independently for Clear Diagnostics

Separating lint check and format check into distinct steps means the developer
can see exactly what type of issue was found:

```yaml
steps:
  - name: Lint check
    run: ruff check src/ tests/ --output-format=github
  - name: Format check
    run: ruff format --check src/ tests/
```

If the lint check step fails but the format check passes, the developer knows
they have a code quality issue, not a formatting issue.

---

## 5.4 GitHub Annotation Output Format

### 5.4.1 Ruff Output Format for GitHub Annotations

Ruff supports a `github` output format that writes annotations directly into
the pull request file diff:

```bash
ruff check src/ tests/ --output-format=github
```

This produces output in the GitHub Actions annotation format:
```
::error file=src/main.py,line=42,col=5::F841 Local variable `x` is assigned to but never used
```

GitHub renders these as inline annotations on the affected lines in the pull
request diff view.

### 5.4.2 ESLint Output Format for GitHub Annotations

ESLint uses formatters. Use a GitHub-compatible formatter:

```bash
npx eslint src/ --format @microsoft/eslint-formatter-sarif --output-file eslint-results.sarif
```

Then upload the SARIF file:
```yaml
- name: Upload SARIF
  if: always()
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: eslint-results.sarif
```

Alternatively, use the stylish formatter and rely on the problem matcher:
```yaml
- name: Run ESLint
  run: npx eslint src/ --max-warnings=0
```

GitHub Actions has a built-in problem matcher for ESLint that converts the
standard output into annotations.

### 5.4.3 Biome CI Mode vs Check Mode

Biome has two modes relevant to CI:

| Command | Behavior |
|---------|----------|
| `biome check` | Reports issues, exits non-zero on errors only |
| `biome ci` | Reports issues, exits non-zero on errors AND warnings |

Use `biome ci` in CI workflows for strict enforcement:

```bash
npx @biomejs/biome ci src/ --formatter-enabled=true --linter-enabled=true
```

Biome outputs annotations in GitHub-compatible format by default when it detects
it is running in GitHub Actions (via the `GITHUB_ACTIONS` environment variable).

### 5.4.4 How Annotations Appear in Pull Request Diffs

When a linter produces GitHub-compatible annotation output, the annotations
appear as yellow (warning) or red (error) inline comments directly on the
affected lines in the pull request "Files changed" tab. This eliminates the
need to dig through raw log output to find the issue location.

---

## 5.5 Complete YAML Example: Parallel Lint Jobs

### 5.5.1 Python Linting with Ruff

```yaml
name: Lint

on:
  pull_request:
    branches: [main]
    paths:
      - "src/**/*.py"
      - "tests/**/*.py"
      - "pyproject.toml"
      - "ruff.toml"
      - ".github/workflows/lint.yml"

jobs:
  python-lint:
    name: Python Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install ruff
        run: pip install ruff==0.8.4
      - name: Ruff lint check
        run: ruff check src/ tests/ --output-format=github
      - name: Ruff format check
        run: ruff format --check src/ tests/
```

### 5.5.2 JavaScript/TypeScript Linting with ESLint or Biome

```yaml
  js-lint:
    name: JS/TS Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
      - name: Install dependencies
        run: npm ci
      - name: ESLint check
        run: npx eslint src/ --max-warnings=0
      # Or, if using Biome instead of ESLint:
      # - name: Biome CI check
      #   run: npx @biomejs/biome ci src/
```

### 5.5.3 Gate Job Aggregating Lint Results

```yaml
  lint-gate:
    name: Lint Gate
    needs: [python-lint, js-lint]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Check lint results
        run: |
          echo "Python lint: ${{ needs.python-lint.result }}"
          echo "JS/TS lint:  ${{ needs.js-lint.result }}"

          failed=0
          for result in \
            "${{ needs.python-lint.result }}" \
            "${{ needs.js-lint.result }}"; do
            if [[ "$result" != "success" ]] && [[ "$result" != "skipped" ]]; then
              failed=1
            fi
          done

          if [[ "$failed" -eq 1 ]]; then
            echo "LINT GATE FAILED"
            exit 1
          fi
          echo "LINT GATE PASSED"
```

---

## 5.6 Path Filters for Lint Workflows

### 5.6.1 Including Linter Configuration Files in Triggers

Changes to linter configuration files can change which rules are active. Always
include these in your path triggers:

| Linter | Configuration files to include |
|--------|-------------------------------|
| Ruff | `ruff.toml`, `pyproject.toml` (contains `[tool.ruff]`) |
| ESLint | `eslint.config.js`, `.eslintrc.*`, `.eslintignore` |
| Biome | `biome.json`, `biome.jsonc` |
| General | `.github/workflows/lint.yml` |

### 5.6.2 Separating Python and JS/TS Path Triggers

If you have separate lint jobs for Python and JavaScript/TypeScript, you can use
job-level `if` conditions to skip individual jobs based on changed files. However,
it is simpler to keep one unified lint workflow with path filters that cover both
languages and let both lint jobs run. The per-language jobs are fast enough (under
60 seconds each) that the optimization of skipping one is rarely worth the added
complexity.
