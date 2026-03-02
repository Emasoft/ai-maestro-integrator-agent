# Testing in Isolated Worktrees - Part 2: Test Execution & Database Patterns

## Table of Contents

1. [When you need to run tests → Running Tests in Isolation](#running-tests-in-isolation)
   - [If running unit tests → Unit Tests](#unit-tests)
   - [When running integration tests → Integration Tests](#integration-tests)
   - [If benchmarking performance → Performance Tests](#performance-tests)
2. [When you need database testing patterns → Database Testing Patterns](#database-testing-patterns)
   - [If you need separate databases → Separate Database Per Worktree](#separate-database-per-worktree)
   - [When testing migrations → Migration Testing](#migration-testing)
   - [If you need rollback testing → Rollback Testing](#rollback-testing)
   - [When ensuring data isolation → Data Isolation](#data-isolation)
3. [When you need to clean up after tests → Cleanup After Tests](#cleanup-after-tests)
   - [If removing test worktrees → Removing Test Worktrees](#removing-test-worktrees)
   - [When releasing ports → Releasing Ports](#releasing-ports)
   - [If cleaning databases → Cleaning Test Databases](#cleaning-test-databases)

**Related Documents**:
- [Part 1: Fundamentals](testing-worktree-isolation-part1-fundamentals.md)
- [Part 3: CI/CD & Troubleshooting](testing-worktree-isolation-part3-cicd.md)

---

## Running Tests in Isolation

### Unit Tests

**What Are Unit Tests**: Tests that verify individual functions or classes in isolation.

**Running Unit Tests in Worktree**:
```bash
# Navigate to test worktree
cd worktrees/test-unit-user-model

# Activate environment
source .venv/bin/activate

# Run unit tests only
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_user.py -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

**Benefits of Isolated Unit Test Worktrees**:
- Test different branches simultaneously
- No dependency conflicts
- Reproducible results
- Safe from interference

### Integration Tests

**What Are Integration Tests**: Tests that verify multiple components working together.

**Running Integration Tests in Worktree**:
```bash
# Navigate to integration test worktree
cd worktrees/test-integration-api-endpoints

# Activate environment
source .venv/bin/activate

# Load test environment with ports
export $(cat .env.test | xargs)

# Start required services on allocated ports
python manage.py runserver $APP_PORT &
celery -A tasks worker --loglevel=info &

# Run integration tests
pytest tests/integration/ -v

# Stop services after tests
pkill -f "runserver $APP_PORT"
pkill -f "celery"
```

**Integration Test Example** with allocated ports:
```python
# tests/integration/test_api.py
import os
import requests
import pytest

@pytest.fixture
def api_url():
    """Get API URL from environment"""
    port = os.getenv('API_PORT', '8002')
    return f'http://localhost:{port}'

def test_create_user(api_url):
    """Test user creation through API"""
    response = requests.post(
        f'{api_url}/users',
        json={'username': 'testuser', 'email': 'test@example.com'}
    )
    assert response.status_code == 201
    assert 'id' in response.json()
```

### Performance Tests

**What Are Performance Tests**: Tests that measure speed, throughput, or resource usage.

**Running Performance Tests in Worktree**:
```bash
# Navigate to performance test worktree
cd worktrees/test-performance-queries

# Activate environment
source .venv/bin/activate

# Load test database
export $(cat .env.test | xargs)

# Run performance tests with profiling
pytest tests/performance/ -v --profile

# Or use dedicated performance tool
locust -f tests/performance/load_test.py --host=http://localhost:8001
```

**Performance Test Example**:
```python
# tests/performance/test_query_speed.py
import time
import pytest
from models import User

def test_user_query_performance():
    """Verify user query completes within 100ms"""
    start = time.time()

    # Execute query
    users = User.objects.filter(active=True).all()
    list(users)  # Force evaluation

    duration = time.time() - start

    # Assert performance requirement
    assert duration < 0.1, f"Query took {duration}s, expected < 0.1s"
```

**Why Use Isolated Performance Worktrees**:
- No interference from other processes
- Consistent baseline
- Reproducible measurements
- Compare performance across branches

---

## Database Testing Patterns

### Separate Database Per Worktree

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

### Migration Testing

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

### Rollback Testing

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

### Data Isolation

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

## Cleanup After Tests

### Removing Test Worktrees

**When to Remove**:
- After tests complete
- When branch is merged
- When worktree is no longer needed

**Manual Removal**:
```bash
python scripts/worktree_remove.py --identifier api-endpoints
```

**Automated Removal** (in CI or cleanup script):
```python
# scripts/cleanup_test_worktrees.py
import json
from datetime import datetime, timedelta
from worktree_remove import remove_worktree

def cleanup_old_test_worktrees(max_age_hours=24):
    """Remove test worktrees older than specified hours"""

    with open('worktrees_registry.json') as f:
        registry = json.load(f)

    cutoff = datetime.now() - timedelta(hours=max_age_hours)

    for worktree_id, info in registry.get('worktrees', {}).items():
        # Only cleanup test worktrees
        if not info['purpose'].startswith('test-'):
            continue

        created = datetime.fromisoformat(info['created'])

        if created < cutoff:
            print(f"Removing old test worktree: {worktree_id}")
            remove_worktree(worktree_id)
```

### Releasing Ports

**Why Release Ports**: Make them available for future test worktrees.

**How Ports Are Released**:

When you run `worktree_remove.py`, it automatically:
1. Reads allocated ports from worktree metadata
2. Removes port allocation from registry
3. Makes ports available for reuse

**Manual Port Release** (if needed):
```python
# scripts/release_ports.py
import json

def release_ports(worktree_id):
    """Release ports allocated to worktree"""

    with open('worktrees_registry.json', 'r') as f:
        registry = json.load(f)

    # Get worktree info
    worktree = registry['worktrees'].get(worktree_id)
    if not worktree or 'ports' not in worktree:
        return

    # Remove from allocated ports
    allocated = registry.get('allocated_ports', [])
    for port in worktree['ports'].values():
        if port in allocated:
            allocated.remove(port)

    registry['allocated_ports'] = allocated

    with open('worktrees_registry.json', 'w') as f:
        json.dump(registry, f, indent=2)
```

### Cleaning Test Databases

**Pattern**: Remove test databases when worktree is removed.

**Automated Cleanup**:
```python
# In worktree_remove.py
def cleanup_test_database(metadata):
    """Drop test database for worktree"""

    if 'database' not in metadata:
        return

    db_name = metadata['database']

    # Drop PostgreSQL database
    subprocess.run(['dropdb', '--if-exists', db_name])

    print(f"✓ Removed test database: {db_name}")
```

**Manual Database Cleanup**:
```bash
# List all test databases
psql -l | grep testdb_

# Drop specific test database
dropdb testdb_integration_api_endpoints

# Drop all test databases (careful!)
psql -l | grep testdb_ | cut -d'|' -f1 | xargs -I {} dropdb {}
```

---

**Next**: Continue to [Part 3: CI/CD & Troubleshooting](testing-worktree-isolation-part3-cicd.md) to learn about CI/CD integration and troubleshooting common issues.
