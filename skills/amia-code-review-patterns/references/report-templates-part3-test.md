# Test Report Template

Template for documenting test execution results and analysis.

## Table of Contents

- [Template](#template)
  - [Test Results](#test-results)
  - [Failed Tests](#failed-tests)
  - [Skipped Tests](#skipped-tests)
  - [Slow Tests](#slow-tests)
  - [Coverage Impact](#coverage-impact)
  - [Next Actions](#next-actions)
- [Test Status Icons](#test-status-icons)
- [Result Summary Types](#result-summary-types)

---

## Template

```markdown
# Test Report
**Generated**: YYYY-MM-DD HH:MM:SS
**Test Suite**: [Full/Unit/Integration/E2E]
**Environment**: [Local/CI/Staging]

## Executive Summary
**Result**: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

- **Total Tests**: X
- **Passed**: Y (ZZ%)
- **Failed**: W
- **Skipped**: V
- **Errors**: U
- **Duration**: Xs

## Test Results

╔════════════════════════════════════════════════════════════╦═════════╦══════════╗
║ Test Function                                              ║ Status  ║ Duration ║
╠════════════════════════════════════════════════════════════╬═════════╬══════════╣
║ test_basic_initialization                                  ║ ✅ PASS ║ 0.12s    ║
║ test_configuration_loading                                 ║ ✅ PASS ║ 0.34s    ║
║ test_api_endpoint_health_check                             ║ ✅ PASS ║ 0.56s    ║
║ test_database_connection                                   ║ ❌ FAIL ║ 2.13s    ║
║ test_authentication_flow                                   ║ ✅ PASS ║ 1.45s    ║
║ test_edge_case_empty_input                                 ║ ✅ PASS ║ 0.08s    ║
║ test_edge_case_large_payload                               ║ ⚠️ SKIP  ║ -        ║
║ test_performance_benchmark_1000_requests 🐌                ║ ⏭️ SKIP  ║ -        ║
║ test_integration_external_api                              ║ ⚠️ ERROR ║ 5.00s    ║
╚════════════════════════════════════════════════════════════╩═════════╩══════════╝

## Failed Tests

### ❌ test_database_connection
**Description**: Verify database connection with retry logic

**Error**:
```

AssertionError: Expected connection status 'connected', got 'timeout'
  File "tests/test_database.py", line 45, in test_database_connection
    assert db.status == 'connected'

```

**Recommendation**: Check database service availability and timeout configuration.

---

### ⚠️ test_integration_external_api (ERROR)
**Description**: Test integration with external payment API

**Error**:
```

ConnectionError: External API unreachable at <https://api.example.com>
  File "tests/test_integration.py", line 78, in test_integration_external_api
    response = payment_api.charge(amount=100)

```

**Recommendation**: Ensure test environment has network access to external API.

---

## Skipped Tests

- **test_edge_case_large_payload**: Requires extended memory allocation (>2GB)
- **test_performance_benchmark_1000_requests** 🐌: Long-running test, skip in CI

## Slow Tests (>1s)

1. `test_integration_external_api` - 5.00s
2. `test_database_connection` - 2.13s
3. `test_authentication_flow` - 1.45s

**Recommendation**: Investigate optimization opportunities for slow tests.

## Coverage Impact

- **Lines Covered**: X (Y% of total)
- **Branches Covered**: W (Z% of total)

## Next Actions

- [ ] Fix database connection test timeout issue
- [ ] Investigate external API connection failure
- [ ] Investigate skipped test requirements
- [ ] Optimize slow tests

---
**Sources**: Test Execution Logs, Coverage Data
**Report ID**: test_YYYYMMDD_HHMMSS
**Log File**: tests/logs/test_run_YYYYMMDD_HHMMSS.log
```

---

## Test Status Icons

| Icon | Meaning |
|------|---------|
| ✅ PASS | Test passed successfully |
| ❌ FAIL | Test assertion failed |
| ⚠️ SKIP | Test skipped (conditional) |
| ⏭️ SKIP | Test skipped (slow/CI) |
| ⚠️ ERROR | Test had execution error |
| 🐌 | Slow test (usually skipped in CI) |

## Result Summary Types

| Result | Criteria |
|--------|----------|
| ✅ PASS | All tests passed |
| ⚠️ PARTIAL | Some tests skipped or minor failures |
| ❌ FAIL | Critical test failures |

---

**Back to [Report Templates Index](report-templates.md)**
