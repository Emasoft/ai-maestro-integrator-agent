# Exit Code CI Failure Patterns

## Table of Contents

- 2.1 Exit Code Persistence
  - 2.1.1 PowerShell $LASTEXITCODE behavior
  - 2.1.2 Bash $? behavior and pitfalls
  - 2.1.3 Solutions for reliable exit code handling
- 2.2 Common Exit Codes by Tool
  - 2.2.1 Git exit codes
  - 2.2.2 npm/yarn/pnpm exit codes
  - 2.2.3 pytest exit codes
  - 2.2.4 cargo exit codes
- 2.3 GitHub Actions Exit Code Handling
  - 2.3.1 Step failure detection
  - 2.3.2 continue-on-error behavior
  - 2.3.3 Custom exit code handling

---

## 2.1 Exit Code Persistence

Exit codes behave differently across shells. Understanding these differences prevents CI failures where the wrong exit code propagates.

### 2.1.1 PowerShell $LASTEXITCODE Behavior

PowerShell maintains `$LASTEXITCODE` separately from `$?`. This causes confusion:

| Variable | Contains | Persists Across |
|----------|----------|-----------------|
| `$LASTEXITCODE` | Exit code from last native command | Until next native command |
| `$?` | Success of last PowerShell command | Single command |

**Critical Issue**: `$LASTEXITCODE` persists until another native command runs.

**Example of the Problem**:
```powershell
# Native command fails
git status --invalid-option
# $LASTEXITCODE = 129

# PowerShell cmdlet succeeds (does NOT reset $LASTEXITCODE)
Write-Host "Continuing..."
# $LASTEXITCODE = 129 (still!)

# Script ends, GitHub Actions sees exit code 129
# WORKFLOW FAILS even though Write-Host succeeded
```

**CI Failure Symptom**: Workflow fails with unexpected exit code even though last visible command succeeded.

**Solution 1**: Explicit exit at end of script:
```powershell
# Always end PowerShell scripts with explicit exit
Write-Host "Script completed"
exit 0
```

**Solution 2**: Check and handle exit codes immediately:
```powershell
git status --invalid-option
if ($LASTEXITCODE -ne 0) {
    Write-Error "Git command failed with code $LASTEXITCODE"
    exit $LASTEXITCODE
}
```

**Solution 3**: Use `$ErrorActionPreference`:
```powershell
# Stop on any error
$ErrorActionPreference = "Stop"

# Or for native commands specifically
$PSNativeCommandUseErrorActionPreference = $true  # PowerShell 7.3+
```

### 2.1.2 Bash $? Behavior and Pitfalls

Bash's `$?` contains the exit code of the most recent command. It gets overwritten by every command.

**Critical Issue**: `$?` is overwritten immediately, even by `echo`.

**Example of the Problem**:
```bash
# Command fails
grep "pattern" nonexistent_file.txt
# $? = 2

# This echo OVERWRITES $? with 0
echo "Grep finished"
# $? = 0

# Script ends with exit code 0
# CI thinks script succeeded!
```

**Solution 1**: Capture exit code immediately:
```bash
grep "pattern" file.txt
exit_code=$?

echo "Grep finished with code: $exit_code"

if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi
```

**Solution 2**: Use `set -e` (exit on error):
```bash
#!/bin/bash
set -e  # Exit immediately if any command fails

grep "pattern" file.txt  # Script exits here if grep fails
echo "This only runs if grep succeeded"
```

**Solution 3**: Use `set -o pipefail` for pipelines:
```bash
#!/bin/bash
set -eo pipefail  # Exit on error, including in pipelines

# Without pipefail, only the last command's exit code matters
cat file.txt | grep "pattern" | wc -l
# With pipefail, if cat or grep fails, pipeline fails
```

**Recommended Bash Script Header**:
```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

### 2.1.3 Solutions for Reliable Exit Code Handling

**Cross-Platform Pattern**: Explicit error checking

```yaml
# GitHub Actions workflow
- name: Run with error checking
  shell: bash
  run: |
    set -eo pipefail

    # Each command explicitly checked
    if ! npm install; then
      echo "npm install failed"
      exit 1
    fi

    if ! npm test; then
      echo "npm test failed"
      exit 1
    fi

    echo "All commands succeeded"
    exit 0
```

**PowerShell Pattern**:
```yaml
- name: Run PowerShell with error checking
  shell: pwsh
  run: |
    $ErrorActionPreference = "Stop"

    try {
        npm install
        npm test
    } catch {
        Write-Error "Command failed: $_"
        exit 1
    }

    exit 0
```

---

## 2.2 Common Exit Codes by Tool

Understanding tool-specific exit codes helps diagnose CI failures quickly.

### 2.2.1 Git Exit Codes

| Exit Code | Meaning | Common Cause |
|-----------|---------|--------------|
| 0 | Success | Command completed normally |
| 1 | Generic error / Diff exists | `git diff --exit-code` found changes |
| 128 | Fatal error | Invalid repository, permission denied |
| 129 | Invalid option | Unknown flag or argument |

**CI Gotcha**: `git diff --exit-code` returns 1 if differences exist (by design).

```yaml
# WRONG: This fails if there are unstaged changes
- run: git diff --exit-code

