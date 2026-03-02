---
name: ci-path-filtered-triggers
description: "How to use path filters in GitHub Actions triggers to skip CI runs on non-code changes."
---

# CI Path-Filtered Triggers

## Table of Contents

- 3.1 Understanding Path Filters in Workflow Triggers
  - 3.1.1 The `paths:` filter syntax
  - 3.1.2 The `paths-ignore:` filter syntax
  - 3.1.3 Choosing between `paths` and `paths-ignore`
- 3.2 Always Including the Workflow File Itself
  - 3.2.1 Why the workflow YAML must be in the paths list
  - 3.2.2 Example of self-referencing workflow trigger
- 3.3 Common Path Filter Patterns
  - 3.3.1 Skip on documentation-only changes
  - 3.3.2 Skip on asset-only changes
  - 3.3.3 Include build configuration files that affect the build
- 3.4 Complete YAML Example with Push and Pull Request Path Filters
  - 3.4.1 Full workflow definition
  - 3.4.2 Walkthrough of path filter logic
- 3.5 Per-Event Scope of Path Filters
  - 3.5.1 Gotcha: `paths` applies per-event, not globally
  - 3.5.2 Different path filters for push vs pull_request
- 3.6 Interaction with Gate Jobs
  - 3.6.1 Path-filtered jobs produce `skipped` status
  - 3.6.2 Gate job must handle `skipped` as acceptable
  - 3.6.3 Cross-reference to gate job pattern
- 3.7 Anti-Pattern: Overly Broad Paths
  - 3.7.1 Catching everything defeats the purpose
  - 3.7.2 How to audit and refine your path filters

---

## 3.1 Understanding Path Filters in Workflow Triggers

### 3.1.1 The `paths:` Filter Syntax

The `paths:` filter specifies which file paths must be changed for the workflow
to trigger. If none of the changed files match any pattern in `paths:`, the
workflow run is skipped entirely.

```yaml
on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

This workflow only runs when files under `src/`, `tests/`, or the file
`pyproject.toml` are modified. A commit that only changes `README.md` will
not trigger the workflow.

### 3.1.2 The `paths-ignore:` Filter Syntax

The `paths-ignore:` filter is the inverse: the workflow runs unless all changed
files match the ignore patterns.

```yaml
on:
  push:
    branches: [main]
    paths-ignore:
      - "docs/**"
      - "*.md"
      - "LICENSE"
```

This workflow runs on any push that changes at least one file NOT matching the
ignore patterns. A commit that only changes `docs/guide.md` and `README.md`
will not trigger the workflow, but a commit that changes `docs/guide.md` and
`src/main.py` will trigger it.

### 3.1.3 Choosing Between `paths` and `paths-ignore`

| Approach | Best when | Risk |
|----------|-----------|------|
| `paths:` | You know exactly which directories contain code | New directories are not covered until added |
| `paths-ignore:` | You want to exclude known non-code paths | New non-code directories trigger CI until excluded |

**Recommendation**: Use `paths:` (explicit inclusion) for CI workflows because it
is safer. If you add a new non-code directory like `assets/`, CI does not run
needlessly. With `paths-ignore:`, you must remember to add `assets/` to the
ignore list.

---

## 3.2 Always Including the Workflow File Itself

### 3.2.1 Why the Workflow YAML Must Be in the Paths List

When you change the workflow YAML file (for example, `.github/workflows/ci.yml`),
you want CI to run so you can verify the workflow change works. If the workflow
file is not in the `paths:` list, changes to the workflow itself will not trigger
a run, and you cannot test your CI changes.

### 3.2.2 Example of Self-Referencing Workflow Trigger

```yaml
on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
      - ".github/workflows/ci.yml"   # Always include the workflow file itself
```

For `paths-ignore:`, the workflow file is not ignored by default, so no extra
action is needed. But explicitly listing it in `paths:` ensures it is never
accidentally excluded.

---

## 3.3 Common Path Filter Patterns

### 3.3.1 Skip on Documentation-Only Changes

Documentation changes (markdown files, docs directory, license) do not affect
the build or tests:

```yaml
paths:
  - "src/**"
  - "tests/**"
  - "pyproject.toml"
  - "package.json"
  - "Cargo.toml"
  - ".github/workflows/ci.yml"
  # Deliberately NOT including: docs/, *.md, LICENSE, CHANGELOG.md
```

### 3.3.2 Skip on Asset-Only Changes

Static assets (images, fonts, design files) do not affect code:

```yaml
paths-ignore:
  - "assets/**"
  - "static/**"
  - "*.png"
  - "*.jpg"
  - "*.svg"
  - "*.ico"
