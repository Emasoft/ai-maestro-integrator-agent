# Testing in Isolated Worktrees - Part 1: Fundamentals

## Table of Contents

1. [When you need to understand testing in isolated worktrees → Overview](#overview)
2. [If you need to understand worktree types for testing → Types of Testing Worktrees](#types-of-testing-worktrees)
   - [When running unit tests → Unit Test Worktrees](#unit-test-worktrees)
   - [If you need integration testing → Integration Test Worktrees](#integration-test-worktrees)
   - [When benchmarking performance → Performance Test Worktrees](#performance-test-worktrees)
   - [If you're validating before merge → Pre-Merge Validation Worktrees](#pre-merge-validation-worktrees)
3. [When you need to create test worktrees → Creating Test Worktrees](#creating-test-worktrees)
   - [If you're starting with basic setup → Basic Test Worktree Creation](#basic-test-worktree-creation)
   - [When you need test type examples → Examples for Different Test Types](#examples-for-different-test-types)
   - [If you want to understand creation process → What Happens During Creation](#what-happens-during-creation)
4. [When you need to set up test environment → Test Environment Setup](#test-environment-setup)
   - [If you're installing dependencies → Installing Dependencies](#installing-dependencies)
   - [When setting up test databases → Database Setup for Tests](#database-setup-for-tests)
   - [When configuring environment → Environment Configuration](#environment-configuration)
   - [If you need port allocation → Port Allocation for Services](#port-allocation-for-services)

**Related Documents**:
- [Part 2: Test Execution & Database Patterns](testing-worktree-isolation-part2-execution.md)
- [Part 3: CI/CD & Troubleshooting](testing-worktree-isolation-part3-cicd.md)

---

## Overview

**Purpose**: This document teaches you how to perform testing in isolated git worktrees.

**What is Testing in Isolated Worktrees**: Running tests in separate git worktrees so that each test environment is completely independent. Each worktree has its own:
- File system directory with checked-out code
- Virtual environment with dependencies
- Database instance (or database name)
- Network ports for services
- Environment variables and configuration

**Why Test in Isolated Worktrees**:
1. **Parallel Execution** - Run multiple test suites simultaneously without conflicts
2. **Branch Safety** - Test feature branches without switching your main working directory
3. **State Isolation** - Each test environment cannot interfere with others
4. **Clean Environment** - Start each test run with a pristine checkout
5. **CI/CD Simulation** - Replicate continuous integration behavior locally
6. **Version Comparison** - Test the same code against different dependency versions

**When to Use Isolated Test Worktrees**:
- Running integration tests that need dedicated ports
- Testing database migrations
- Performance testing that requires stable environment
- Pre-merge validation of pull requests
- Comparing test results across branches
- Matrix testing (multiple Python versions, dependency combinations)

---

## Types of Testing Worktrees

### Unit Test Worktrees

**What They Are**: Worktrees dedicated to running unit tests only.

**Characteristics**:
- Fast to set up (minimal dependencies)
- No external services needed
- Quick teardown
- Can run many in parallel

**Example Use Case**:
```bash
# Create unit test worktree for feature branch
python scripts/worktree_create.py \
    --purpose test-unit \
    --identifier api-validators \
    --branch feature/api-validators
```

### Integration Test Worktrees

**What They Are**: Worktrees with full service stack for integration testing.

**Characteristics**:
- Require database instance
- Need allocated network ports
- May need external service mocks
- Longer setup time

**Example Use Case**:
```bash
# Create integration test worktree with ports
python scripts/worktree_create.py \
    --purpose test-integration \
    --identifier payment-flow \
    --branch feature/payment-integration \
    --ports
```

### Performance Test Worktrees

**What They Are**: Worktrees configured for performance benchmarking.

**Characteristics**:
- Isolated from other processes
- Consistent resource allocation
- Monitoring and profiling enabled
- Long-running tests

**Example Use Case**:
```bash
# Create performance test worktree
python scripts/worktree_create.py \
    --purpose test-performance \
    --identifier query-optimization \
    --branch optimize/database-queries
```

### Pre-Merge Validation Worktrees

**What They Are**: Worktrees used to validate pull requests before merging.

**Characteristics**:
- Run full test suite
- Check for merge conflicts
- Validate against target branch
- Temporary (deleted after validation)

**Example Use Case**:
```bash
# Create pre-merge validation worktree
python scripts/worktree_create.py \
    --purpose test-premerge \
    --identifier pr-1234 \
    --branch feature/new-api
```

---

## Creating Test Worktrees

### Basic Test Worktree Creation

**Command Pattern**:
```bash
python scripts/worktree_create.py \
    --purpose <test-type> \
    --identifier <unique-name> \
    --branch <branch-name> \
    [--ports]
```

**Parameters Explained**:
- `--purpose` - Type of test worktree (test-unit, test-integration, test-performance, test-premerge)
- `--identifier` - Unique name for this test worktree (use ticket number, feature name, or test type)
- `--branch` - Which git branch to checkout
- `--ports` - Request port allocation for services (optional, needed for integration tests)

### Examples for Different Test Types

**Unit Tests** (no ports needed):
```bash
python scripts/worktree_create.py \
    --purpose test-unit \
    --identifier user-model \
    --branch main
```

**Integration Tests** (with ports):
```bash
python scripts/worktree_create.py \
    --purpose test-integration \
    --identifier api-endpoints \
    --branch feature/rest-api \
    --ports
```

**Performance Tests**:
```bash
python scripts/worktree_create.py \
    --purpose test-performance \
    --identifier load-testing \
    --branch optimize/caching
```

**Pre-Merge Validation**:
```bash
python scripts/worktree_create.py \
    --purpose test-premerge \
    --identifier pr-5678 \
    --branch feature/authentication
```

### What Happens During Creation

**Step-by-Step Process**:

1. **Directory Creation** - Creates worktree directory under `worktrees/`
2. **Git Checkout** - Checks out specified branch in new directory
3. **Metadata File** - Creates `.worktree-metadata.json` with configuration
4. **Port Allocation** - If `--ports` specified, allocates 3 consecutive ports
5. **Virtual Environment** - Sets up Python venv (optional, can be deferred)
6. **Registry Update** - Updates `worktrees_registry.json` with worktree info

**Example Metadata File** (`worktrees/test-integration-api-endpoints/.worktree-metadata.json`):
```json
{
    "purpose": "test-integration",
    "identifier": "api-endpoints",
    "branch": "feature/rest-api",
    "created": "2025-12-31T10:30:00Z",
    "ports": {
        "app": 8001,
        "api": 8002,
        "db": 8003
    },
    "database": "testdb_api_endpoints",
    "env_file": ".env.test-integration"
}
```

---

## Test Environment Setup

### Installing Dependencies

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

### Database Setup for Tests

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

### Running Migrations

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

### Environment Configuration

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

### Port Allocation for Services

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

**Next**: Continue to [Part 2: Test Execution & Database Patterns](testing-worktree-isolation-part2-execution.md) to learn about running tests and database testing patterns.
