# Testing Worktrees: Types and Creation

## Table of Contents

1. [Types of Testing Worktrees](#types-of-testing-worktrees)
   - [Unit Test Worktrees](#unit-test-worktrees)
   - [Integration Test Worktrees](#integration-test-worktrees)
   - [Performance Test Worktrees](#performance-test-worktrees)
   - [Pre-Merge Validation Worktrees](#pre-merge-validation-worktrees)
2. [Creating Test Worktrees](#creating-test-worktrees)
   - [Basic Test Worktree Creation](#basic-test-worktree-creation)
   - [Examples for Different Test Types](#examples-for-different-test-types)
   - [What Happens During Creation](#what-happens-during-creation)

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

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Environment Setup](testing-worktree-isolation-part2-environment-setup.md)
- [Running Tests](testing-worktree-isolation-part3-running-tests.md)
