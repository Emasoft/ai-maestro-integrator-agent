---
name: ci-optimized-matrix
description: "How to use the include syntax and strategic matrix design to minimize CI job count without sacrificing coverage."
---

# CI Optimized Matrix

## Table of Contents

- 4.1 Understanding Default Matrix Behavior
  - 4.1.1 Full Cartesian product and its cost
  - 4.1.2 When the Cartesian product is appropriate
- 4.2 Using `include` Syntax for Exact Combinations
  - 4.2.1 How `include` works
  - 4.2.2 Building a selective matrix with `include` only
  - 4.2.3 Complete YAML example with `include`
- 4.3 Side-by-Side Comparison: Cartesian vs Include
  - 4.3.1 Scenario: Multi-OS, multi-version Python testing
  - 4.3.2 Cartesian product approach
  - 4.3.3 Include-based approach
  - 4.3.4 Job count and cost comparison
- 4.4 Using `fail-fast: false` for Full Diagnostic Visibility
  - 4.4.1 Default fail-fast behavior and why it hides failures
  - 4.4.2 Setting `fail-fast: false` to see all results
- 4.5 Conditional Steps Within Matrix Jobs
  - 4.5.1 Running coverage upload on only one matrix entry
  - 4.5.2 Using matrix value expressions in `if` conditions
  - 4.5.3 Complete YAML example with conditional coverage step
- 4.6 Cost Analysis and Optimization Strategy
  - 4.6.1 Calculating CI minute savings
  - 4.6.2 Deciding which combinations to drop

---

## 4.1 Understanding Default Matrix Behavior

### 4.1.1 Full Cartesian Product and Its Cost

When you define a matrix with multiple dimensions, GitHub Actions creates a job
for every combination. This is the Cartesian product:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.11", "3.12", "3.13"]
```

This creates 3 operating systems multiplied by 3 Python versions = 9 jobs.

Each additional dimension multiplies the total. Adding `architecture: [x64, arm64]`
would create 3 * 3 * 2 = 18 jobs. CI costs grow rapidly with each new dimension.

### 4.1.2 When the Cartesian Product Is Appropriate

The full Cartesian product is appropriate when:
- Every combination genuinely needs testing (all OS + all versions used in production)
- The test suite is fast (under 5 minutes per job)
- The repository has sufficient CI minute budget

If any of these conditions are not met, an optimized matrix saves time and money.

---

## 4.2 Using `include` Syntax for Exact Combinations

### 4.2.1 How `include` Works

The `include` key lets you specify exact matrix entries without generating a
Cartesian product. Each `include` entry adds one specific job:

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        python-version: "3.12"
      - os: macos-latest
        python-version: "3.12"
      - os: ubuntu-latest
        python-version: "3.13"
```

This creates exactly 3 jobs -- no more, no less. You control each combination
explicitly.

### 4.2.2 Building a Selective Matrix with `include` Only

When you use `include` without any top-level matrix dimensions, the matrix
contains only the explicitly listed entries. This is the most precise approach:

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - os: ubuntu-latest
        python-version: "3.11"
        label: "Linux Python 3.11"
      - os: ubuntu-latest
        python-version: "3.12"
        label: "Linux Python 3.12"
      - os: ubuntu-latest
        python-version: "3.13"
        label: "Linux Python 3.13"
      - os: macos-latest
        python-version: "3.12"
        label: "macOS Python 3.12"
      - os: windows-latest
        python-version: "3.12"
        label: "Windows Python 3.12"
```

This creates 5 jobs. The primary Python version (3.12) is tested on all three
operating systems, while the additional versions (3.11, 3.13) are tested only
on Linux. This covers the most likely platform-specific issues without paying
for 9 jobs.

### 4.2.3 Complete YAML Example with `include`

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    name: Test (${{ matrix.label }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            python-version: "3.11"
            label: "Linux Py3.11"
          - os: ubuntu-latest
            python-version: "3.12"
            label: "Linux Py3.12"
          - os: ubuntu-latest
            python-version: "3.13"
            label: "Linux Py3.13"
          - os: macos-latest
            python-version: "3.12"
            label: "macOS Py3.12"
          - os: windows-latest
            python-version: "3.12"
            label: "Windows Py3.12"
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Run tests
        run: pytest tests/ -v --tb=short
```

---

## 4.3 Side-by-Side Comparison: Cartesian vs Include

### 4.3.1 Scenario: Multi-OS, Multi-Version Python Testing

Goal: Test Python 3.11, 3.12, and 3.13 on Linux, macOS, and Windows.

