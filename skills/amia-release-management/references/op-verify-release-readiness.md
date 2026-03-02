---
name: op-verify-release-readiness
description: "Run pre-release verification checklist to confirm release readiness"
procedure: support-skill
workflow-instruction: support
---

# Operation: Verify Release Readiness


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify all tests pass](#step-1-verify-all-tests-pass)
  - [Step 2: Check for critical bugs](#step-2-check-for-critical-bugs)
  - [Step 3: Verify documentation updated](#step-3-verify-documentation-updated)
  - [Step 4: Check dependency vulnerabilities](#step-4-check-dependency-vulnerabilities)
  - [Step 5: Check CI/CD status](#step-5-check-cicd-status)
  - [Step 6: Check for breaking changes (if major release)](#step-6-check-for-breaking-changes-if-major-release)
  - [Step 7: Generate verification report](#step-7-generate-verification-report)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Quality Gates](#quality-gates)
- [Error Handling](#error-handling)
  - [Tests fail](#tests-fail)
  - [Critical bugs open](#critical-bugs-open)
  - [CI not available](#ci-not-available)
- [Verification Script](#verification-script)

## Purpose

Execute a comprehensive pre-release verification checklist to ensure all quality gates pass before approving a release.

## When to Use

- Before any release is approved
- When uncertain if code is ready for release
- After receiving a release request from orchestrator

## Prerequisites

1. Access to repository test suite
2. Access to CI/CD status
3. GitHub CLI authenticated
4. Understanding of required quality gates

## Procedure

### Step 1: Verify all tests pass

```bash
# Run test suite
echo "Running test suite..."
TEST_RESULT=$(npm test 2>&1) || TEST_RESULT=$(pytest 2>&1)
TEST_EXIT=$?

if [ $TEST_EXIT -eq 0 ]; then
  echo "PASS: All tests pass"
  TESTS_PASS=true
else
  echo "FAIL: Tests failed"
  echo "$TEST_RESULT" | tail -20
  TESTS_PASS=false
fi
```

### Step 2: Check for critical bugs

```bash
# Check for open critical/blocker issues
CRITICAL_BUGS=$(gh issue list --label "critical,blocker,bug" --state open --json number --jq 'length')

if [ "$CRITICAL_BUGS" -eq 0 ]; then
  echo "PASS: No critical bugs open"
  NO_CRITICAL_BUGS=true
else
  echo "FAIL: $CRITICAL_BUGS critical bugs open"
  gh issue list --label "critical,blocker,bug" --state open --json number,title --jq '.[] | "#\(.number): \(.title)"'
  NO_CRITICAL_BUGS=false
fi
```

### Step 3: Verify documentation updated

```bash
# Check CHANGELOG.md was updated
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
  CHANGELOG_CHANGED=$(git diff "$LAST_TAG"..HEAD --name-only | grep -c "CHANGELOG.md" || echo "0")
else
  CHANGELOG_CHANGED=$(git log --name-only --oneline | grep -c "CHANGELOG.md" || echo "0")
fi

if [ "$CHANGELOG_CHANGED" -gt 0 ]; then
  echo "PASS: CHANGELOG.md updated"
  DOCS_UPDATED=true
else
  echo "WARN: CHANGELOG.md not updated"
  DOCS_UPDATED=false
fi
```

### Step 4: Check dependency vulnerabilities

```bash
# For npm projects
if [ -f "package.json" ]; then
  AUDIT_RESULT=$(npm audit --json 2>/dev/null)
  HIGH_VULNS=$(echo "$AUDIT_RESULT" | jq '.metadata.vulnerabilities.high // 0')
  CRITICAL_VULNS=$(echo "$AUDIT_RESULT" | jq '.metadata.vulnerabilities.critical // 0')

  if [ "$HIGH_VULNS" -eq 0 ] && [ "$CRITICAL_VULNS" -eq 0 ]; then
    echo "PASS: No high/critical vulnerabilities"
    DEPS_CLEAN=true
  else
    echo "FAIL: Found $HIGH_VULNS high, $CRITICAL_VULNS critical vulnerabilities"
    DEPS_CLEAN=false
  fi
fi

# For Python projects
if [ -f "requirements.txt" ]; then
  SAFETY_RESULT=$(safety check --json 2>/dev/null || echo "[]")
  VULN_COUNT=$(echo "$SAFETY_RESULT" | jq 'length')

  if [ "$VULN_COUNT" -eq 0 ]; then
    echo "PASS: No known vulnerabilities"
    DEPS_CLEAN=true
  else
    echo "WARN: Found $VULN_COUNT vulnerabilities"
    DEPS_CLEAN=false
  fi
fi
```

### Step 5: Check CI/CD status

```bash
# Get latest CI run status
CI_STATUS=$(gh run list --limit 1 --json status,conclusion --jq '.[0]')
CI_CONCLUSION=$(echo "$CI_STATUS" | jq -r '.conclusion')

if [ "$CI_CONCLUSION" = "success" ]; then
  echo "PASS: CI pipeline passed"
  CI_PASS=true
else
  echo "FAIL: CI pipeline status: $CI_CONCLUSION"
  CI_PASS=false
fi
```

### Step 6: Check for breaking changes (if major release)

```bash
RELEASE_TYPE="${1:-minor}"

if [ "$RELEASE_TYPE" = "major" ]; then
  # Check for migration guide
  if [ -f "MIGRATION.md" ] || grep -q "migration" README.md; then
    echo "PASS: Migration guide present"
    MIGRATION_READY=true
  else
    echo "FAIL: Major release requires migration guide"
    MIGRATION_READY=false
  fi
fi
```

### Step 7: Generate verification report

```bash
# Determine overall readiness
if [ "$TESTS_PASS" = true ] && [ "$NO_CRITICAL_BUGS" = true ] && [ "$CI_PASS" = true ]; then
  READY=true
  READY_STATUS="READY_FOR_RELEASE"
else
  READY=false
  READY_STATUS="BLOCKED"
fi

# Build report
cat << EOF
{
  "version": "$VERSION",
  "ready": $READY,
  "status": "$READY_STATUS",
  "gates": {
    "tests_pass": {"status": "$TESTS_PASS", "details": "Test suite result"},
    "no_critical_bugs": {"status": "$NO_CRITICAL_BUGS", "details": "$CRITICAL_BUGS critical issues"},
    "docs_updated": {"status": "$DOCS_UPDATED", "details": "CHANGELOG status"},
    "dependencies_clean": {"status": "${DEPS_CLEAN:-true}", "details": "Vulnerability scan"},
    "ci_pass": {"status": "$CI_PASS", "details": "CI pipeline status"}
  },
  "blockers": []
}
EOF
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version | string | yes | Version being verified |
| release_type | string | no | Type: patch, minor, major |
| skip_tests | boolean | no | Skip test execution (use CI result) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| version | string | Version being verified |
| ready | boolean | Overall readiness status |
| status | string | READY_FOR_RELEASE or BLOCKED |
| gates | object | Individual gate results |
| blockers | string[] | List of blocking issues |

## Example Output

```json
{
  "version": "1.2.4",
  "ready": true,
  "status": "READY_FOR_RELEASE",
  "gates": {
    "tests_pass": {"status": true, "details": "142 tests passed"},
    "no_critical_bugs": {"status": true, "details": "0 critical issues"},
    "docs_updated": {"status": true, "details": "CHANGELOG.md updated"},
    "dependencies_clean": {"status": true, "details": "No vulnerabilities"},
    "ci_pass": {"status": true, "details": "All workflows passed"}
  },
  "blockers": []
}
```

## Quality Gates

| Gate | Blocking | Description |
|------|----------|-------------|
| tests_pass | Yes | All tests must pass |
| no_critical_bugs | Yes | No critical/blocker bugs open |
| ci_pass | Yes | CI pipeline must pass |
| docs_updated | No (warn) | CHANGELOG should be updated |
| dependencies_clean | No (warn) | No high/critical vulnerabilities |
| migration_ready | Yes (major) | Major releases need migration guide |

## Error Handling

### Tests fail

**Cause**: Test suite has failures.

**Solution**: Fix failing tests before release.

### Critical bugs open

**Cause**: Unresolved critical issues.

**Solution**: Close or downgrade issues, or delay release.

### CI not available

**Cause**: Cannot check CI status.

**Solution**: Run tests locally, verify manually.

## Verification Script

```bash
#!/bin/bash
# verify_release_readiness.sh

VERSION="$1"
RELEASE_TYPE="${2:-patch}"

echo "=== Release Readiness Verification ==="
echo "Version: $VERSION"
echo "Type: $RELEASE_TYPE"
echo ""

BLOCKERS=()

# Gate 1: Tests
if npm test >/dev/null 2>&1 || pytest >/dev/null 2>&1; then
  echo "[PASS] Tests"
else
  echo "[FAIL] Tests"
  BLOCKERS+=("Tests failing")
fi

# Gate 2: Critical bugs
BUGS=$(gh issue list --label "critical,blocker" --state open --json number | jq 'length')
if [ "$BUGS" -eq 0 ]; then
  echo "[PASS] No critical bugs"
else
  echo "[FAIL] $BUGS critical bugs"
  BLOCKERS+=("$BUGS critical bugs open")
fi

# Gate 3: CI
CI=$(gh run list --limit 1 --json conclusion --jq '.[0].conclusion')
if [ "$CI" = "success" ]; then
  echo "[PASS] CI pipeline"
else
  echo "[FAIL] CI: $CI"
  BLOCKERS+=("CI pipeline failed")
fi

# Summary
echo ""
if [ ${#BLOCKERS[@]} -eq 0 ]; then
  echo "STATUS: READY_FOR_RELEASE"
else
  echo "STATUS: BLOCKED"
  echo "Blockers:"
  for b in "${BLOCKERS[@]}"; do
    echo "  - $b"
  done
fi
```
