# PR Evaluation Methodology

## Contents

- 1.0 When to evaluate a PR for merge readiness
- 2.0 Evaluation gates that must pass before approval
  - 2.1 Gate 0: Requirement Compliance (verifying PR implements what user requested)
  - 2.2 Gate 0.5: TDD Compliance (verifying test-first development workflow)
  - 2.3 Gate 1: Comprehensive Test Execution
  - 2.4 Gate 2: Quality and Security Checks
  - 2.5 Gate 3: Build Verification
- 3.0 Evidence requirements for objective evaluation
  - 3.1 What constitutes valid evidence
  - 3.2 What to document for each failure
- 4.0 Verdict decision criteria
  - 4.1 Automatic rejection triggers
  - 4.2 APPROVE criteria
  - 4.3 REQUEST CHANGES criteria
  - 4.4 REJECT criteria
- 5.0 Structured reporting requirements
  - 5.1 Report format and required sections
  - 5.2 Structured data output format

---

## 1.0 When to evaluate a PR for merge readiness

Evaluate a PR when:

- **A PR is marked as ready for review** - Author has completed development and requests evaluation
- **Orchestrator assigns PR evaluation task** - As part of automated PR review workflow
- **Code changes need quality assessment before merge** - To verify functional correctness
- **Re-evaluation is requested after fixes** - PR author pushed updates addressing previous issues
- **Automated CI/CD triggers evaluation** - Integration with continuous integration pipeline
- **Manual review is requested** - Team member requests comprehensive test verification
- **Merge readiness check is needed** - Before final approval and merge to main branch

---

## 2.0 Evaluation gates that must pass before approval

PR evaluation follows a **sequential gate system**. Each gate must pass before proceeding to the next.

### 2.1 Gate 0: Requirement Compliance (verifying PR implements what user requested)

**Purpose:** Verify that the PR actually implements what the user requested, not something else.

**CRITICAL:** This gate is executed **BEFORE** all other gates. No point in testing code that doesn't meet requirements.

#### Gate 0 Procedure

**Step 1:** Load `USER_REQUIREMENTS.md` from project root or handoff document

**Step 2:** Compare PR scope against user requirements

- What did the user ask for?
- What does this PR deliver?
- Are they the same thing?

**Step 3:** Check for deviations

