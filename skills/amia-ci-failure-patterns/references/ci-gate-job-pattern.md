---
name: ci-gate-job-pattern
description: "How to aggregate multiple CI jobs into a single branch protection check using a gate job."
---

# CI Gate Job Pattern

## Table of Contents

- 1.1 Understanding the Gate Job Pattern
  - 1.1.1 What is a gate job and why you need one
  - 1.1.2 The problem with per-job branch protection
- 1.2 Implementing a Gate Job with `if: always()` and `needs`
  - 1.2.1 The `needs` keyword for job dependency declaration
  - 1.2.2 The `if: always()` condition to run regardless of upstream results
  - 1.2.3 Checking upstream job results in the gate step
- 1.3 Complete YAML Example with Three Dependent Jobs
  - 1.3.1 Full workflow definition
  - 1.3.2 Walkthrough of each section
- 1.4 Configuring Branch Protection to Use the Gate
  - 1.4.1 GitHub repository settings for required status checks
  - 1.4.2 Naming convention for the gate check
- 1.5 Handling Skipped Jobs as Acceptable
  - 1.5.1 Why jobs get skipped (path filters, conditional logic)
  - 1.5.2 Variant gate logic that treats `skipped` as OK
- 1.6 Anti-Pattern: Branch Protection Without a Gate
  - 1.6.1 The matrix entry problem
  - 1.6.2 Why adding or removing jobs breaks protection rules

---

## 1.1 Understanding the Gate Job Pattern

### 1.1.1 What Is a Gate Job and Why You Need One

A gate job is a single GitHub Actions job that runs after all other CI jobs and reports
a single pass/fail status. Branch protection rules in your repository settings then
require only this one gate job to succeed before a pull request can be merged.

Without a gate job, you must list every individual CI job name in branch protection
settings. When you add a new matrix entry, rename a job, or remove one, branch
protection breaks silently -- either blocking all merges or allowing broken code through.

A gate job solves this by acting as a single aggregation point. It inspects the
results of all upstream jobs and exits with code 0 (success) only if every required
upstream job succeeded.

### 1.1.2 The Problem with Per-Job Branch Protection

When you list individual job names in branch protection (for example `test-linux`,
`test-macos`, `lint`), any change to the workflow structure causes one of two failures:

1. **Merge blocked forever**: You add `test-windows` to the matrix but forget to add
   it to branch protection. The old required check `test-linux` still passes, but
   GitHub now sees `test-windows` as a new, unknown check and does not require it.
   Then you rename `test-linux` to `test-ubuntu` and branch protection now waits
   forever for a check named `test-linux` that will never arrive.

2. **Broken code merged**: You remove `test-macos` from the matrix. Branch protection
   still requires a check named `test-macos`. Since that check never runs, GitHub
   treats it as "pending" -- but some configurations interpret a never-arriving check
   as not required, allowing the pull request to merge without macOS testing.

---

## 1.2 Implementing a Gate Job with `if: always()` and `needs`

### 1.2.1 The `needs` Keyword for Job Dependency Declaration

The `needs` keyword tells GitHub Actions that a job depends on one or more other jobs.
The gate job must list every job it aggregates in its `needs` array:

```yaml
gate:
  needs: [lint, test, build]
```

By default, a job with `needs` only runs if all listed jobs succeeded. This is not
what you want for a gate job because if `lint` fails, the gate job would be skipped
entirely, and branch protection would see the gate as "pending" forever.

### 1.2.2 The `if: always()` Condition to Run Regardless of Upstream Results

Adding `if: always()` to the gate job tells GitHub Actions to run the gate job
no matter what happened to the upstream jobs -- whether they succeeded, failed,
were cancelled, or were skipped:

```yaml
gate:
  needs: [lint, test, build]
  if: always()
```

This ensures the gate job always runs and always reports a status to branch protection.

### 1.2.3 Checking Upstream Job Results in the Gate Step

Inside the gate job, you inspect each upstream job result using the expression
`needs.<job-id>.result`. The possible values are:

| Value | Meaning |
|-------|---------|
| `success` | The job completed without errors |
| `failure` | The job completed with errors (non-zero exit code) |
| `cancelled` | The job was cancelled (by user or concurrency group) |
| `skipped` | The job was skipped (due to `if` condition or path filter) |

The gate step checks each result and exits with code 1 if any upstream job
did not succeed:

```bash
if [[ "${{ needs.lint.result }}" != "success" ]] || \
   [[ "${{ needs.test.result }}" != "success" ]] || \
   [[ "${{ needs.build.result }}" != "success" ]]; then
  echo "One or more required jobs did not succeed"
  echo "  lint:  ${{ needs.lint.result }}"
  echo "  test:  ${{ needs.test.result }}"
  echo "  build: ${{ needs.build.result }}"
  exit 1
fi
echo "All required jobs succeeded"
```

---

