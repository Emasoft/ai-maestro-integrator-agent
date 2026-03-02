# Testing in Isolated Worktrees

## Table of Contents

- [Overview](#overview)
- [Document Map](#document-map)
  - [Part 1: Types and Creation](#part-1-types-and-creation)
  - [Part 2: Environment Setup](#part-2-environment-setup)
  - [Part 3: Running Tests](#part-3-running-tests)
  - [Part 4: Database Testing Patterns](#part-4-database-testing-patterns)
  - [Part 5: Cleanup After Tests](#part-5-cleanup-after-tests)
  - [Part 6: CI/CD Integration](#part-6-cicd-integration)
  - [Part 7: Troubleshooting and Summary](#part-7-troubleshooting-and-summary)
- [Quick Reference](#quick-reference)
  - [Essential Commands](#essential-commands)
  - [When to Use Each Worktree Type](#when-to-use-each-worktree-type)
- [Related Documents](#related-documents)

---

## Overview

**Purpose**: This document is the index for testing in isolated git worktrees.

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

## Document Map

This topic is split into multiple reference files for easier consumption. Read the sections relevant to your current task.

### Part 1: Types and Creation
**File**: [testing-worktree-isolation-part1-types-and-creation.md](testing-worktree-isolation-part1-types-and-creation.md)

**Read this when you need to**:
- Understand different types of test worktrees (unit, integration, performance, pre-merge)
- Create a new test worktree
- Know what parameters to use for creation
- Understand what happens during worktree creation

**Contents**:
- 1.1 Types of Testing Worktrees
  - 1.1.1 Unit Test Worktrees - fast setup, no external services
  - 1.1.2 Integration Test Worktrees - with database and ports
  - 1.1.3 Performance Test Worktrees - isolated benchmarking
  - 1.1.4 Pre-Merge Validation Worktrees - PR validation
- 1.2 Creating Test Worktrees
  - 1.2.1 Basic Test Worktree Creation command pattern
  - 1.2.2 Examples for Different Test Types
  - 1.2.3 What Happens During Creation (metadata, ports, registry)

---

### Part 2: Environment Setup
**File**: [testing-worktree-isolation-part2-environment-setup.md](testing-worktree-isolation-part2-environment-setup.md)

**Read this when you need to**:
- Install dependencies in a test worktree
- Set up a test database for a worktree
- Run database migrations in test context
- Configure environment variables for testing
- Allocate and use ports for services

**Contents**:
- 2.1 Installing Dependencies
  - 2.1.1 Manual venv creation and pip install
  - 2.1.2 Automated setup script example
- 2.2 Database Setup for Tests
  - 2.2.1 Naming convention for test databases
  - 2.2.2 Creating test databases (PostgreSQL, MySQL)
  - 2.2.3 Database configuration in .env.test
- 2.3 Running Migrations
- 2.4 Environment Configuration
  - 2.4.1 Test-specific environment variables
  - 2.4.2 Loading environment in worktree
- 2.5 Port Allocation for Services
  - 2.5.1 Port allocation strategy
  - 2.5.2 Using allocated ports from metadata

---

### Part 3: Running Tests
**File**: [testing-worktree-isolation-part3-running-tests.md](testing-worktree-isolation-part3-running-tests.md)

**Read this when you need to**:
- Run unit tests in an isolated worktree
- Run integration tests with services
- Run performance tests with profiling
- Write tests that use allocated ports

**Contents**:
- 3.1 Unit Tests
  - 3.1.1 Running unit tests in worktree
  - 3.1.2 Benefits of isolated unit test worktrees
- 3.2 Integration Tests
  - 3.2.1 Starting services on allocated ports
  - 3.2.2 Integration test example with port fixtures
  - 3.2.3 Stopping services after tests
- 3.3 Performance Tests
  - 3.3.1 Running with profiling
  - 3.3.2 Performance test example
  - 3.3.3 Why use isolated performance worktrees

---

### Part 4: Database Testing Patterns
**File**: [testing-worktree-isolation-part4-database-testing.md](testing-worktree-isolation-part4-database-testing.md)

**Read this when you need to**:
- Implement separate database per worktree pattern
- Test database migrations safely
- Test migration rollbacks
- Ensure data isolation between test runs

**Contents**:
- 4.1 Separate Database Per Worktree
  - 4.1.1 Implementation pattern
  - 4.1.2 Benefits of database isolation
- 4.2 Migration Testing
  - 4.2.1 Creating migration test worktree
  - 4.2.2 Setting up base database state
  - 4.2.3 Testing forward migration
  - 4.2.4 Testing backward migration
- 4.3 Rollback Testing
  - 4.3.1 Rollback test pattern with code example
- 4.4 Data Isolation
  - 4.4.1 Generating database name from worktree metadata
  - 4.4.2 Clean database fixture for test runs

---

### Part 5: Cleanup After Tests
**File**: [testing-worktree-isolation-part5-cleanup.md](testing-worktree-isolation-part5-cleanup.md)

**Read this when you need to**:
- Remove test worktrees after testing
- Automate cleanup of old test worktrees
- Release allocated ports
- Clean up test databases

**Contents**:
- 5.1 Removing Test Worktrees
  - 5.1.1 Manual removal command
  - 5.1.2 Automated removal script for old worktrees
- 5.2 Releasing Ports
  - 5.2.1 How ports are released automatically
  - 5.2.2 Manual port release script
- 5.3 Cleaning Test Databases
  - 5.3.1 Automated database cleanup
  - 5.3.2 Manual database cleanup commands

---

### Part 6: CI/CD Integration
**File**: [testing-worktree-isolation-part6-cicd.md](testing-worktree-isolation-part6-cicd.md)

**Read this when you need to**:
- Set up matrix testing with worktrees
- Run parallel test execution
- Collect test artifacts from worktrees
- Integrate worktree testing in GitHub Actions

**Contents**:
- 6.1 Matrix Testing with Worktrees
  - 6.1.1 What is matrix testing
  - 6.1.2 GitHub Actions matrix example (Python 3.9-3.12)
- 6.2 Parallel Test Execution
  - 6.2.1 Local parallel execution script
  - 6.2.2 GitHub Actions parallel jobs example
- 6.3 Artifact Collection
  - 6.3.1 Local artifact collection script
  - 6.3.2 GitHub Actions artifact upload

---

### Part 7: Troubleshooting and Summary
**File**: [testing-worktree-isolation-part7-troubleshooting.md](testing-worktree-isolation-part7-troubleshooting.md)

**Read this when you need to**:
- Fix test database connection failures
- Resolve port conflicts
- Fix virtual environment issues
- Handle migration state mismatches
- Clean up stale test worktrees
- Diagnose test interference problems

**Contents**:
- 7.1 Troubleshooting
  - 7.1.1 Test Database Connection Failures - check db exists, verify env var
  - 7.1.2 Port Conflicts - find process, kill, request new ports
  - 7.1.3 Virtual Environment Issues - verify venv, recreate, check version
  - 7.1.4 Migration State Mismatches - check status, reset, verify files
  - 7.1.5 Stale Test Worktrees - list, remove, cleanup old
  - 7.1.6 Test Interference - random order, separate db, separate worktrees
- 7.2 Summary
  - 7.2.1 Key takeaways
  - 7.2.2 When to use test worktrees
  - 7.2.3 Essential commands quick reference

---

## Quick Reference

### Essential Commands

**Create test worktree**:
```bash
python scripts/worktree_create.py \
    --purpose test-integration \
    --identifier my-test \
    --branch main \
    --ports
```

**Set up and run tests**:
```bash
cd worktrees/test-integration-my-test
source .venv/bin/activate
export $(cat .env.test | xargs)
pytest tests/integration/
```

**Cleanup**:
```bash
python scripts/worktree_remove.py --identifier my-test
```

### When to Use Each Worktree Type

| Type | Use When | Needs Ports | Needs Database |
|------|----------|-------------|----------------|
| `test-unit` | Running isolated function/class tests | No | No |
| `test-integration` | Testing multiple components together | Yes | Yes |
| `test-performance` | Benchmarking and profiling | Maybe | Maybe |
| `test-premerge` | Validating PR before merge | Yes | Yes |
| `test-migration` | Testing database schema changes | No | Yes |

---

## Related Documents

- [Worktree Management SKILL](../SKILL.md)
- [Worktree Creation Guide](creating-worktrees.md)
- [Worktree Lifecycle](worktree-operations-management.md)