```

### 3.3.3 Include Build Configuration Files That Affect the Build

These files can change build behavior and must trigger CI:

| Language/Ecosystem | Configuration files to include |
|--------------------|-------------------------------|
| Python | `pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`, `uv.lock` |
| JavaScript/TypeScript | `package.json`, `package-lock.json`, `bun.lockb`, `tsconfig.json` |
| Rust | `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml` |
| Go | `go.mod`, `go.sum` |
| General | `.github/workflows/*.yml`, `Makefile`, `Dockerfile` |

---

## 3.4 Complete YAML Example with Push and Pull Request Path Filters

### 3.4.1 Full Workflow Definition

```yaml
name: CI

on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
      - "uv.lock"
      - ".github/workflows/ci.yml"
  pull_request:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
      - "uv.lock"
      - ".github/workflows/ci.yml"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Run tests
        run: pytest tests/ -v
```

### 3.4.2 Walkthrough of Path Filter Logic

When a developer pushes a commit that changes only `README.md`:
1. GitHub compares the changed files against the `paths:` list
2. `README.md` does not match any pattern (`src/**`, `tests/**`, etc.)
3. The workflow is skipped entirely -- no runner is allocated, no minutes are used

When a developer pushes a commit that changes `src/utils.py` and `docs/guide.md`:
1. GitHub compares changed files against the `paths:` list
2. `src/utils.py` matches `src/**`
3. The workflow triggers because at least one changed file matches

---

## 3.5 Per-Event Scope of Path Filters

### 3.5.1 Gotcha: `paths` Applies Per-Event, Not Globally

Path filters are defined under each event type (`push:`, `pull_request:`), not
at the workflow level. You must duplicate the path list under each event:

```yaml
on:
  push:
    branches: [main]
    paths:         # This paths list only applies to push events
      - "src/**"
  pull_request:
    branches: [main]
    paths:         # This paths list only applies to pull_request events
      - "src/**"
```

There is no global `paths:` key that applies to all events. If you only add
`paths:` under `push:` but not under `pull_request:`, pull request events will
trigger on every file change.

### 3.5.2 Different Path Filters for Push vs Pull Request

In some cases, you may want different filters for each event. For example,
push to `main` should always run (no path filter), but pull requests should
be path-filtered:

```yaml
on:
  push:
    branches: [main]
    # No paths filter -- every push to main runs CI
  pull_request:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

---

## 3.6 Interaction with Gate Jobs

### 3.6.1 Path-Filtered Jobs Produce `skipped` Status

When a path filter prevents a job from running, that job's status is `skipped`.
This is important if you have a gate job (see [ci-gate-job-pattern.md](ci-gate-job-pattern.md))
that checks upstream job results.

### 3.6.2 Gate Job Must Handle `skipped` as Acceptable

If the gate job only accepts `success`, documentation-only pull requests will
fail the gate because the test job was skipped. The gate must treat `skipped`
as an acceptable result:

```yaml
gate:
  needs: [lint, test, build]
  if: always()
  runs-on: ubuntu-latest
  steps:
    - name: Check results
      run: |
        for job in lint test build; do
          result="${{ needs[job].result }}"
          # This expression syntax does not work -- you must expand each explicitly
        done

        # Explicit check for each job:
        for result in \
          "${{ needs.lint.result }}" \
          "${{ needs.test.result }}" \
          "${{ needs.build.result }}"; do
          if [[ "$result" != "success" ]] && [[ "$result" != "skipped" ]]; then
            echo "GATE FAILED: found result=$result"
            exit 1
          fi
        done
        echo "GATE PASSED"
```

### 3.6.3 Cross-Reference to Gate Job Pattern

For the full gate job implementation including the `skipped` variant, see
[ci-gate-job-pattern.md](ci-gate-job-pattern.md), section 1.5.

---

## 3.7 Anti-Pattern: Overly Broad Paths

### 3.7.1 Catching Everything Defeats the Purpose

An overly broad paths list is equivalent to having no path filter:

```yaml
# BAD: This matches almost everything, defeating the purpose of path filtering
paths:
  - "**"
```

```yaml
# BAD: Too broad -- catches config files that rarely change
paths:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"
  - "**/*.json"
  - "**/*.yaml"
  - "**/*.yml"
  - "**/*.toml"
```

### 3.7.2 How to Audit and Refine Your Path Filters

1. Review your recent CI runs using the GitHub Actions UI
2. For each run, check the "Files changed" tab on the associated commit/PR
3. Count how many runs were triggered by documentation-only or asset-only changes
4. Add those paths to your filter exclusions
5. Monitor for one week and adjust

A well-tuned path filter typically reduces CI runs by 20-40% on active repositories
with frequent documentation and configuration updates.