## 1.3 Complete YAML Example with Three Dependent Jobs

### 1.3.1 Full Workflow Definition

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linters
        run: |
          echo "Running lint checks..."
          # Replace with your actual lint command
          npm run lint

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run tests
        run: |
          pip install -e ".[test]"
          pytest tests/

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build package
        run: |
          pip install build
          python -m build

  gate:
    name: CI Gate
    needs: [lint, test, build]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Check all job results
        run: |
          echo "Job results:"
          echo "  lint:  ${{ needs.lint.result }}"
          echo "  test:  ${{ needs.test.result }}"
          echo "  build: ${{ needs.build.result }}"

          if [[ "${{ needs.lint.result }}" != "success" ]] || \
             [[ "${{ needs.test.result }}" != "success" ]] || \
             [[ "${{ needs.build.result }}" != "success" ]]; then
            echo "GATE FAILED: One or more jobs did not succeed"
            exit 1
          fi

          echo "GATE PASSED: All jobs succeeded"
```

### 1.3.2 Walkthrough of Each Section

- **lint, test, build**: These are the actual CI jobs. They run in parallel by default
  because none depends on another.
- **gate**: This job depends on all three upstream jobs via `needs: [lint, test, build]`.
  The `if: always()` ensures it runs even if upstream jobs fail or are cancelled.
  The step inspects each result and fails the gate if any upstream job did not succeed.

---

## 1.4 Configuring Branch Protection to Use the Gate

### 1.4.1 GitHub Repository Settings for Required Status Checks

1. Navigate to your repository on GitHub
2. Go to Settings > Branches > Branch protection rules
3. Click "Add rule" or edit an existing rule for `main`
4. Check "Require status checks to pass before merging"
5. In the search box, type `CI Gate` (the `name:` field of the gate job)
6. Select the matching check and save

Now only the gate job status matters. You can freely add, remove, or rename the
upstream jobs without ever touching branch protection settings again.

### 1.4.2 Naming Convention for the Gate Check

Use a descriptive, stable name for the gate job. The `name:` field in the YAML
(not the job ID) is what appears in GitHub. Common conventions:

| Pattern | Example |
|---------|---------|
| `<workflow> Gate` | `CI Gate` |
| `All checks passed` | `All checks passed` |
| `Required checks` | `Required checks` |

Choose one name and never change it. This is the only name that goes into
branch protection.

---

## 1.5 Handling Skipped Jobs as Acceptable

### 1.5.1 Why Jobs Get Skipped

Jobs may be skipped when:
- Path filters exclude the job's trigger (documentation-only changes skip test jobs)
- An `if` condition evaluates to false
- A preceding job in the dependency chain was skipped

When a job is skipped, its result is `skipped`, not `success`. A strict gate
that only accepts `success` will fail on documentation-only pull requests.

### 1.5.2 Variant Gate Logic That Treats `skipped` as OK

To allow skipped jobs to pass the gate, check for both `success` and `skipped`:

```yaml
gate:
  name: CI Gate
  needs: [lint, test, build]
  if: always()
  runs-on: ubuntu-latest
  steps:
    - name: Check all job results
      run: |
        check_result() {
          local job_name="$1"
          local result="$2"
          if [[ "$result" != "success" ]] && [[ "$result" != "skipped" ]]; then
            echo "FAIL: $job_name = $result"
            return 1
          fi
          echo "OK:   $job_name = $result"
          return 0
        }

        failed=0
        check_result "lint"  "${{ needs.lint.result }}"  || failed=1
        check_result "test"  "${{ needs.test.result }}"  || failed=1
        check_result "build" "${{ needs.build.result }}" || failed=1

        if [[ "$failed" -eq 1 ]]; then
          echo "GATE FAILED"
          exit 1
        fi
        echo "GATE PASSED"
```

This variant treats `skipped` the same as `success` but still fails on `failure`
or `cancelled`.

---

## 1.6 Anti-Pattern: Branch Protection Without a Gate

### 1.6.1 The Matrix Entry Problem

Consider a test matrix with `os: [ubuntu-latest, macos-latest]`. GitHub creates
two check names: `test (ubuntu-latest)` and `test (macos-latest)`. If you add
these both to branch protection and later add `windows-latest` to the matrix,
the new `test (windows-latest)` check is not required. It can fail without
blocking the merge.

If you later remove `macos-latest` from the matrix, branch protection still
requires `test (macos-latest)`. That check never arrives, and pull requests
are blocked forever (or until someone manually updates branch protection).

### 1.6.2 Why Adding or Removing Jobs Breaks Protection Rules

Any structural change to the workflow -- adding a job, removing a job, renaming
a job, changing a matrix entry -- requires a corresponding manual update to
branch protection settings. This creates a maintenance burden and a window
where protection is misconfigured.

The gate job eliminates this entirely. Branch protection references only the
gate job name, which never changes regardless of how many upstream jobs exist.
