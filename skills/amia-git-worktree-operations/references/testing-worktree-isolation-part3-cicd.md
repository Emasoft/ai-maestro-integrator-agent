# Testing in Isolated Worktrees - Part 3: CI/CD & Troubleshooting

## Table of Contents

1. [When integrating with CI/CD → CI/CD Integration](#cicd-integration)
   - [If running matrix tests → Matrix Testing with Worktrees](#matrix-testing-with-worktrees)
   - [When running tests in parallel → Parallel Test Execution](#parallel-test-execution)
   - [If collecting test artifacts → Artifact Collection](#artifact-collection)
2. [When you encounter testing problems → Troubleshooting](#troubleshooting)
   - [If database connections fail → Test Database Connection Failures](#test-database-connection-failures)
   - [When ports are already in use → Port Conflicts](#port-conflicts)
   - [If virtual environment has issues → Virtual Environment Issues](#virtual-environment-issues)
   - [When migrations don't match → Migration State Mismatches](#migration-state-mismatches)
   - [If worktrees accumulate → Stale Test Worktrees](#stale-test-worktrees)
   - [When tests affect each other → Test Interference](#test-interference)
3. [If you need a testing summary → Summary](#summary)

**Related Documents**:
- [Part 1: Fundamentals](testing-worktree-isolation-part1-fundamentals.md)
- [Part 2: Test Execution & Database Patterns](testing-worktree-isolation-part2-execution.md)

---

## CI/CD Integration

### Matrix Testing with Worktrees

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

### Parallel Test Execution

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

### Artifact Collection

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

## Troubleshooting

### Test Database Connection Failures

**Problem**: Tests fail with "cannot connect to database".

**Solutions**:

1. **Check database exists**:
```bash
psql -l | grep testdb_integration_api_endpoints
```

2. **Verify environment variable**:
```bash
echo $DATABASE_URL
# Should show: postgresql://localhost/testdb_integration_api_endpoints
```

3. **Create database if missing**:
```bash
createdb testdb_integration_api_endpoints
```

4. **Check database permissions**:
```bash
psql testdb_integration_api_endpoints -c "SELECT current_user;"
```

### Port Conflicts

**Problem**: Tests fail with "address already in use".

**Solutions**:

1. **Check port allocation**:
```bash
cat .worktree-metadata.json | grep -A3 ports
```

2. **Find process using port**:
```bash
lsof -i :8001
```

3. **Kill conflicting process**:
```bash
kill -9 <PID>
```

4. **Request new ports**:
```bash
# Remove and recreate worktree with fresh ports
python scripts/worktree_remove.py --identifier api-endpoints
python scripts/worktree_create.py --purpose test-integration --identifier api-endpoints --branch main --ports
```

### Virtual Environment Issues

**Problem**: Wrong Python version or missing packages.

**Solutions**:

1. **Verify venv is activated**:
```bash
which python
# Should point to worktree/.venv/bin/python
```

2. **Recreate virtual environment**:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
```

3. **Check Python version**:
```bash
python --version
```

### Migration State Mismatches

**Problem**: "Migration already applied" or "migration not found" errors.

**Solutions**:

1. **Check migration status**:
```bash
python manage.py showmigrations
```

2. **Reset test database**:
```bash
dropdb testdb_migration_test
createdb testdb_migration_test
python manage.py migrate
```

3. **Verify migration files**:
```bash
ls -la migrations/
git status migrations/
```

### Stale Test Worktrees

**Problem**: Too many old test worktrees consuming disk space.

**Solutions**:

1. **List all test worktrees**:
```bash
python scripts/worktree_list.py | grep test-
```

2. **Remove specific worktree**:
```bash
python scripts/worktree_remove.py --identifier old-test
```

3. **Cleanup old worktrees** (older than 24 hours):
```bash
python scripts/cleanup_test_worktrees.py --max-age 24
```

### Test Interference

**Problem**: Tests pass in isolation but fail when run together.

**Solutions**:

1. **Run tests in random order**:
```bash
pytest tests/ --random-order
```

2. **Use separate database per test**:
```python
@pytest.fixture(scope='function')
def db(test_database):
    """Fresh database for each test"""
    # Truncate all tables
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE users CASCADE;")
```

3. **Create separate worktree per test suite**:
```bash
# Instead of one worktree for all tests
python scripts/worktree_create.py --purpose test-unit --identifier all-tests --branch main

# Create one per suite
python scripts/worktree_create.py --purpose test-unit --identifier user-tests --branch main
python scripts/worktree_create.py --purpose test-unit --identifier api-tests --branch main
```

---

## Summary

**Key Takeaways**:

1. **Isolation** - Each test worktree is completely independent
2. **Parallel** - Run multiple test suites simultaneously
3. **Database** - Use separate database per worktree
4. **Ports** - Allocate unique ports for integration tests
5. **Cleanup** - Always remove worktrees after testing
6. **CI/CD** - Use worktrees for matrix and parallel testing

**When to Use Test Worktrees**:
- Yes: Integration tests needing services
- Yes: Performance testing
- Yes: Pre-merge validation
- Yes: Migration testing
- Yes: Matrix testing (multiple Python versions)
- No: Quick unit tests (overhead not worth it)

**Essential Commands**:
```bash
# Create test worktree
python scripts/worktree_create.py --purpose test-integration --identifier my-test --branch main --ports

# Run tests
cd worktrees/test-integration-my-test
source .venv/bin/activate
export $(cat .env.test | xargs)
pytest tests/integration/

# Cleanup
python scripts/worktree_remove.py --identifier my-test
```

---

**Complete Documentation**:
- [Part 1: Fundamentals](testing-worktree-isolation-part1-fundamentals.md) - Overview, Types, Creation, Environment Setup
- [Part 2: Test Execution & Database Patterns](testing-worktree-isolation-part2-execution.md) - Running Tests, Database Patterns, Cleanup
- [Part 3: CI/CD & Troubleshooting](testing-worktree-isolation-part3-cicd.md) - CI/CD Integration, Troubleshooting, Summary