### 4.3.2 Cartesian Product Approach

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.11", "3.12", "3.13"]
```

Jobs created: 9 (every combination)

### 4.3.3 Include-Based Approach

```yaml
strategy:
  matrix:
    include:
      - { os: ubuntu-latest, python-version: "3.11" }
      - { os: ubuntu-latest, python-version: "3.12" }
      - { os: ubuntu-latest, python-version: "3.13" }
      - { os: macos-latest, python-version: "3.12" }
      - { os: windows-latest, python-version: "3.12" }
```

Jobs created: 5 (targeted combinations)

### 4.3.4 Job Count and Cost Comparison

| Approach | Jobs | Minutes per job | Total minutes |
|----------|------|-----------------|---------------|
| Cartesian | 9 | 8 | 72 |
| Include | 5 | 8 | 40 |
| **Savings** | **4 fewer** | | **32 minutes** |

The include approach tests all three Python versions (on Linux) and all three
operating systems (with the primary Python version), catching both version-specific
and platform-specific issues.

---

## 4.4 Using `fail-fast: false` for Full Diagnostic Visibility

### 4.4.1 Default Fail-Fast Behavior and Why It Hides Failures

By default, `fail-fast` is `true`. When any matrix job fails, GitHub Actions
cancels all other running matrix jobs. This saves CI minutes but hides failures
that might exist on other platforms or versions.

For example, if the Linux/Python 3.11 job fails, the macOS and Windows jobs
are cancelled immediately. You do not learn whether those platforms also have
issues until you fix the Linux failure and re-run.

### 4.4.2 Setting `fail-fast: false` to See All Results

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - { os: ubuntu-latest, python-version: "3.12" }
      - { os: macos-latest, python-version: "3.12" }
      - { os: windows-latest, python-version: "3.12" }
```

With `fail-fast: false`, all matrix jobs run to completion even if one fails.
You see the full picture of which platforms and versions pass or fail in a
single CI run, reducing the number of push-fix-wait cycles.

---

## 4.5 Conditional Steps Within Matrix Jobs

### 4.5.1 Running Coverage Upload on Only One Matrix Entry

You typically want to collect and upload code coverage from only one matrix entry
to avoid duplicate reports and unnecessary processing time:

```yaml
- name: Upload coverage
  if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
```

### 4.5.2 Using Matrix Value Expressions in `if` Conditions

GitHub Actions expressions can reference `matrix.*` values directly:

```yaml
- name: Run slow integration tests
  if: matrix.os == 'ubuntu-latest'
  run: pytest tests/integration/ -v --timeout=300

- name: Build wheel
  if: matrix.python-version == '3.12'
  run: python -m build --wheel
```

These conditions evaluate at runtime. The step is skipped (not failed) when
the condition is false.

### 4.5.3 Complete YAML Example with Conditional Coverage Step

```yaml
jobs:
  test:
    name: Test (${{ matrix.os }}, Py${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            python-version: "3.11"
          - os: ubuntu-latest
            python-version: "3.12"
            upload-coverage: true
          - os: ubuntu-latest
            python-version: "3.13"
          - os: macos-latest
            python-version: "3.12"
          - os: windows-latest
            python-version: "3.12"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install
        run: pip install -e ".[test]"
      - name: Run tests with coverage
        run: pytest tests/ -v --cov=src --cov-report=xml
      - name: Upload coverage report
        if: matrix.upload-coverage == true
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: false
```

Note the custom `upload-coverage` matrix variable. Only the entry that sets
it to `true` runs the upload step.

---

## 4.6 Cost Analysis and Optimization Strategy

### 4.6.1 Calculating CI Minute Savings

Formula: `(Cartesian jobs - Include jobs) * average minutes per job = saved minutes`

For a project running CI 20 times per day:
- Cartesian: 9 jobs * 8 min * 20 runs = 1,440 minutes/day
- Include: 5 jobs * 8 min * 20 runs = 800 minutes/day
- Savings: 640 minutes/day = approximately 19,200 minutes/month

### 4.6.2 Deciding Which Combinations to Drop

Follow this priority order when deciding which matrix entries to keep:

1. **Keep**: All language/runtime versions on the primary OS (usually Linux)
2. **Keep**: The primary language version on all target operating systems
3. **Consider dropping**: Non-primary versions on non-primary operating systems
4. **Consider dropping**: Older language versions on newer operating systems
   (older versions are more likely to have issues on the same OS they were
   developed on, not on newer platforms)

The goal is to maximize coverage of the two main failure axes (version compatibility
and platform compatibility) while minimizing the combinatorial explosion.
