# Testing Worktrees: Troubleshooting and Summary

## Table of Contents

1. [Troubleshooting](#troubleshooting)
   - [Test Database Connection Failures](#test-database-connection-failures)
   - [Port Conflicts](#port-conflicts)
   - [Virtual Environment Issues](#virtual-environment-issues)
   - [Migration State Mismatches](#migration-state-mismatches)
   - [Stale Test Worktrees](#stale-test-worktrees)
   - [Test Interference](#test-interference)
2. [Summary](#summary)

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

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Types and Creation](testing-worktree-isolation-part1-types-and-creation.md)
- [CI/CD Integration](testing-worktree-isolation-part6-cicd.md)
