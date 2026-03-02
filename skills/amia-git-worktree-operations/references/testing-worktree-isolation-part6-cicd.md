# Testing Worktrees: CI/CD Integration

## Table of Contents

1. [Matrix Testing with Worktrees](#matrix-testing-with-worktrees)
2. [Parallel Test Execution](#parallel-test-execution)
3. [Artifact Collection](#artifact-collection)

---

## Matrix Testing with Worktrees

**What Is Matrix Testing**: Running tests across multiple configurations (Python versions, dependency versions, etc.).

**Pattern Using Worktrees**:

**GitHub Actions Example**:
```yaml
# .github/workflows/matrix-test.yml
name: Matrix Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Create test worktree
        run: |
          python scripts/worktree_create.py \
            --purpose test-matrix \
            --identifier py${{ matrix.python-version }} \
            --branch ${{ github.ref_name }} \
            --ports

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        working-directory: worktrees/test-matrix-py${{ matrix.python-version }}
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        working-directory: worktrees/test-matrix-py${{ matrix.python-version }}
        run: |
          source .venv/bin/activate
          pytest tests/ -v --junitxml=junit-${{ matrix.python-version }}.xml

      - name: Cleanup worktree
        if: always()
        run: |
          python scripts/worktree_remove.py --identifier py${{ matrix.python-version }}
```

---

## Parallel Test Execution

**Pattern**: Run multiple test suites simultaneously using separate worktrees.

**Local Parallel Execution**:
```bash
#!/bin/bash
# scripts/run_parallel_tests.sh

# Create test worktrees for different test suites
python scripts/worktree_create.py --purpose test-unit --identifier suite1 --branch main &
python scripts/worktree_create.py --purpose test-integration --identifier suite2 --branch main --ports &
python scripts/worktree_create.py --purpose test-performance --identifier suite3 --branch main --ports &

# Wait for creation
wait

# Run tests in parallel
(cd worktrees/test-unit-suite1 && source .venv/bin/activate && pytest tests/unit/) &
(cd worktrees/test-integration-suite2 && source .venv/bin/activate && pytest tests/integration/) &
(cd worktrees/test-performance-suite3 && source .venv/bin/activate && pytest tests/performance/) &

# Wait for completion
wait

# Cleanup
python scripts/worktree_remove.py --identifier suite1 &
python scripts/worktree_remove.py --identifier suite2 &
python scripts/worktree_remove.py --identifier suite3 &
wait
```

**GitHub Actions Parallel Example**:
```yaml
# .github/workflows/parallel-tests.yml
name: Parallel Tests

on: [push]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          python scripts/worktree_create.py --purpose test-unit --identifier ci-unit --branch ${{ github.ref_name }}
          cd worktrees/test-unit-ci-unit
          python -m venv .venv && source .venv/bin/activate
          pip install -r requirements.txt -r requirements-test.txt
          pytest tests/unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: |
          python scripts/worktree_create.py --purpose test-integration --identifier ci-integration --branch ${{ github.ref_name }} --ports
          cd worktrees/test-integration-ci-integration
          python -m venv .venv && source .venv/bin/activate
          pip install -r requirements.txt -r requirements-test.txt
          pytest tests/integration/ -v

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run performance tests
        run: |
          python scripts/worktree_create.py --purpose test-performance --identifier ci-perf --branch ${{ github.ref_name }}
          cd worktrees/test-performance-ci-perf
          python -m venv .venv && source .venv/bin/activate
          pip install -r requirements.txt -r requirements-test.txt
          pytest tests/performance/ -v
```

---

## Artifact Collection

**What Are Test Artifacts**: Files generated during testing (coverage reports, logs, screenshots, etc.).

**Pattern for Collecting Artifacts from Worktrees**:

**Local Collection**:
```python
# scripts/collect_test_artifacts.py
import os
import shutil
from pathlib import Path

def collect_artifacts(worktree_id, output_dir='test-artifacts'):
    """Collect test artifacts from worktree"""

    worktree_path = Path('worktrees') / worktree_id
    output_path = Path(output_dir) / worktree_id
    output_path.mkdir(parents=True, exist_ok=True)

    # Coverage reports
    coverage_html = worktree_path / 'htmlcov'
    if coverage_html.exists():
        shutil.copytree(coverage_html, output_path / 'coverage')

    # JUnit XML
    for junit_file in worktree_path.glob('junit-*.xml'):
        shutil.copy(junit_file, output_path)

    # Logs
    log_dir = worktree_path / 'logs'
    if log_dir.exists():
        shutil.copytree(log_dir, output_path / 'logs')

    print(f"✓ Artifacts collected to {output_path}")
```

**GitHub Actions Collection**:
```yaml
# In workflow file
- name: Run tests
  working-directory: worktrees/test-integration-ci
  run: |
    source .venv/bin/activate
    pytest tests/ -v --junitxml=junit.xml --cov=src --cov-report=html

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: |
      worktrees/test-integration-ci/junit.xml
      worktrees/test-integration-ci/htmlcov/

- name: Upload logs
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-logs
    path: worktrees/test-integration-ci/logs/
```

---

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Cleanup After Tests](testing-worktree-isolation-part5-cleanup.md)
- [Troubleshooting](testing-worktree-isolation-part7-troubleshooting.md)