- Technology substitutions (user said Node.js, PR uses Python)
- Feature omissions (user requested feature X, PR doesn't include it)
- Scope creep (PR adds features user didn't request)
- Simplifications (PR implements "simpler alternative" without approval)

#### Automatic Rejection Triggers (Gate 0)

**REJECT IMMEDIATELY if:**

❌ User said "build X" but PR builds "Y" instead
❌ User specified technology A but PR uses technology B without approval
❌ PR removes/skips features user explicitly requested
❌ PR implements "simpler alternative" without user approval
❌ PR changes core requirements without documented approval

**Verdict:** `REJECT - Requirement Deviation`

**Required evidence:**

- Quote from USER_REQUIREMENTS.md showing what was requested
- Description of what PR actually delivers
- Specific deviations identified

---

### 2.2 Gate 0.5: TDD Compliance (verifying test-first development workflow)

**Purpose:** Verify that the PR followed Test-Driven Development workflow.

**THE IRON LAW:** No production code without a failing test first.

#### Gate 0.5 Procedure

**Step 1:** Verify RED Commit Exists

```bash
git log --oneline origin/main..HEAD | grep "^[a-f0-9]* RED:"
```

Expected: At least one commit with "RED:" prefix showing failing test

**Step 2:** Verify GREEN Commit Exists

```bash
git log --oneline origin/main..HEAD | grep "^[a-f0-9]* GREEN:"
```

Expected: At least one commit with "GREEN:" prefix showing passing implementation

**Step 3:** Verify Correct Sequence

```bash
git log --oneline origin/main..HEAD
```

Expected: RED commit appears BEFORE corresponding GREEN commit

**Step 4:** Verify Tests Pass

```bash
uv run pytest tests/ -v
```

Expected: All tests pass (exit code 0)

#### Automatic Rejection Triggers (Gate 0.5)

**REJECT IMMEDIATELY if:**

❌ No RED commit found (test was not written first)
❌ No GREEN commit found (implementation is missing)
❌ GREEN commit appears before RED commit (wrong sequence)
❌ Tests fail on GREEN commit (TDD cycle incomplete)

**Verdict:** `REJECT - TDD Workflow Violation`

**Required evidence:**

- Git log showing commit sequence
- Identification of which TDD step is missing or out of order

---

### 2.3 Gate 1: Comprehensive Test Execution

**Purpose:** Run ALL available tests to verify functional correctness.

#### Test Categories to Execute

**MANDATORY - Run ALL of these:**

1. **Unit tests** - Test individual functions/methods in isolation
2. **Integration tests** - Test component interactions
3. **End-to-end tests** - Test full user workflows
4. **Performance tests** (if applicable) - Test speed, memory, throughput
5. **Linting and formatting checks** - Code style compliance
6. **Type checking** - Static type verification
7. **Security scans** - Vulnerability detection
8. **Build verification** - Successful compilation/bundling

#### Test Execution Rules

**DO:**
✅ Run ALL available tests (no skipping)
✅ Collect ALL failures (don't stop at first failure)
✅ Capture full output logs
✅ Record exit codes
✅ Measure execution time
✅ Check test coverage percentage

**DO NOT:**
❌ Skip tests to save time
❌ Stop at first failure
❌ Ignore flaky tests
❌ Run only unit tests
❌ Skip expensive integration tests

#### Test Execution Commands

```bash
# Unit + Integration + E2E tests
uv run pytest tests/ --verbose --tb=long --junitxml=test-results.xml \
  --cov=src --cov-report=html 2>&1 | tee test-execution.log
echo $? > test-exit-code.txt

# Linting
uv run ruff check src/ tests/ | tee lint-report.log

# Type checking
uv run mypy src/ | tee typecheck-report.log

# Security scan
trufflehog git file://. --since-commit HEAD~1 | tee security-scan.log

# Build verification
uv build | tee build-report.log
```

---

### 2.4 Gate 2: Quality and Security Checks

**Purpose:** Verify code quality standards and security compliance.

#### Quality Dimensions

1. **Code Style Compliance**
   - Tool: `ruff check`
   - Threshold: Zero violations
   - Evidence: lint-report.log

2. **Type Safety**
   - Tool: `mypy`
   - Threshold: Zero type errors
   - Evidence: typecheck-report.log

3. **Security Vulnerabilities**
   - Tool: `trufflehog`, `bandit`, etc.
   - Threshold: Zero high/critical findings
   - Evidence: security-scan.log

4. **Test Coverage**
   - Tool: pytest with `--cov`
   - Threshold: ≥80% line coverage (project-specific)
   - Evidence: coverage report HTML

---

### 2.5 Gate 3: Build Verification

**Purpose:** Verify that the code builds successfully.

#### Build Requirements

- **Build command succeeds** (exit code 0)
- **No build warnings** (or documented exceptions)
- **Artifacts are generated** (binaries, wheels, bundles)
- **Dependencies resolve** (no conflicts)

#### Build Verification Commands

```bash
# Python project
uv build | tee build-report.log
echo $? > build-exit-code.txt

# Node.js project
npm run build | tee build-report.log

# Rust project
cargo build --release | tee build-report.log
```

---

## 3.0 Evidence requirements for objective evaluation

### 3.1 What constitutes valid evidence

**Valid evidence is:**

- **Specific** - Names the exact test, file, line number
- **Reproducible** - Includes steps to reproduce
- **Objective** - States facts, not opinions
- **Complete** - Includes full error messages and stack traces

**Example of VALID evidence:**

```
Test: test_user_login (tests/auth/test_login.py:42)
Expected: HTTP 200 with auth token
Actual: HTTP 401 Unauthorized
Error: AssertionError: expected status 200, got 401
Stack trace: [full trace]
```

**Example of INVALID evidence:**

```
The login test failed.
```

### 3.2 What to document for each failure

For **every** test failure, quality violation, or build error, document:

1. **Identifier** - Test name, check name, or error type
2. **Location** - File path and line number
3. **Expected outcome** - What should have happened
4. **Actual outcome** - What actually happened
5. **Error message** - Full error text
6. **Stack trace** - Complete traceback (if applicable)
7. **Reproduction steps** - How to trigger the failure
8. **Relevant logs** - Excerpts from execution logs

---

## 4.0 Verdict decision criteria

### 4.1 Automatic rejection triggers

**REJECT immediately if ANY of these are true:**

| Trigger | Evidence Required | Verdict |
|---------|-------------------|---------|
| Requirement deviation | USER_REQUIREMENTS.md vs PR scope comparison | REJECT - Requirement Deviation |
| TDD workflow violation | Git log showing missing/wrong commit sequence | REJECT - TDD Workflow Violation |
| Critical security vulnerability | Security scan report | REJECT - Security Issue |
| Build failure | Build log with error | REJECT - Build Failed |
| Zero tests | Test execution log | REJECT - No Tests |

### 4.2 APPROVE criteria

**Verdict: APPROVE**

All of the following must be true:

✅ Gate 0 passed - Requirement compliance verified
✅ Gate 0.5 passed - TDD workflow verified
✅ All tests passed (unit, integration, e2e, performance)
✅ Zero lint violations
✅ Zero type errors
✅ Zero high/critical security findings
✅ Test coverage ≥ threshold (typically 80%)
✅ Build succeeded
✅ No regressions detected

**Example verdict:**

```
VERDICT: APPROVE

SUMMARY:
- Tests: 150/150 passed
- Coverage: 87.3%
- Lint: 0 violations
- Type check: 0 errors
- Security: 0 findings
- Build: Success

Ready for merge.
```

### 4.3 REQUEST CHANGES criteria

**Verdict: REQUEST CHANGES**

Use this verdict when:

⚠️ Some tests fail (not all)
⚠️ Minor lint violations (style issues)
⚠️ Coverage below threshold but tests pass
⚠️ Non-critical security findings
⚠️ Performance regression detected
⚠️ Missing documentation

**Example verdict:**

```
VERDICT: REQUEST CHANGES

SUMMARY:
- Tests: 142/150 passed (8 failures)
- Failed tests: auth module (login, logout, token refresh)
- Coverage: 79.2% (below 80% threshold)
- Lint: 3 violations (unused imports)
- Type check: 0 errors
- Security: 1 low-severity finding
- Build: Success

Action required: Fix 8 failing auth tests, remove unused imports.
```

### 4.4 REJECT criteria

**Verdict: REJECT**

Use this verdict when:

❌ Requirement deviation (Gate 0 failure)
❌ TDD workflow violation (Gate 0.5 failure)
❌ Critical security vulnerability
❌ Build failure
❌ Zero tests present
❌ Majority of tests fail (>50%)
❌ Fundamental design flaws

**Example verdict:**

```
VERDICT: REJECT

REASON: TDD Workflow Violation

EVIDENCE:
Git log shows no RED commit. Production code was written without
writing a failing test first, violating TDD workflow requirement.

ACTION: Close PR. Author must restart with proper TDD workflow.
```

---

## 5.0 Structured reporting requirements

### 5.1 Report format and required sections

**Write report to:** `pr-evaluation-report-${PR_NUMBER}.md`

**Required sections:**

```markdown
# PR Evaluation Report: #${PR_NUMBER}

**PR Title:** [title]
**Author:** [author]
**Branch:** [branch]
**Evaluated:** [timestamp]
**Evaluator:** amia-pr-evaluator

---

## Verdict

**APPROVE** | **REQUEST CHANGES** | **REJECT**

[One-sentence summary of verdict]

---

## Evaluation Summary

| Dimension | Status | Details |
|-----------|--------|---------|
| Requirement Compliance | PASS/FAIL | [brief result] |
| TDD Compliance | PASS/FAIL | [brief result] |
| Unit Tests | X/Y passed | [failures] |
| Integration Tests | X/Y passed | [failures] |
| E2E Tests | X/Y passed | [failures] |
| Lint Check | X violations | [violations] |
| Type Check | X errors | [errors] |
| Security Scan | X findings | [findings] |
| Build | SUCCESS/FAIL | [details] |
| Coverage | X% | threshold: Y% |

---

## Gate 0: Requirement Compliance

**Status:** PASS | FAIL

[Details of requirement verification]

---

## Gate 0.5: TDD Compliance

**Status:** PASS | FAIL

[Git log analysis, RED/GREEN commits, sequence verification]

---

## Test Execution Results

### Unit Tests
[Details, failures, errors]

### Integration Tests
[Details, failures, errors]

### End-to-End Tests
[Details, failures, errors]

---

## Quality Checks

### Linting
[Results from ruff check]

### Type Checking
[Results from mypy]

### Security Scan
[Results from trufflehog/bandit]

---

## Build Verification

[Results from build command]

---

## Evidence

[Full logs, error messages, stack traces for all failures]

---

## Recommendation

[Clear action items for PR author or orchestrator]
```

### 5.2 Structured data output format

**Write JSON to:** `pr-evaluation-${PR_NUMBER}.json`

```json
{
  "pr_number": 123,
  "pr_title": "Add user authentication",
  "author": "username",
  "branch": "feature/auth",
  "evaluated_at": "2026-02-05T10:30:00Z",
  "evaluator": "amia-pr-evaluator",
  "verdict": "APPROVE|REQUEST_CHANGES|REJECT",
  "summary": {
    "requirement_compliance": "pass|fail",
    "tdd_compliance": "pass|fail",
    "tests_total": 150,
    "tests_passed": 142,
    "tests_failed": 8,
    "lint_violations": 0,
    "type_errors": 0,
    "security_findings": 0,
    "coverage_percent": 87.3,
    "build_status": "success|failure"
  },
  "gates": {
    "gate_0_requirement_compliance": {
      "status": "pass|fail",
      "evidence": "..."
    },
    "gate_0_5_tdd_compliance": {
      "status": "pass|fail",
      "red_commit": "abc123",
      "green_commit": "def456",
      "sequence_correct": true
    },
    "gate_1_tests": {
      "unit_tests": {"passed": 100, "failed": 0},
      "integration_tests": {"passed": 40, "failed": 8},
      "e2e_tests": {"passed": 2, "failed": 0}
    },
    "gate_2_quality": {
      "lint": {"violations": 0},
      "typecheck": {"errors": 0},
      "security": {"findings": []}
    },
    "gate_3_build": {
      "status": "success|failure",
      "exit_code": 0
    }
  },
  "failures": [
    {
      "category": "test",
      "test_name": "test_user_login",
      "file": "tests/auth/test_login.py",
      "line": 42,
      "error": "AssertionError: expected 200, got 401",
      "stack_trace": "..."
    }
  ],
  "recommendation": "Fix 8 failing integration tests in auth module.",
  "report_file": "/path/to/pr-evaluation-report-123.md"
}
```

---

## Summary

PR evaluation follows a **sequential gate system** with automatic rejection at early gates if fundamental requirements are not met:

1. **Gate 0:** Does PR implement what user requested?
2. **Gate 0.5:** Did PR follow TDD workflow?
3. **Gate 1:** Do all tests pass?
4. **Gate 2:** Does code meet quality standards?
5. **Gate 3:** Does code build successfully?

**Evidence-based evaluation** requires specific, reproducible, objective documentation of all findings.

**Verdict decisions** are based on clear criteria:

- **APPROVE:** All gates pass
- **REQUEST CHANGES:** Minor issues, fixable
- **REJECT:** Critical failures, fundamental problems

**Structured reporting** provides both human-readable (markdown) and machine-readable (JSON) outputs for orchestrator processing.
