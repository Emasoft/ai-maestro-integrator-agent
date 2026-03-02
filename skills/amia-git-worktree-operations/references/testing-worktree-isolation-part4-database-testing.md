# Testing Worktrees: Database Testing Patterns

## Table of Contents

1. [Separate Database Per Worktree](#separate-database-per-worktree)
2. [Migration Testing](#migration-testing)
3. [Rollback Testing](#rollback-testing)
4. [Data Isolation](#data-isolation)

---

## Separate Database Per Worktree

**Pattern**: Each test worktree uses its own database instance or database name.

**Implementation**:
```bash
# Create database for worktree
createdb testdb_integration_api_endpoints

# Configure in .env.test
echo "DATABASE_URL=postgresql://localhost/testdb_integration_api_endpoints" > .env.test
```

**Benefits**:
- Complete data isolation
- Parallel test execution
- No test interference
- Easy cleanup

---

## Migration Testing

**What Is Migration Testing**: Verifying database schema changes work correctly.

**Pattern for Testing Migrations**:

1. **Create migration test worktree**:
```bash
python scripts/worktree_create.py \
    --purpose test-migration \
    --identifier add-user-roles \
    --branch feature/user-roles
```

2. **Set up base database**:
```bash
cd worktrees/test-migration-add-user-roles
source .venv/bin/activate

# Create test database
createdb testdb_migration_user_roles

# Run migrations up to before your change
export DATABASE_URL=postgresql://localhost/testdb_migration_user_roles
python manage.py migrate 0042_previous_migration
```

3. **Test forward migration**:
```bash
# Apply your new migration
python manage.py migrate 0043_add_user_roles

# Verify schema changes
psql testdb_migration_user_roles -c "\d users"

# Run tests
pytest tests/migrations/test_0043_add_user_roles.py
```

4. **Test backward migration** (rollback):
```bash
# Rollback migration
python manage.py migrate 0042_previous_migration

# Verify rollback worked
pytest tests/migrations/test_0043_rollback.py
```

---

## Rollback Testing

**What Is Rollback Testing**: Verifying migrations can be safely reversed.

**Pattern**:
```python
# tests/migrations/test_migration_rollback.py
import pytest
from django.db import connection

def test_migration_0043_rollback():
    """Test rolling back user roles migration"""

    # Apply migration
    call_command('migrate', '0043_add_user_roles')

    # Add test data
    User.objects.create(username='test', role='admin')

    # Rollback migration
    call_command('migrate', '0042_previous_migration')

    # Verify rollback
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='users'"
        )
        columns = [row[0] for row in cursor.fetchall()]

        # Role column should be gone
        assert 'role' not in columns
```

---

## Data Isolation

**Pattern**: Ensure test data in one worktree doesn't affect others.

**Implementation**:

1. **Separate database names**:
```python
# conftest.py - Generate database name from worktree
import os
import json

@pytest.fixture(scope='session')
def test_database():
    """Get test database name from worktree metadata"""

    with open('.worktree-metadata.json') as f:
        metadata = json.load(f)

    return metadata['database']
```

2. **Clean database before each test run**:
```python
# conftest.py
@pytest.fixture(scope='session', autouse=True)
def setup_test_database(test_database):
    """Create fresh test database"""

    # Drop if exists
    subprocess.run(['dropdb', '--if-exists', test_database])

    # Create fresh
    subprocess.run(['createdb', test_database], check=True)

    # Run migrations
    os.environ['DATABASE_URL'] = f'postgresql://localhost/{test_database}'
    call_command('migrate')

    yield

    # Cleanup after all tests
    subprocess.run(['dropdb', test_database])
```

---

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Running Tests](testing-worktree-isolation-part3-running-tests.md)
- [Cleanup After Tests](testing-worktree-isolation-part5-cleanup.md)
