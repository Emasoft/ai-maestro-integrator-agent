# PR Evaluator Scenarios and Troubleshooting

This document covers common scenarios, troubleshooting guides, and best practices for the pr-evaluator agent.

## Table of Contents

- Common Scenarios
  - Scenario 1: All Tests Pass
  - Scenario 2: Minor Issues Only
  - Scenario 3: Critical Test Failures
  - Scenario 4: Performance Regression
  - Scenario 5: Insufficient Test Coverage
- Troubleshooting
  - Worktree Creation Fails
  - Tests Fail Due to Missing Dependencies
  - Tests Require External Services
  - Cannot Parse Test Output
  - Tests Appear Stuck or Hanging
- Best Practices

---

## Common Scenarios

### Scenario 1: All Tests Pass

```
VERDICT: APPROVE

All checks passed:
- 150/150 tests passed
- Build successful
- No linting issues
- No type errors
- No security findings
- Coverage: 89.1% (+3.3%)

RECOMMENDATION: PR is ready to merge
```

### Scenario 2: Minor Issues Only

```
VERDICT: APPROVE (with minor issues noted)

Tests: 150/150 passed
Build: Success
Linting: 2 minor issues (line length, missing type hint)
Coverage: 86.5% (+1.2%)

RECOMMENDATION: Approve with suggestion to fix linting in follow-up
```

### Scenario 3: Critical Test Failures

```
VERDICT: REJECT

Tests: 87/150 passed (63 failures)
Build: Failed
Linting: 15 issues
Type errors: 7

CRITICAL ISSUES:
- Build fails due to import errors
- 63 tests failing across multiple modules
- Suggests PR was not tested locally before submission

RECOMMENDATION: Reject and request PR author test locally first
```

### Scenario 4: Performance Regression

```
VERDICT: REQUEST CHANGES

Tests: 150/150 passed
Build: Success
Performance: REGRESSION DETECTED

ISSUE: Integration test suite duration increased from 45s to 8m 32s
Likely cause: N+1 query problem in new API endpoint

RECOMMENDATION: Request optimization before merge
```

### Scenario 5: Insufficient Test Coverage

```
VERDICT: REQUEST CHANGES

Tests: 150/150 passed
Build: Success
Coverage: 72.3% (-5.1% from base)

ISSUE: New code in src/auth/token_manager.py has only 45% coverage
Critical security code insufficiently tested

RECOMMENDATION: Request additional tests for new authentication logic
```

---

## Troubleshooting

### Issue: Worktree Creation Fails

```
Error: fatal: 'pull/123/head' is not a commit

Solution:
1. Fetch PR refs first:
   git fetch origin pull/123/head:pr-123
2. Then create worktree:
   git worktree add /tmp/pr-eval-123 pr-123
```

### Issue: Tests Fail Due to Missing Dependencies

```
Error: ModuleNotFoundError: No module named 'pytest'

Solution:
1. Ensure dependency installation in evaluation environment:
   cd /tmp/pr-eval-123
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
2. Then run tests
```

### Issue: Tests Require External Services

```
Error: ConnectionRefusedError: [Errno 61] Connection refused (PostgreSQL)

Solution:
1. Start required services in evaluation environment:
   docker-compose up -d postgres redis
2. Wait for services to be ready:
   docker-compose exec postgres pg_isready
3. Then run tests
```

### Issue: Cannot Parse Test Output

```
Error: Test log format unrecognized

Solution:
1. Use structured output formats:
   pytest --junitxml=results.xml
2. Parse XML instead of text logs
3. Use pytest-json-report for JSON output
```

### Issue: Tests Appear Stuck or Hanging

```
Issue: Test suite produces no output, appears non-responsive

Solution:
1. Check for hanging tests (infinite loops, blocked I/O, deadlocks)
2. Monitor test progress - if no new output after significant test completion, interrupt:
   - Check if pytest process is consuming CPU (active loop) or idle (blocked)
   - Check for open network connections or file handles
3. If tests are unresponsive, report as evaluation failure with evidence
4. Suggest PR author investigate hanging tests (provide last completed test name)
```

---

## Best Practices

### 1. Always Use Isolated Environments
Never evaluate PRs in main working directory. Always use worktrees, containers, or dedicated clones.

### 2. Collect Complete Evidence
Capture all logs, outputs, and reports. Future debugging may require this evidence.

### 3. Be Deterministic
Same PR should produce same evaluation results. Ensure environment consistency.

### 4. Report Objectively
Stick to facts. No speculation, no opinions, no implementation suggestions.

### 5. Compare with Baseline
When possible, compare PR results with base branch results to identify regressions.

### 6. Detect Hanging Tests
Monitor test progress for responsiveness. Non-progressing tests indicate PR issues.

### 7. Clean Up Thoroughly
Always remove evaluation environments after completion to avoid disk space issues.

### 8. Version Your Reports
Include timestamps, commit SHAs, and environment details in reports for reproducibility.
