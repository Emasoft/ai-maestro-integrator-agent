---
procedure: proc-handle-failed-pr
workflow-instruction: "Step 22 - Handling Failed PRs"
operation: op-verify-fix-locally
description: "Verify CI fix locally before pushing to remote"
---

# Operation: Verify Fix Locally


## Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Check Environment Parity](#step-1-check-environment-parity)
  - [Step 2: Run Linting and Type Checks](#step-2-run-linting-and-type-checks)
  - [Step 3: Run Unit Tests](#step-3-run-unit-tests)
  - [Step 4: Simulate CI Environment (if possible)](#step-4-simulate-ci-environment-if-possible)
  - [Step 5: Test the Specific Fix](#step-5-test-the-specific-fix)
  - [Step 6: Run Full Test Suite](#step-6-run-full-test-suite)
- [Local Verification Checklist](#local-verification-checklist)
- [Output](#output)
- [Platform-Specific Verification](#platform-specific-verification)
  - [For Cross-Platform Fixes](#for-cross-platform-fixes)
  - [For Exit Code Fixes](#for-exit-code-fixes)
  - [For Syntax Fixes](#for-syntax-fixes)
- [Error Handling](#error-handling)
  - [Tests fail locally after fix](#tests-fail-locally-after-fix)
  - [Cannot replicate CI environment](#cannot-replicate-ci-environment)
  - [Tests pass locally but different versions](#tests-pass-locally-but-different-versions)
- [Next Operation](#next-operation)

## Purpose

This operation verifies that the applied CI fix works locally before pushing to trigger a new CI run. Local verification catches issues early and avoids wasting CI resources.

## Prerequisites

- Fix applied (see [op-apply-pattern-fix.md](op-apply-pattern-fix.md))
- Local development environment set up
- Same language runtime versions as CI

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| modified_files | list | Yes | Files that were modified |
| test_command | string | Yes | Command to run tests |
| ci_workflow | string | No | Path to CI workflow file |

## Procedure

### Step 1: Check Environment Parity

Verify your local environment matches CI:

```bash
# Check Python version
python3 --version
# Compare with workflow: grep "python-version" .github/workflows/*.yml

# Check Node version
node --version
# Compare with workflow: grep "node-version" .github/workflows/*.yml

# Check other tools
which ruff && ruff --version
which pytest && pytest --version
```

### Step 2: Run Linting and Type Checks

Run the same linting that CI runs:

```bash
# Python
ruff check .
mypy src/

# JavaScript/TypeScript
npx eslint .
npx tsc --noEmit

# Rust
cargo clippy

# Go
go vet ./...
```

### Step 3: Run Unit Tests

Execute the test suite:

```bash
# Python
pytest -v

# JavaScript
npm test

# Rust
cargo test

# Go
go test ./...
```

### Step 4: Simulate CI Environment (if possible)

For platform-specific fixes, try to simulate the CI environment:

**Using Docker (for Linux CI):**

```bash
# Run tests in Ubuntu container matching CI
docker run --rm -v $(pwd):/workspace -w /workspace python:3.11 \
  sh -c "pip install -e . && pytest"
```

**Using act (for GitHub Actions):**

```bash
# Install act: brew install act
# Run specific job
act -j test

# Dry run to see what would execute
act -n
```

**Using Windows VM/WSL (for Windows CI):**

```powershell
# In Windows/WSL
python -m pytest
```

### Step 5: Test the Specific Fix

Target the exact scenario that was failing:

```bash
# If the fix was for temp paths, run tests that use temp files
pytest -v -k "temp"

# If the fix was for imports, run the specific module
python -c "from mypackage.utils import helper; print('Import OK')"

# If the fix was for a shell script, run it
bash scripts/build.sh
```

### Step 6: Run Full Test Suite

After targeted tests pass, run the full suite:

```bash
# Run all tests with verbose output
pytest -v --tb=short

# Include coverage if CI checks coverage
pytest --cov=src --cov-report=term-missing
```

## Local Verification Checklist

Copy and use this checklist:

```markdown
- [ ] Environment versions match CI
- [ ] Linting passes (ruff/eslint/clippy)
- [ ] Type checking passes (mypy/tsc)
- [ ] Targeted test for fix passes
- [ ] Full test suite passes
- [ ] No new warnings introduced
```

## Output

| Output | Type | Description |
|--------|------|-------------|
| lint_status | boolean | Whether linting passed |
| test_status | boolean | Whether tests passed |
| coverage | number | Test coverage percentage (if applicable) |
| verification_summary | string | Summary of verification results |

## Platform-Specific Verification

### For Cross-Platform Fixes

Test on multiple platforms if possible:

| Platform | Method |
|----------|--------|
| Linux | Docker or native |
| macOS | Native |
| Windows | WSL, VM, or remote |

### For Exit Code Fixes

Verify exit codes explicitly:

```bash
# Run script and check exit code
./script.sh
echo "Exit code: $?"  # Should be 0

# Test failure handling
./script.sh --force-error || echo "Error handled correctly"
```

### For Syntax Fixes

Validate syntax without execution:

```bash
# Bash
bash -n script.sh

# Python
python3 -m py_compile script.py

# YAML
python3 -c "import yaml; yaml.safe_load(open('workflow.yml'))"
```

## Error Handling

### Tests fail locally after fix

If tests fail after applying the fix:

1. Check if the fix was applied correctly
2. Verify no typos or syntax errors
3. Check if additional changes are needed
4. Revert and re-apply: `git diff HEAD^ -- file.py`

### Cannot replicate CI environment

If you cannot match the CI environment:

1. Document what you verified locally
2. Note the platform differences
3. Consider adding CI matrix testing for multiple platforms
4. Push with awareness that CI may reveal additional issues

### Tests pass locally but different versions

If your local versions differ from CI:

```bash
# Use version managers to switch
pyenv install 3.11.0 && pyenv local 3.11.0
nvm use 18

# Or use Docker to match exactly
docker run --rm -v $(pwd):/app -w /app python:3.11-slim pytest
```

## Next Operation

After successful local verification:
- [op-push-and-monitor.md](op-push-and-monitor.md) - Push changes and monitor CI
