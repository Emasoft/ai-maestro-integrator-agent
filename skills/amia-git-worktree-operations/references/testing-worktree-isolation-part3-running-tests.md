# Testing Worktrees: Running Tests in Isolation

## Table of Contents

1. [Unit Tests](#unit-tests)
2. [Integration Tests](#integration-tests)
3. [Performance Tests](#performance-tests)

---

## Unit Tests

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

---

## Integration Tests

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

---

## Performance Tests

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

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Types and Creation](testing-worktree-isolation-part1-types-and-creation.md)
- [Environment Setup](testing-worktree-isolation-part2-environment-setup.md)
- [Database Testing Patterns](testing-worktree-isolation-part4-database-testing.md)
