# Testing Worktrees: Environment Setup

## Table of Contents

1. [Installing Dependencies](#installing-dependencies)
2. [Database Setup for Tests](#database-setup-for-tests)
3. [Running Migrations](#running-migrations)
4. [Environment Configuration](#environment-configuration)
5. [Port Allocation for Services](#port-allocation-for-services)

---

## Installing Dependencies

**Why**: Each worktree needs its own dependencies to avoid conflicts.

**How to Install**:
```bash
# Navigate to test worktree
cd worktrees/test-integration-api-endpoints

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

**Automated Setup Script**:
```python
# scripts/setup_test_env.py
import os
import subprocess
import sys

def setup_test_environment(worktree_path):
    """Set up test environment in worktree"""

    # Create venv
    venv_path = os.path.join(worktree_path, '.venv')
    subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)

    # Get pip path
    pip = os.path.join(venv_path, 'bin', 'pip')

    # Install dependencies
    subprocess.run([pip, 'install', '-r', 'requirements.txt'],
                   cwd=worktree_path, check=True)
    subprocess.run([pip, 'install', '-r', 'requirements-test.txt'],
                   cwd=worktree_path, check=True)

    print(f"✓ Test environment ready: {worktree_path}")
```

---

## Database Setup for Tests

**Separate Database Per Worktree**:

Each test worktree should use its own database to ensure isolation.

**Naming Convention**:
```
testdb_<purpose>_<identifier>

Examples:
- testdb_integration_api_endpoints
- testdb_unit_user_model
- testdb_performance_queries
```

**Creating Test Database**:
```bash
# PostgreSQL example
createdb testdb_integration_api_endpoints

# MySQL example
mysql -e "CREATE DATABASE testdb_integration_api_endpoints;"
```

**Database Configuration in Test Worktree**:

Create `.env.test` file in worktree:
```bash
# .env.test
DATABASE_URL=postgresql://localhost/testdb_integration_api_endpoints
DATABASE_NAME=testdb_integration_api_endpoints
TEST_MODE=true
```

---

## Running Migrations

**Why Run Migrations in Test Worktrees**: Ensures database schema matches the code being tested.

**How to Run**:
```bash
# Navigate to test worktree
cd worktrees/test-integration-api-endpoints

# Activate virtual environment
source .venv/bin/activate

# Load test environment variables
export $(cat .env.test | xargs)

# Run migrations
python manage.py migrate  # Django example
alembic upgrade head      # SQLAlchemy example
```

---

## Environment Configuration

**Test-Specific Environment Variables**:

Create `.env.test` with test-appropriate values:
```bash
# .env.test - Example for integration test worktree

# Database
DATABASE_URL=postgresql://localhost/testdb_integration_api_endpoints

# Ports (from worktree metadata)
APP_PORT=8001
API_PORT=8002
DB_PORT=8003

# Test mode flags
TEST_MODE=true
DEBUG=true
LOG_LEVEL=DEBUG

# External services (use mocks in test)
PAYMENT_API_URL=http://localhost:9001/mock
EMAIL_BACKEND=console

# Disable external calls
SEND_EMAILS=false
CACHE_ENABLED=false
```

**Loading Environment**:
```bash
# In test worktree
source .venv/bin/activate
export $(cat .env.test | xargs)
```

---

## Port Allocation for Services

**Why Allocate Ports**: Multiple test worktrees running simultaneously need different ports.

**Port Allocation Strategy**:
- Each worktree gets 3 consecutive ports
- Ports start from configurable base (default: 8000)
- Tracked in `worktrees_registry.json`

**Example Port Assignment**:
```
Worktree 1: 8001, 8002, 8003
Worktree 2: 8004, 8005, 8006
Worktree 3: 8007, 8008, 8009
```

**Using Allocated Ports**:
```python
# Read ports from metadata
import json

with open('.worktree-metadata.json') as f:
    metadata = json.load(f)

app_port = metadata['ports']['app']
api_port = metadata['ports']['api']
db_port = metadata['ports']['db']

# Start services on allocated ports
uvicorn.run(app, host="0.0.0.0", port=app_port)
```

---

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Types and Creation](testing-worktree-isolation-part1-types-and-creation.md)
- [Running Tests](testing-worktree-isolation-part3-running-tests.md)