# CORRECT: Only check if needed
- run: |
    if git diff --exit-code; then
      echo "No changes"
    else
      echo "Changes detected, committing..."
      git add .
      git commit -m "Auto-commit changes"
    fi
```

### 2.2.2 npm/yarn/pnpm Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Generic failure |
| 2 | Invalid argument / command not found |
| 127 | Command not found (shell level) |

**npm-specific behavior**: `npm test` exit code comes from the test runner.

```bash
# npm test returns the exit code of the underlying test command
npm test  # Exit code = exit code of "jest" or "mocha" etc.
```

**CI Gotcha**: `npm ci` fails if `package-lock.json` is out of sync.

```yaml
# CORRECT: Use npm ci for reproducible builds
- run: npm ci

# WRONG: npm install may modify package-lock.json
- run: npm install
```

### 2.2.3 pytest Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | All tests passed |
| 1 | Some tests failed |
| 2 | Test execution interrupted |
| 3 | Internal error |
| 4 | pytest command line usage error |
| 5 | No tests collected |

**CI Gotcha**: Exit code 5 (no tests) often indicates a configuration problem.

```yaml
# Check for "no tests collected" specifically
- name: Run tests
  run: |
    pytest tests/ || exit_code=$?

    if [ "$exit_code" = "5" ]; then
      echo "ERROR: No tests were collected!"
      echo "Check pytest configuration and test discovery"
      exit 1
    fi

    exit ${exit_code:-0}
```

### 2.2.4 cargo Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Build/test failure |
| 101 | Compilation error |

**Cargo-specific behavior**: Compilation warnings don't affect exit code unless `--deny warnings`.

```yaml
# Fail on warnings in CI
- run: cargo build --release
  env:
    RUSTFLAGS: "-D warnings"

# Or use clippy
- run: cargo clippy -- -D warnings
```

---

## 2.3 GitHub Actions Exit Code Handling

### 2.3.1 Step Failure Detection

GitHub Actions considers a step failed when:
1. Exit code is non-zero
2. The `shell` returns non-zero

```yaml
jobs:
  build:
    steps:
      - name: This step fails the job
        run: exit 1
        # Job stops here by default

      - name: This never runs
        run: echo "Skipped"
```

### 2.3.2 continue-on-error Behavior

Use `continue-on-error: true` to prevent step failure from failing the job:

```yaml
- name: Optional step
  continue-on-error: true
  run: |
    # This might fail, but job continues
    npm run optional-check

- name: Check previous step result
  run: |
    # steps.*.outcome is 'success' or 'failure'
    echo "Previous step: ${{ steps.optional.outcome }}"
```

**Important**: The step is still marked as failed (red X), but the job continues.

**Access step outcome**:
```yaml
- name: Optional check
  id: optional
  continue-on-error: true
  run: npm run lint

- name: Handle lint results
  if: steps.optional.outcome == 'failure'
  run: echo "Lint failed but continuing..."
```

### 2.3.3 Custom Exit Code Handling

**Pattern 1**: Capture and handle specific exit codes:

```yaml
- name: Run with exit code handling
  id: mycommand
  run: |
    ./my-script.sh || exit_code=$?

    case $exit_code in
      0) echo "Success" ;;
      1) echo "::warning::Minor issue detected" ;;
      2) echo "::error::Critical error"; exit 2 ;;
      *) echo "Unknown exit code: $exit_code"; exit $exit_code ;;
    esac
```

**Pattern 2**: Set output based on exit code:

```yaml
- name: Check condition
  id: check
  run: |
    if ./check-something.sh; then
      echo "result=passed" >> $GITHUB_OUTPUT
    else
      echo "result=failed" >> $GITHUB_OUTPUT
    fi
  continue-on-error: true

- name: React to check
  if: steps.check.outputs.result == 'failed'
  run: echo "Check failed, taking action..."
```

**Pattern 3**: Matrix job with different exit code handling:

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        allow_failure: false
      - os: windows-latest
        allow_failure: true

steps:
  - name: Run tests
    continue-on-error: ${{ matrix.allow_failure }}
    run: npm test
```

---

## Summary: Exit Code Checklist

Before committing CI workflows:

- [ ] PowerShell scripts end with explicit `exit 0`
- [ ] Bash scripts use `set -eo pipefail`
- [ ] Exit codes are captured immediately after commands
- [ ] Tool-specific exit codes are documented and handled
- [ ] `continue-on-error` used intentionally with outcome checking
- [ ] Pipelines propagate errors correctly
- [ ] `git diff --exit-code` behavior is handled
- [ ] "No tests collected" (pytest 5) is caught
