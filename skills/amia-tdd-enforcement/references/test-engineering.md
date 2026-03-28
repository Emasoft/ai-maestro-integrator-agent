# Test Engineering Procedures

## Contents

- 1.1 When verifying TDD cycle compliance (RED-GREEN-REFACTOR pattern)
  - 1.1.1 RED Phase verification checklist
  - 1.1.2 GREEN Phase verification checklist
  - 1.1.3 REFACTOR Phase verification checklist
  - 1.1.4 Git history analysis for commit patterns
- 1.2 When validating test coverage meets requirements
  - 1.2.1 Running coverage tools (pytest, npm)
  - 1.2.2 Coverage thresholds and enforcement
  - 1.2.3 Parsing coverage reports
  - 1.2.4 Identifying uncovered critical paths
- 1.3 When reviewing test quality beyond coverage metrics
  - 1.3.1 Seven quality dimensions assessment
  - 1.3.2 Assertion quality evaluation
  - 1.3.3 Edge case coverage verification
  - 1.3.4 Test isolation validation
- 1.4 When enforcing quality gates before code review
  - 1.4.1 Gate 1: TDD Compliance (mandatory)
  - 1.4.2 Gate 2: Coverage Threshold (mandatory)
  - 1.4.3 Gate 3: Test Quality (advisory)
- 1.5 When executing the complete TDD workflow enforcement
  - 1.5.1 Step 1: Parsing enforcement requests
  - 1.5.2 Step 2: TDD cycle audit execution
  - 1.5.3 Step 3: Coverage analysis procedures
  - 1.5.4 Step 4: Test quality review execution
  - 1.5.5 Step 5: Report generation format
  - 1.5.6 Step 6: Results communication protocol
- 1.6 When determining rejection criteria for code changes
  - 1.6.1 Automatic rejection violations
  - 1.6.2 Conditional rejection requirements
  - 1.6.3 User escalation scenarios
- 1.7 When verifying tests match user requirements
  - 1.7.1 Loading USER_REQUIREMENTS.md
  - 1.7.2 Requirement-to-test mapping
  - 1.7.3 Traceability checklist verification
- 1.8 When using tools for test enforcement
  - 1.8.1 Read tool usage patterns
  - 1.8.2 Write tool for reports
  - 1.8.3 Bash tool for test execution
- 1.9 When troubleshooting common test enforcement issues
  - 1.9.1 No test commits found
  - 1.9.2 Coverage tool failures
  - 1.9.3 Tests pass but coverage low
  - 1.9.4 TDD compliance uncertain
  - 1.9.5 Conflicting coverage reports

---

## 1.1 When verifying TDD cycle compliance (RED-GREEN-REFACTOR pattern)

### Purpose

Verify that developers follow the strict RED-GREEN-REFACTOR cycle by analyzing git commit history and ensuring tests are written before implementation.

### 1.1.1 RED Phase verification checklist

**What to verify:**

- [ ] Failing test committed before any implementation
- [ ] Test commit message starts with "RED:"
- [ ] Test actually fails for the right reason
- [ ] Test documents intended behavior

**How to verify:**

```bash
# Get commit history for branch
git log --oneline feature-branch

# Look for commits starting with "RED:"
git log --grep="^RED:" feature-branch

# Verify test failure by checking out RED commit
git checkout <red-commit-hash>
pytest <test-file>  # Should fail
```

**Pass criteria:**

- Test commit exists with "RED:" prefix
- Test fails when run in isolation
- Failure message indicates missing functionality
- No implementation code in the same commit

### 1.1.2 GREEN Phase verification checklist

**What to verify:**

- [ ] Implementation written only after failing test exists
- [ ] Implementation commit message starts with "GREEN:"
- [ ] Minimum code to pass the test
- [ ] All tests pass after implementation

**How to verify:**

```bash
# Find GREEN commits
git log --grep="^GREEN:" feature-branch

# Verify chronological order: RED before GREEN
git log --oneline --graph feature-branch

# Check out GREEN commit and verify tests pass
git checkout <green-commit-hash>
pytest <test-file>  # Should pass
```

**Pass criteria:**

- GREEN commit follows RED commit chronologically
- Tests pass after GREEN commit
- Implementation is minimal (no extra features)
- Commit only contains implementation, not new tests

### 1.1.3 REFACTOR Phase verification checklist

**What to verify:**

- [ ] Refactoring happens only after tests pass
- [ ] Refactoring commit message starts with "REFACTOR:"
- [ ] Tests still pass after refactoring
- [ ] No behavior changes during refactor

**How to verify:**

```bash
# Find REFACTOR commits
git log --grep="^REFACTOR:" feature-branch

# Verify tests pass before and after refactor
git checkout <commit-before-refactor>
pytest  # Should pass

git checkout <refactor-commit>
pytest  # Should still pass
```

**Pass criteria:**

- REFACTOR commit follows GREEN commit
- All tests still pass
- No new tests added during refactor
- Code structure improved without behavior change

### 1.1.4 Git history analysis for commit patterns

**Analysis procedure:**

1. **Extract full commit log:**

   ```bash
   git log --oneline --decorate feature-branch
   ```

2. **Identify commit patterns:**
   - Look for RED/GREEN/REFACTOR prefixes
   - Verify chronological ordering
   - Check for implementation commits without tests

3. **Create commit timeline:**
   - Document each commit with type (RED/GREEN/REFACTOR)
   - Note any violations (GREEN before RED, etc.)
   - Flag commits without proper prefix

4. **Verification checklist:**
   - [ ] Feature branch has test commits
   - [ ] Test commits precede implementation commits
   - [ ] Commit messages follow RED/GREEN/REFACTOR pattern
   - [ ] No implementation commits without test commits

**Violation detection:**

- Implementation commit before test commit = FAIL
- Missing commit prefix = FAIL
- Multiple GREEN commits for single RED = WARN
- No REFACTOR after GREEN = ADVISORY (not mandatory)

---

## 1.2 When validating test coverage meets requirements

### Purpose

Validate that test coverage meets minimum project thresholds for line, branch, and function coverage.

### 1.2.1 Running coverage tools (pytest, npm)

**For Python projects:**

```bash
# Run pytest with coverage
pytest --cov=src --cov-report=term-missing --cov-report=json

# Generate detailed HTML report
pytest --cov=src --cov-report=html

# Coverage for specific files
pytest --cov=src/module.py --cov-report=term
```

**For JavaScript/TypeScript projects:**

```bash
# Run tests with coverage
npm run test -- --coverage

# Or with jest directly
npx jest --coverage --collectCoverageFrom='src/**/*.{js,ts}'

# Generate lcov report
npm run test -- --coverage --coverageReporters=lcov
```

**Coverage output locations:**

- Python: `coverage.json`, `.coverage`, `htmlcov/`
- JavaScript: `coverage/`, `coverage/lcov.info`

### 1.2.2 Coverage thresholds and enforcement

**Minimum thresholds:**

| Coverage Type | Minimum Threshold | Action if Below |
|---------------|-------------------|-----------------|
| Line Coverage | 80% | Block merge |
| Branch Coverage | 75% | Block merge |
| Function Coverage | 90% | Block merge |
| Critical Path Coverage | 100% | Block merge |

**Threshold verification:**

1. **Parse coverage report:**
   - Extract line coverage percentage
   - Extract branch coverage percentage
   - Extract function coverage percentage

2. **Compare against thresholds:**
   - Line >= 80%? → Gate 2 PASS condition 1
   - Branch >= 75%? → Gate 2 PASS condition 2
   - Function >= 90%? → Gate 2 PASS condition 3

3. **Critical path verification:**
   - Identify critical paths from requirements
   - Verify 100% coverage for these paths
   - Document any uncovered critical code

**Enforcement actions:**

| Condition | Action |
|-----------|--------|
| All thresholds met | PASS - proceed to Gate 3 |
| Any threshold below minimum | FAIL - block merge, generate coverage gap report |
| Coverage 75-80% | Document justification required |
| Critical path uncovered | Automatic FAIL regardless of overall coverage |

### 1.2.3 Parsing coverage reports

**Python coverage.json format:**

```bash
# Read coverage report
cat coverage.json | jq '.totals'

# Extract line coverage
cat coverage.json | jq '.totals.percent_covered'

# Find uncovered lines
cat coverage.json | jq '.files[] | select(.summary.percent_covered < 80)'
```

**JavaScript coverage format:**

```bash
# Read coverage summary
cat coverage/coverage-summary.json | jq '.total'

# Extract line coverage
cat coverage/coverage-summary.json | jq '.total.lines.pct'

# Find files with low coverage
cat coverage/coverage-summary.json | jq 'to_entries[] | select(.value.lines.pct < 80)'
```

**Coverage report sections to extract:**

- Overall coverage percentages
- Per-file coverage breakdown
- Uncovered lines list
- Branch coverage details
- Function coverage details

### 1.2.4 Identifying uncovered critical paths

**Critical path definition:**

Critical paths are code sections that:

- Handle user authentication
- Process financial transactions
- Implement security controls
- Manage data persistence
- Handle error recovery
- Execute core business logic

**Identification procedure:**

1. **Load requirements document:**

   ```bash
   # Read USER_REQUIREMENTS.md
   cat docs_dev/requirements/USER_REQUIREMENTS.md
   ```

2. **Map requirements to code:**
   - Identify files implementing each requirement
   - Mark these as critical paths
   - List functions/methods in critical paths

3. **Cross-reference with coverage:**
   - Check coverage for each critical path file
   - Identify any uncovered lines in critical code
   - Document missing tests for critical paths

4. **Report critical gaps:**

   ```markdown
   Critical Path Coverage Gaps:
   - Requirement REQ-AUTH-001: src/auth.py line 45-52 uncovered
   - Requirement REQ-DATA-003: src/persistence.py function save_transaction() 0% covered
   ```

**Automatic FAIL conditions:**

- Any critical path with <100% coverage
- Any security-related code uncovered
- Any error handling in critical paths untested

---

## 1.3 When reviewing test quality beyond coverage metrics

### Purpose

Evaluate test suite quality across multiple dimensions beyond simple coverage percentages.

### 1.3.1 Seven quality dimensions assessment

**Quality dimension weights:**

| Dimension | Weight | Evaluation Criteria |
|-----------|--------|---------------------|
| Assertion Quality | 20% | One assertion per test, meaningful assertions |
| Edge Case Coverage | 20% | Boundary conditions, error paths, empty inputs |
| Test Isolation | 15% | No shared state, no test order dependencies |
| Readability | 15% | Clear naming, Arrange-Act-Assert pattern |
| Maintainability | 10% | No hardcoded values, proper setup/teardown |
| Performance | 10% | Fast execution, no unnecessary waits |
| Documentation | 10% | Test describes behavior, not implementation |

**Scoring calculation:**

```
Quality Score = (Assertion * 0.20) + (EdgeCase * 0.20) + (Isolation * 0.15) +
                (Readability * 0.15) + (Maintainability * 0.10) +
                (Performance * 0.10) + (Documentation * 0.10)
```

**Pass criteria:**

- Quality Score >= 70% → PASS
- Quality Score 60-70% → WARN (advisory)
- Quality Score < 60% → FAIL (does not block, but documented)

### 1.3.2 Assertion quality evaluation

**What to check:**

1. **One assertion per test:**
   - Count assertions in each test method
   - Flag tests with multiple assertions
   - Score: (tests with 1 assertion / total tests) * 100

2. **Meaningful assertions:**
   - Check for `assert True` or `assert foo` without comparison
   - Verify assertions check specific expected values
   - Flag generic assertions without context

3. **Assertion message quality:**
   - Verify assertions include failure messages
   - Check messages explain what failed
   - Example: `assert result == 5, f"Expected 5 but got {result}"`

**Scoring:**

- 100%: All tests have exactly 1 meaningful assertion with clear message
- 75%: Most tests have 1 assertion, some lack messages
- 50%: Multiple assertions per test, unclear messages
- 25%: Generic assertions (assert True, assert foo)
- 0%: No assertions or empty test bodies

### 1.3.3 Edge case coverage verification

**Edge cases to verify:**

1. **Boundary conditions:**
   - [ ] Minimum values (0, -1, empty string)
   - [ ] Maximum values (MAX_INT, very long strings)
   - [ ] Off-by-one errors (array[length], array[length-1])

2. **Error paths:**
   - [ ] Invalid input handling
   - [ ] Null/None handling
   - [ ] Exception raising and catching
   - [ ] Network failures (timeouts, disconnects)

3. **Empty inputs:**
   - [ ] Empty lists, arrays, strings
   - [ ] Zero quantities
   - [ ] Missing optional parameters

4. **Special values:**
   - [ ] Negative numbers where positive expected
   - [ ] Floating point edge cases (NaN, Infinity)
   - [ ] Unicode and special characters
   - [ ] Date edge cases (leap years, timezone boundaries)

**Edge case scoring:**

```
Edge Case Score = (Edge cases tested / Total expected edge cases) * 100
```

**Analysis procedure:**

1. Read all test files
2. Identify test names suggesting edge cases (test_empty, test_null, test_boundary)
3. Count edge case tests
4. Compare against expected edge cases for the module
5. Document missing edge case tests

### 1.3.4 Test isolation validation

**Isolation checks:**

1. **No shared mutable state:**

   ```python
   # BAD: Shared state between tests
   class TestSuite:
       shared_data = []  # Mutable shared state

       def test_a(self):
           self.shared_data.append(1)

       def test_b(self):
           assert len(self.shared_data) == 1  # Depends on test_a running first
   ```

2. **No test order dependencies:**
   - Tests must pass when run in any order
   - Tests must pass when run individually
   - Tests must not depend on setup from other tests

3. **Proper setup and teardown:**
   - Use `setUp()` / `tearDown()` or fixtures
   - Clean up resources after each test
   - Reset state between tests

**Validation procedure:**

```bash
# Run tests in random order
pytest --random-order

# Run tests in reverse order
pytest --reverse

# Run each test individually
pytest test_file.py::test_function_name
```

**Scoring:**

- 100%: All tests pass in any order, individually
- 75%: Tests pass normally but fail in random order
- 50%: Tests depend on specific order
- 0%: Tests fail when run individually

---

## 1.4 When enforcing quality gates before code review

### Purpose

Apply three-gate quality system to determine if code can proceed to review and merge.

### 1.4.1 Gate 1: TDD Compliance (mandatory)

**Purpose:** Verify developer followed TDD discipline.

**Verification steps:**

1. **Read git log for feature branch:**

   ```bash
   git log --oneline feature-branch
   ```

2. **Identify test commits (RED) and implementation commits (GREEN):**
   - Parse commit messages
   - Extract commits with "RED:" prefix
   - Extract commits with "GREEN:" prefix

3. **Verify chronological order:**
   - RED must come before GREEN
   - No GREEN without preceding RED
   - Each feature has complete RED-GREEN cycle

4. **Check commit message patterns:**
   - RED: <test description>
   - GREEN: <implementation description>
   - REFACTOR: <refactoring description> (optional)

5. **Verify test failure/pass states:**
   - Checkout RED commit → tests should fail
   - Checkout GREEN commit → tests should pass

**Pass criteria:**

- Every implementation has a preceding failing test
- Correct commit message pattern followed
- No implementation commits without test commits
- Tests fail at RED, pass at GREEN

**Fail action:**

- Generate TDD Violation Report
- Block code review
- Send violation notice via AI Maestro
- Return: `G1:FAIL`

**Output:**

- `G1:PASS` → Proceed to Gate 2
- `G1:FAIL` → Block, skip Gate 2 and Gate 3

### 1.4.2 Gate 2: Coverage Threshold (mandatory)

**Purpose:** Verify test coverage meets minimum standards.

**Verification steps:**

1. **Run test suite with coverage enabled:**

   ```bash
   # Python
   pytest --cov=src --cov-report=json

   # JavaScript
   npm run test -- --coverage
   ```

2. **Parse coverage report:**
   - Extract line coverage percentage
   - Extract branch coverage percentage
   - Extract function coverage percentage

3. **Check against thresholds:**
   - Line coverage >= 80%?
   - Branch coverage >= 75%?
   - Function coverage >= 90%?

4. **Identify uncovered critical paths:**
   - Load USER_REQUIREMENTS.md
   - Map requirements to critical code
   - Verify 100% coverage for critical paths

**Pass criteria:**

- Line coverage >= 80%
- Branch coverage >= 75%
- Function coverage >= 90%
- Critical paths at 100%

**Fail action:**

- Generate Coverage Gap Report
- List uncovered lines and branches
- Block merge until coverage improved
- Return: `G2:FAIL`

**Output:**

- `G2:PASS` → Proceed to Gate 3
- `G2:FAIL` → Block, Gate 3 may still run for advisory info

### 1.4.3 Gate 3: Test Quality (advisory)

**Purpose:** Evaluate test suite quality beyond coverage.

**Verification steps:**

1. **Analyze test file structure:**
   - Read all test files
   - Count test methods
   - Check naming conventions

2. **Review assertion patterns:**
   - Count assertions per test
   - Check for meaningful assertions
   - Verify assertion messages

3. **Check for test isolation:**
   - Look for shared mutable state
   - Check for test order dependencies
   - Verify proper setup/teardown

4. **Evaluate edge case coverage:**
   - Identify edge case tests
   - Compare against expected edge cases
   - Document missing edge cases

5. **Calculate quality score:**
   - Score each of 7 dimensions
   - Apply weights
   - Compute overall quality score

**Pass criteria:**

- Quality score >= 70%
- No critical quality issues

**Advisory action (if below threshold):**

- Generate Quality Improvement Suggestions
- Document in report
- Does NOT block (advisory only)
- Return: `G3:WARN`

**Output:**

- `G3:PASS` → All gates passed
- `G3:WARN` → Advisory warnings, does not block
- `G3:FAIL` → Serious quality issues, documented but not blocking

---

## 1.5 When executing the complete TDD workflow enforcement

### Purpose

Execute end-to-end TDD enforcement workflow from request to final report.

### 1.5.1 Step 1: Parsing enforcement requests

**Request metadata to extract:**

- PR number or feature branch name
- Files changed (implementation and tests)
- Expected test locations
- Coverage requirements (if non-standard)
- Deadline or urgency

**Parsing procedure:**

```bash
# Get PR metadata
gh pr view <PR_NUMBER> --json files,title,body

# Get files changed
gh pr diff <PR_NUMBER> --name-only

# Identify test files vs implementation files
gh pr diff <PR_NUMBER> --name-only | grep -E '(test_|_test\.)'
```

**Validation:**

- [ ] PR number valid and accessible
- [ ] Feature branch exists
- [ ] Files changed list retrieved
- [ ] Test files identified
- [ ] Implementation files identified

### 1.5.2 Step 2: TDD cycle audit execution

**Audit procedure:**

1. **Get commit history:**

   ```bash
   git log --oneline feature-branch
   ```

2. **Identify commit patterns:**

   ```bash
   # Find RED commits
   git log --grep="^RED:" feature-branch

   # Find GREEN commits
   git log --grep="^GREEN:" feature-branch

   # Find REFACTOR commits
   git log --grep="^REFACTOR:" feature-branch
   ```

3. **Verify chronological order:**
   - Parse commit timestamps
   - Ensure RED precedes GREEN
   - Document any violations

4. **Test failure verification:**

   ```bash
   # For each RED commit, verify test fails
   git checkout <RED_COMMIT>
   pytest <test_file> 2>&1 | tee test-failure-log.txt

   # For corresponding GREEN commit, verify test passes
   git checkout <GREEN_COMMIT>
   pytest <test_file> 2>&1 | tee test-pass-log.txt
   ```

**Verification checklist:**

- [ ] Feature branch has test commits
- [ ] Test commits precede implementation commits
- [ ] Commit messages follow RED/GREEN/REFACTOR pattern
- [ ] Tests fail at RED commits
- [ ] Tests pass at GREEN commits

**Output:**

- TDD compliance status: COMPLIANT or VIOLATION
- Violation details if any
- Commit timeline document

### 1.5.3 Step 3: Coverage analysis procedures

**Analysis procedure:**

1. **Run test suite with coverage:**

   ```bash
   # Python
   pytest --cov=src --cov-report=term-missing --cov-report=json

   # JavaScript
   npm run test -- --coverage
   ```

2. **Parse coverage report:**

   ```bash
   # Python
   cat coverage.json | jq '.totals'

   # JavaScript
   cat coverage/coverage-summary.json | jq '.total'
   ```

3. **Extract metrics:**
   - Line coverage percentage
   - Branch coverage percentage
   - Function coverage percentage
   - Uncovered lines list

4. **Compare against thresholds:**
   - Line >= 80%?
   - Branch >= 75%?
   - Function >= 90%?

5. **Identify gaps:**

   ```bash
   # List uncovered lines
   pytest --cov=src --cov-report=term-missing | grep "TOTAL"
   ```

**Coverage checklist:**

- [ ] Line coverage meets threshold
- [ ] Branch coverage meets threshold
- [ ] Function coverage meets threshold
- [ ] Critical paths fully covered
- [ ] Coverage gaps documented

**Output:**

- Coverage percentages: line/branch/function
- Coverage status: PASS or FAIL
- Uncovered lines list
- Coverage gap document

### 1.5.4 Step 4: Test quality review execution

**Review procedure:**

1. **Read all test files:**

   ```bash
   # Get list of test files
   find . -name "test_*.py" -o -name "*_test.js"

   # Read each test file
   cat test_file.py
   ```

2. **Analyze test structure:**
   - Count test methods
   - Check naming conventions
   - Identify test patterns

3. **Evaluate each quality dimension:**
   - Assertion quality: Count assertions per test
   - Edge cases: Look for boundary/error tests
   - Isolation: Check for shared state
   - Readability: Evaluate naming and structure
   - Maintainability: Check for hardcoded values
   - Performance: Note any slow tests
   - Documentation: Review docstrings

4. **Score each dimension:**
   - Apply scoring criteria for each dimension
   - Calculate weighted score
   - Determine overall quality score

5. **Generate recommendations:**
   - Document quality issues found
   - Suggest improvements
   - Prioritize fixes

**Quality checklist:**

- [ ] One assertion per test method
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] No shared mutable state between tests
- [ ] Edge cases covered (null, empty, boundary)
- [ ] Error paths tested
- [ ] Tests are independent

**Output:**

- Quality score percentage
- Quality status: PASS/WARN/FAIL
- Quality issues list
- Improvement recommendations

### 1.5.5 Step 5: Report generation format

**Report structure:**

```markdown
# TDD Compliance Report

**PR:** #{number}
**Branch:** feature-branch-name
**Timestamp:** YYYY-MM-DD HH:MM:SS
**Analyst:** amia-test-engineer

## Executive Summary

Gate 1 (TDD Compliance): [PASS/FAIL]
Gate 2 (Coverage Threshold): [PASS/FAIL]
Gate 3 (Test Quality): [PASS/WARN/FAIL]

**Overall Status:** [APPROVED / REJECTED / NEEDS IMPROVEMENT]

## 1. TDD Cycle Compliance (Gate 1)

### Commit Timeline
- RED: commit_hash - test description
- GREEN: commit_hash - implementation description
- REFACTOR: commit_hash - refactor description

### Verification Results
- [x] Failing test exists before implementation
- [x] Correct commit message pattern
- [x] Tests fail at RED, pass at GREEN

**Gate 1 Result:** PASS

## 2. Coverage Analysis (Gate 2)

### Coverage Metrics
- Line Coverage: XX%
- Branch Coverage: XX%
- Function Coverage: XX%

### Threshold Compliance
- Line: [PASS/FAIL] (80% required)
- Branch: [PASS/FAIL] (75% required)
- Function: [PASS/FAIL] (90% required)

### Uncovered Code
- src/module.py: lines 45-52
- src/utils.py: function calculate()

**Gate 2 Result:** PASS/FAIL

## 3. Test Quality Assessment (Gate 3)

### Quality Dimensions
- Assertion Quality: XX/100
- Edge Case Coverage: XX/100
- Test Isolation: XX/100
- Readability: XX/100
- Maintainability: XX/100
- Performance: XX/100
- Documentation: XX/100

**Overall Quality Score:** XX%

### Issues Found
1. Multiple assertions in test_foo()
2. Missing edge case for empty input
3. Shared state in test class

### Recommendations
1. Split test_foo() into separate tests
2. Add test_empty_input()
3. Use fixtures instead of class variables

**Gate 3 Result:** PASS/WARN/FAIL

## 4. Requirement Traceability

### Requirements Coverage
- [x] REQ-001: Tested in test_requirement_001()
- [ ] REQ-002: NO TESTS FOUND
- [x] REQ-003: Tested in test_requirement_003()

### Violations
- REQ-002 is not tested (BLOCKING)

## 5. Final Determination

**Decision:** [APPROVED / REJECTED]

**Reasons:**
- Gate 1: [reason]
- Gate 2: [reason]
- Gate 3: [reason]

**Next Steps:**
- [Action required from developer]
```

**Report location:**
`reports/tdd-compliance-PR{number}-{timestamp}.md`

### 1.5.6 Step 6: Results communication protocol

**Communication steps:**

1. **Generate report file:**

   ```bash
   # Save report to standard location
   REPORT_FILE="reports/tdd-compliance-PR${PR_NUMBER}-$(date +%Y%m%d%H%M%S).md"
   echo "$REPORT_CONTENT" > "$REPORT_FILE"
   ```

2. **Send AI Maestro message to developer:** Send a message using the `agent-messaging` skill with:
   - **Recipient**: The developer agent name
   - **Subject**: `TDD Compliance Report for PR #<PR_NUMBER>`
   - **Priority**: `high`
   - **Content**: `{"type": "test_report", "message": "TDD enforcement complete. Status: [PASS/FAIL]. Details: <REPORT_FILE>"}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

3. **Post PR comment:**

   ```bash
   gh pr comment ${PR_NUMBER} --body "## TDD Compliance Report

   Gate 1 (TDD): ${GATE1_STATUS}
   Gate 2 (Coverage): ${GATE2_STATUS}
   Gate 3 (Quality): ${GATE3_STATUS}

   Full report: ${REPORT_FILE}"
   ```

4. **Update GitHub Projects board:**

   ```bash
   # Add "needs-tests" label if failed
   if [ "$GATE1_STATUS" == "FAIL" ] || [ "$GATE2_STATUS" == "FAIL" ]; then
     gh pr edit ${PR_NUMBER} --add-label "needs-tests"
   fi

   # Update project board status
   # (requires project board API access)
   ```

5. **Return minimal output to orchestrator:**

   ```
   [DONE] test-engineer - PR#${PR_NUMBER} G1:${GATE1} G2:${GATE2} G3:${GATE3}
   Coverage: ${LINE}%/${BRANCH}%/${FUNCTION}% | TDD: ${STATUS}
   Details: ${REPORT_FILE}
   ```

---

## 1.6 When determining rejection criteria for code changes

### Purpose

Apply consistent rejection criteria to determine if code can proceed to merge.

### 1.6.1 Automatic rejection violations

**The following violations automatically reject code:**

1. **No failing test before implementation**
   - **Reason:** TDD fundamental violation
   - **Detection:** Git history shows implementation commit without preceding RED commit
   - **Action:** Block code review, send violation notice
   - **Message:** "REJECTED: Implementation committed before failing test (TDD violation)"

2. **Implementation without test commit**
   - **Reason:** Missing RED phase
   - **Detection:** Implementation commit exists but no corresponding test commit
   - **Action:** Block code review, request tests
   - **Message:** "REJECTED: No tests found for implementation"

3. **Coverage below 80%**
   - **Reason:** Insufficient test coverage
   - **Detection:** Line coverage < 80%
   - **Action:** Block merge, generate coverage gap report
   - **Message:** "REJECTED: Coverage {XX}% below threshold (80% required)"

4. **Tests don't run**
   - **Reason:** Broken test suite
   - **Detection:** Test execution fails or throws errors
   - **Action:** Block immediately, request fix
   - **Message:** "REJECTED: Test suite fails to execute"

5. **Tests depend on execution order**
   - **Reason:** Test isolation violation
   - **Detection:** Tests pass normally but fail in random order
   - **Action:** Block merge, request isolation fix
   - **Message:** "REJECTED: Tests fail when run in random order (isolation violation)"

### 1.6.2 Conditional rejection requirements

**The following require explicit justification:**

1. **Coverage between 75-80%**
   - **Condition:** Line coverage 75-79%
   - **Requirement:** Developer must document:
     - Why 80% cannot be achieved
     - Risk assessment of uncovered code
     - Plan to improve coverage
   - **Approval:** Requires orchestrator or user approval
   - **Message:** "CONDITIONAL: Coverage {XX}% below threshold. Justification required."

2. **Test quality score 60-70%**
   - **Condition:** Gate 3 quality score 60-69%
   - **Requirement:** Developer must provide:
     - Test quality improvement plan
     - Timeline for improvements
     - Risk mitigation strategy
   - **Approval:** Requires code reviewer approval
   - **Message:** "ADVISORY: Test quality {XX}% below 70%. Improvement plan required."

3. **Missing edge case tests**
   - **Condition:** Edge case score < 80%
   - **Requirement:** Developer must document:
     - Which edge cases are untested
     - Why these edge cases are not critical
     - Acceptance of risk
   - **Approval:** Requires user approval
   - **Message:** "ADVISORY: Edge cases incomplete. Risk acceptance required."

### 1.6.3 User escalation scenarios

**The following must be escalated to the user:**

1. **Requirement untested**
   - **Scenario:** USER_REQUIREMENTS.md contains requirement with no corresponding test
   - **Escalation reason:** Only user can approve requirement gap
   - **Required info:**
     - Which requirement is untested
     - Impact of not testing
     - Developer's explanation
   - **Message:** "ESCALATION: Requirement {REQ-XXX} has no tests. User approval needed."

2. **Technology mismatch in tests**
   - **Scenario:** Tests use different framework than specified in requirements
   - **Escalation reason:** May indicate requirement misunderstanding
   - **Required info:**
     - Expected technology
     - Actual technology used
     - Justification for mismatch
   - **Message:** "ESCALATION: Tests use {TECH_A} but requirements specify {TECH_B}. User approval needed."

3. **Scope reduction in testing**
   - **Scenario:** Developer requests to reduce testing scope (lower thresholds, skip requirements)
   - **Escalation reason:** Only user can approve scope changes
   - **Required info:**
     - Original scope
     - Requested reduced scope
     - Business justification
   - **Message:** "ESCALATION: Request to reduce test scope. User decision required."

**Escalation procedure:**

1. **Document the issue:**
   - Create escalation document in `reports/escalations/`
   - Include all relevant context
   - Provide recommendation

2. **Notify user via AI Maestro:** Send a message using the `agent-messaging` skill with:
   - **Recipient**: `orchestrator-master`
   - **Subject**: `ESCALATION: Test enforcement decision required`
   - **Priority**: `urgent`
   - **Content**: `{"type": "escalation", "message": "User decision required for PR #<PR>. See: reports/escalations/escalation-<timestamp>.md"}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

3. **Wait for user response:**
   - Do NOT proceed with automated decision
   - Block PR until user responds
   - Mark PR with "needs-user-decision" label

---

## 1.7 When verifying tests match user requirements

### Purpose

Ensure tests validate user requirements and maintain requirement-to-test traceability.

### 1.7.1 Loading USER_REQUIREMENTS.md

**File location:**
`docs_dev/requirements/USER_REQUIREMENTS.md`

**Loading procedure:**

```bash
# Check if requirements file exists
if [ ! -f "docs_dev/requirements/USER_REQUIREMENTS.md" ]; then
  echo "WARNING: USER_REQUIREMENTS.md not found"
  # Escalate to orchestrator
fi

# Read requirements file
REQUIREMENTS=$(cat docs_dev/requirements/USER_REQUIREMENTS.md)

# Parse requirements
# Look for requirement IDs: REQ-XXX
grep -E "REQ-[A-Z]+-[0-9]+" docs_dev/requirements/USER_REQUIREMENTS.md > requirements-list.txt
```

**Requirement format expected:**

```markdown
## REQ-AUTH-001: User Authentication

**Description:** Users must authenticate using username and password

**Acceptance Criteria:**
- [ ] User can log in with valid credentials
- [ ] Invalid credentials are rejected
- [ ] Session is created on successful login
- [ ] Failed attempts are logged

**Test Verification:** Tests must verify all acceptance criteria
```

### 1.7.2 Requirement-to-test mapping

**Mapping procedure:**

1. **Extract requirement IDs:**

   ```bash
   # Get all requirement IDs from USER_REQUIREMENTS.md
   grep -oE "REQ-[A-Z]+-[0-9]+" docs_dev/requirements/USER_REQUIREMENTS.md | sort -u > req-ids.txt
   ```

2. **Search for tests referencing each requirement:**

   ```bash
   # For each requirement ID, find tests
   while read REQ_ID; do
     echo "Searching tests for $REQ_ID"
     grep -r "$REQ_ID" tests/ --include="*.py" --include="*.js"
   done < req-ids.txt
   ```

3. **Create requirement-to-test mapping:**

   ```bash
   # Generate mapping document
   echo "# Requirement Traceability Matrix" > traceability-matrix.md

   while read REQ_ID; do
     echo "## $REQ_ID" >> traceability-matrix.md

     # Find tests
     TESTS=$(grep -r "$REQ_ID" tests/ --include="*.py" --include="*.js" -l)

     if [ -z "$TESTS" ]; then
       echo "- **NO TESTS FOUND** ⚠️" >> traceability-matrix.md
     else
       echo "- Tests found:" >> traceability-matrix.md
       echo "$TESTS" | while read TEST_FILE; do
         echo "  - $TEST_FILE" >> traceability-matrix.md
       done
     fi
   done < req-ids.txt
   ```

4. **Identify gaps:**
   - Requirements with no tests → VIOLATION
   - Tests with no requirement reference → WARNING
   - Requirements partially tested → INCOMPLETE

### 1.7.3 Traceability checklist verification

**Checklist items:**

For each test file, verify:

- [ ] **Tests trace to requirements**
  - Each test has a comment: `# Tests REQ-XXX`
  - Or docstring: `"""Verifies REQ-XXX: description"""`
  - Test name references requirement: `test_req_xxx_...`

- [ ] **All requirements have tests**
  - Loop through all requirement IDs
  - Verify each has at least one test
  - Document any missing tests

- [ ] **No unauthorized testing**
  - Tests should only verify specified requirements
  - Flag tests that test undocumented behavior
  - Escalate to user if feature scope expanded

- [ ] **Technology matches specification**
  - Check test framework matches requirements
  - Verify test approach aligns with specification
  - Example: If requirement says "unit tests", verify no integration tests

**Verification script:**

```bash
#!/bin/bash
# verify-traceability.sh

REQUIREMENTS_FILE="docs_dev/requirements/USER_REQUIREMENTS.md"
TEST_DIR="tests/"
REPORT_FILE="reports/traceability-report.md"

# Extract requirement IDs
REQ_IDS=$(grep -oE "REQ-[A-Z]+-[0-9]+" "$REQUIREMENTS_FILE" | sort -u)

echo "# Requirement Traceability Report" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

MISSING_TESTS=0

for REQ_ID in $REQ_IDS; do
  echo "Checking $REQ_ID..."

  # Search for tests
  TESTS=$(grep -r "$REQ_ID" "$TEST_DIR" -l 2>/dev/null)

  if [ -z "$TESTS" ]; then
    echo "## ⚠️ $REQ_ID - NO TESTS FOUND" >> "$REPORT_FILE"
    echo "**Status:** VIOLATION" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    MISSING_TESTS=$((MISSING_TESTS + 1))
  else
    echo "## ✓ $REQ_ID - Tests Found" >> "$REPORT_FILE"
    echo "**Status:** PASS" >> "$REPORT_FILE"
    echo "**Test Files:**" >> "$REPORT_FILE"
    echo "$TESTS" | while read TEST_FILE; do
      echo "- $TEST_FILE" >> "$REPORT_FILE"
    done
    echo "" >> "$REPORT_FILE"
  fi
done

echo "## Summary" >> "$REPORT_FILE"
echo "- Total Requirements: $(echo "$REQ_IDS" | wc -l)" >> "$REPORT_FILE"
echo "- Missing Tests: $MISSING_TESTS" >> "$REPORT_FILE"

if [ $MISSING_TESTS -gt 0 ]; then
  echo "**TRACEABILITY VIOLATION:** $MISSING_TESTS requirements have no tests" >> "$REPORT_FILE"
  exit 1
else
  echo "**TRACEABILITY PASS:** All requirements have tests" >> "$REPORT_FILE"
  exit 0
fi
```

**Violation reporting:**

If tests do not cover user requirements:

```markdown
[REVIEW BLOCKED] Requirement Coverage Violation

**Untested Requirement:** REQ-AUTH-001 - User authentication with username/password
**Expected Test:** test_user_authentication_with_valid_credentials()
**Violation Type:** Missing Test

**Impact:** Authentication requirement has no test coverage. Security risk.

**Action Required:** Create tests for REQ-AUTH-001 before this PR can be approved.

**See:** docs_dev/requirement-issues/20250205-test-violation-REQ-AUTH-001.md
```

---

## 1.8 When using tools for test enforcement

### Purpose

Define proper usage of Read, Write, and Bash tools for TDD enforcement tasks.

### 1.8.1 Read tool usage patterns

**What to read:**

1. **Test files:**

   ```
   Read test_module.py
   Read test_feature.js
   ```

   - Purpose: Analyze test structure and quality
   - Look for: Assertions, edge cases, isolation

2. **Implementation files:**

   ```
   Read src/module.py
   Read src/feature.js
   ```

   - Purpose: Understand what is being tested
   - Look for: Functions, classes, critical paths

3. **Coverage reports:**

   ```
   Read coverage.json
   Read coverage/coverage-summary.json
   ```

   - Purpose: Extract coverage metrics
   - Look for: Line/branch/function percentages

4. **Requirement documents:**

   ```
   Read docs_dev/requirements/USER_REQUIREMENTS.md
   ```

   - Purpose: Verify test-to-requirement traceability
   - Look for: Requirement IDs, acceptance criteria

5. **Git history:**

   ```
   Read .git/logs/HEAD
   ```

   - Purpose: Verify TDD cycle compliance
   - Look for: Commit patterns, chronological order

**Read tool best practices:**

- Read before writing reports
- Read implementation to understand test context
- Read coverage before analyzing gaps
- Read requirements before verifying traceability

### 1.8.2 Write tool for reports

**What to write:**

1. **TDD compliance reports:**

   ```
   Write reports/tdd-compliance-PR{number}-{timestamp}.md
   ```

   - Content: Gate results, compliance status, violations

2. **Coverage gap reports:**

   ```
   Write reports/coverage-gaps-PR{number}-{timestamp}.md
   ```

   - Content: Uncovered lines, missing tests, gap analysis

3. **Test quality reports:**

   ```
   Write reports/test-quality-PR{number}-{timestamp}.md
   ```

   - Content: Quality scores, issues, recommendations

4. **Violation notices:**

   ```
   Write reports/violations/tdd-violation-PR{number}-{timestamp}.md
   ```

   - Content: Specific TDD violations, required fixes

5. **Traceability reports:**

   ```
   Write reports/traceability-PR{number}-{timestamp}.md
   ```

   - Content: Requirement-to-test mapping, missing tests

**Write tool best practices:**

- Use consistent file naming: `{type}-PR{number}-{timestamp}.md`
- Always include timestamp
- Save to `reports/` directory
- Use markdown format for readability
- Include actionable recommendations

### 1.8.3 Bash tool for test execution

**What to execute:**

1. **Run test suites:**

   ```bash
   # Python
   pytest tests/ -v

   # JavaScript
   npm run test
   ```

2. **Run coverage analysis:**

   ```bash
   # Python with coverage
   pytest --cov=src --cov-report=term-missing --cov-report=json

   # JavaScript with coverage
   npm run test -- --coverage
   ```

3. **Query git history:**

   ```bash
   # Get commit log
   git log --oneline feature-branch

   # Search for commit patterns
   git log --grep="^RED:" feature-branch
   ```

4. **Execute linting tools:**

   ```bash
   # Python linting
   ruff check src/ tests/

   # JavaScript linting
   npm run lint
   ```

5. **Send AI Maestro messages:**
   Send a message using the `agent-messaging` skill with the appropriate Recipient, Subject, Priority, and Content fields.
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

6. **Update GitHub PR:**

   ```bash
   # Post PR comment
   gh pr comment {PR_NUMBER} --body "..."

   # Add label
   gh pr edit {PR_NUMBER} --add-label "needs-tests"
   ```

**Bash tool best practices:**

- Always set timeout for long-running operations
- Capture output to files for analysis
- Use `2>&1` to capture stderr
- Check exit codes to detect failures
- Use `tee` to log output while viewing it

**Example: Complete test enforcement via Bash:**

```bash
#!/bin/bash
# complete-test-enforcement.sh

PR_NUMBER=$1
TIMESTAMP=$(date +%Y%m%d%H%M%S)
REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"

echo "=== Test Enforcement for PR #$PR_NUMBER ==="

# Step 1: Verify TDD compliance
echo "Step 1: Checking TDD compliance..."
git log --oneline feature-branch > "$REPORT_DIR/commits-$TIMESTAMP.txt"
TDD_STATUS="PASS"
if ! git log --grep="^RED:" feature-branch | grep -q "RED:"; then
  echo "WARNING: No RED commits found"
  TDD_STATUS="FAIL"
fi

# Step 2: Run tests with coverage
echo "Step 2: Running tests with coverage..."
pytest --cov=src --cov-report=json --cov-report=term-missing > "$REPORT_DIR/test-output-$TIMESTAMP.txt" 2>&1
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
  echo "ERROR: Tests failed or didn't run"
  TDD_STATUS="FAIL"
fi

# Step 3: Parse coverage
echo "Step 3: Parsing coverage..."
LINE_COV=$(cat coverage.json | jq '.totals.percent_covered')
BRANCH_COV=$(cat coverage.json | jq '.totals.percent_covered_branches')

COV_STATUS="PASS"
if (( $(echo "$LINE_COV < 80" | bc -l) )); then
  echo "WARNING: Line coverage $LINE_COV% below 80%"
  COV_STATUS="FAIL"
fi

# Step 4: Generate report
echo "Step 4: Generating report..."
REPORT_FILE="$REPORT_DIR/tdd-compliance-PR$PR_NUMBER-$TIMESTAMP.md"
cat > "$REPORT_FILE" <<EOF
# TDD Compliance Report - PR #$PR_NUMBER

**Timestamp:** $(date)
**Analyst:** amia-test-engineer

## Results
- Gate 1 (TDD): $TDD_STATUS
- Gate 2 (Coverage): $COV_STATUS
- Line Coverage: $LINE_COV%
- Branch Coverage: $BRANCH_COV%

## Details
See attached logs:
- Commits: $REPORT_DIR/commits-$TIMESTAMP.txt
- Test output: $REPORT_DIR/test-output-$TIMESTAMP.txt
EOF

echo "Report generated: $REPORT_FILE"

# Step 5: Send AI Maestro message
echo "Step 5: Sending notification..."
# Send a message using the `agent-messaging` skill with:
# - Recipient: `orchestrator-master`
# - Subject: `TDD Report for PR #$PR_NUMBER`
# - Priority: `high`
# - Content: `{"type": "test_report", "message": "G1:$TDD_STATUS G2:$COV_STATUS | Coverage: $LINE_COV% | Report: $REPORT_FILE"}`
# - Verify: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

echo "=== Test Enforcement Complete ==="
```

---

## 1.9 When troubleshooting common test enforcement issues

### Purpose

Resolve common problems encountered during test enforcement.

### 1.9.1 No test commits found

**Problem:**
Cannot identify test commits in git history. No commits with "RED:" prefix.

**Symptoms:**

- `git log --grep="^RED:"` returns no results
- Unable to verify TDD compliance
- Uncertain if developer followed TDD

**Possible causes:**

1. **Non-standard commit patterns:**
   - Developer used different prefix (e.g., "test:", "Test:", "feat:")
   - Developer didn't use prefixes at all

2. **All changes in single commit:**
   - Tests and implementation committed together
   - No separate RED/GREEN commits

3. **Wrong branch:**
   - Analyzing wrong branch
   - Feature branch not yet pushed

**Solutions:**

1. **Check for alternate patterns:**

   ```bash
   # Search for "test" in commit messages
   git log --grep="test" --grep="Test" -i feature-branch

   # Search for test file commits
   git log --oneline -- tests/
   ```

2. **Review all commits manually:**

   ```bash
   # Show detailed commit info
   git log --stat feature-branch

   # Look for test files in diffs
   git log -p feature-branch -- tests/
   ```

3. **Ask developer about testing approach:**
   - Send AI Maestro message requesting TDD evidence
   - Document uncertainty in report
   - Mark as "TDD UNCERTAIN" (not PASS or FAIL)

4. **Document the issue:**

   ```markdown
   **TDD Compliance:** UNCERTAIN

   **Reason:** No commits with RED/GREEN pattern found. Developer may have:
   1. Used non-standard commit messages
   2. Committed tests and implementation together
   3. Followed TDD but didn't label commits

   **Recommendation:** Request developer confirmation of TDD approach.
   ```

### 1.9.2 Coverage tool failures

**Problem:**
Coverage tool crashes or produces no output.

**Symptoms:**

- `pytest --cov=src` fails with error
- No `coverage.json` file generated
- Coverage report is empty or corrupted

**Possible causes:**

1. **Coverage tool not installed:**

   ```bash
   # Python
   pip show pytest-cov  # Check if installed

   # JavaScript
   npm list jest  # Check if installed
   ```

2. **Incorrect configuration:**
   - `.coveragerc` file misconfigured
   - `jest.config.js` missing or wrong
   - Coverage paths wrong

3. **Tests don't run:**
   - Tests fail before coverage calculated
   - Import errors prevent test execution

**Solutions:**

1. **Verify test framework installed:**

   ```bash
   # Python
   pip install pytest pytest-cov

   # JavaScript
   npm install --save-dev jest
   ```

2. **Check configuration:**

   ```bash
   # Python - check .coveragerc
   cat .coveragerc

   # JavaScript - check jest.config.js
   cat jest.config.js
   ```

3. **Run tests manually first:**

   ```bash
   # Python - run tests without coverage
   pytest tests/ -v

   # JavaScript - run tests without coverage
   npm run test
   ```

4. **Try manual test run first:**

   ```bash
   # If tests pass, try coverage again
   pytest --cov=src --cov-report=term
   ```

5. **Check for import errors:**

   ```bash
   # Python - verify imports work
   python -c "import src.module"

   # JavaScript - verify imports work
   node -e "require('./src/module')"
   ```

6. **Document the failure:**

   ```markdown
   **Gate 2 (Coverage):** SKIPPED

   **Reason:** Coverage tool failed to execute.

   **Error:** [paste error message]

   **Recommendation:** Fix coverage tool configuration before proceeding.
   ```

### 1.9.3 Tests pass but coverage low

**Problem:**
Tests run successfully but coverage is below threshold.

**Symptoms:**

- All tests pass (green)
- Coverage report shows <80% line coverage
- Gate 2 fails despite passing tests

**Possible causes:**

1. **Incomplete test coverage:**
   - Tests don't cover all code paths
   - Only happy path tested, error paths untested
   - Edge cases missing

2. **Dead code:**
   - Unused functions not removed
   - Deprecated code still in codebase

3. **Missing tests:**
   - Some modules have no tests at all
   - Test files exist but don't cover all functions

**Solutions:**

1. **Identify uncovered lines:**

   ```bash
   # Python - show missing lines
   pytest --cov=src --cov-report=term-missing

   # JavaScript - generate detailed report
   npm run test -- --coverage --verbose
   ```

2. **Generate coverage HTML report:**

   ```bash
   # Python
   pytest --cov=src --cov-report=html
   open htmlcov/index.html

   # JavaScript
   npm run test -- --coverage
   open coverage/lcov-report/index.html
   ```

3. **Document gaps:**

   ```markdown
   ## Uncovered Code

   ### src/module.py (65% coverage)
   - Lines 45-52: Error handling code untested
   - Lines 78-85: Edge case for empty input untested
   - Function `calculate()`: 0% coverage - no tests exist

   ### src/utils.py (50% coverage)
   - Lines 12-20: Validation logic untested
   ```

4. **Request additional tests:**

   ```bash
   # Send AI Maestro message to developer
   Send a message using the `agent-messaging` skill with:
   - **Recipient**: `developer-agent`
   - **Subject**: `Coverage gaps in PR #123`
   - **Priority**: `high`
   - **Content**: `{"type": "coverage_gap", "message": "Coverage is 65%, below 80% threshold. Uncovered: src/module.py lines 45-52, 78-85. See: reports/coverage-gaps-PR123-timestamp.md"}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

5. **Block merge until fixed:**

   ```markdown
   **Gate 2 Result:** FAIL

   **Coverage:** 65% (80% required)

   **Action:** Merge blocked until coverage improves. See coverage gap report for uncovered lines.
   ```

### 1.9.4 TDD compliance uncertain

**Problem:**
Cannot definitively determine if TDD was followed.

**Symptoms:**

- Git history unclear
- No standard commit patterns
- Commits mixed (tests + implementation together)

**Possible causes:**

1. **Non-standard workflow:**
   - Developer doesn't use RED/GREEN prefixes
   - Squashed commits before push
   - Rebased and lost intermediate commits

2. **Pair programming:**
   - Multiple developers working together
   - Commits not atomic

3. **Migration of existing code:**
   - Tests added after code already written
   - Retroactive test addition

**Solutions:**

1. **Review all commits chronologically:**

   ```bash
   # Show detailed commit history
   git log --all --decorate --oneline --graph feature-branch

   # Show files changed in each commit
   git log --stat feature-branch
   ```

2. **Look for test files in early commits:**

   ```bash
   # Show when test files were created/modified
   git log --follow -- tests/test_feature.py

   # Compare timestamps
   git log --format="%H %ad %s" --date=iso feature-branch
   ```

3. **Ask developer for TDD evidence:**

   ```bash
   # Send AI Maestro message using the `agent-messaging` skill with:
   # - Recipient: `developer-agent`
   # - Subject: `TDD verification needed for PR #123`
   # - Priority: `high`
   # - Content: `{"type": "request", "message": "Cannot verify TDD compliance from git history. Please confirm: Were tests written before implementation? Can you provide evidence?"}`
   # - Verify: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.
   ```

4. **Document uncertainty:**

   ```markdown
   **Gate 1 (TDD Compliance):** UNCERTAIN

   **Analysis:** Git history does not clearly show RED-GREEN-REFACTOR pattern.

   **Observations:**
   - No commits with RED/GREEN prefixes
   - Tests and implementation appear in same commits
   - Possible squash or rebase before push

   **Developer Response Needed:**
   - Did you follow TDD (write tests first)?
   - Were intermediate commits squashed?
   - Can you provide evidence of TDD approach?

   **Recommendation:** Do not proceed until TDD compliance confirmed.
   ```

5. **Escalate to user if evidence lacking:**
   - If developer cannot provide TDD evidence
   - Treat as TDD violation
   - Request explicit approval to proceed

### 1.9.5 Conflicting coverage reports

**Problem:**
Different tools report different coverage percentages.

**Symptoms:**

- `pytest --cov` shows 85% coverage
- HTML report shows 78% coverage
- Different tools give different results

**Possible causes:**

1. **Different coverage scopes:**
   - One tool includes test files in coverage
   - One tool excludes certain directories
   - Configuration differs between tools

2. **Partial test runs:**
   - Coverage from incomplete test run cached
   - Different subsets of tests run

3. **Configuration differences:**
   - `.coveragerc` vs command-line options
   - `jest.config.js` vs package.json settings

**Solutions:**

1. **Use project's canonical coverage tool:**

   ```bash
   # Check project documentation for standard tool
   cat README.md | grep -i coverage

   # Check CI/CD configuration
   cat .github/workflows/test.yml | grep -i coverage
   ```

2. **Verify coverage scope:**

   ```bash
   # Python - check what's included
   pytest --cov=src --cov-report=term

   # Check .coveragerc
   cat .coveragerc
   ```

3. **Clear coverage cache:**

   ```bash
   # Python - remove old coverage data
   rm -f .coverage coverage.json
   rm -rf htmlcov/

   # JavaScript - remove old coverage
   rm -rf coverage/

   # Re-run coverage
   pytest --cov=src --cov-report=json
   ```

4. **Document discrepancy:**

   ```markdown
   **Coverage Discrepancy Detected:**

   - Tool A (pytest): 85% line coverage
   - Tool B (coverage.py): 78% line coverage

   **Resolution:** Using pytest (project standard) as canonical source.

   **Reported Coverage:** 85% (from pytest)
   ```

5. **Report lowest number:**
   - When in doubt, use the most conservative estimate
   - Document which tool was used
   - Explain why this tool chosen

6. **Standardize for future:**

   ```markdown
   **Recommendation:** Standardize coverage tool in project documentation.

   Add to README.md:
   ```bash
   # Standard coverage command
   pytest --cov=src --cov-report=term-missing
   ```

   Coverage reports from other tools should not be used for enforcement.

   ```

---

## Summary

This reference document covers all test engineering procedures for TDD enforcement:

1. **TDD Cycle Verification:** RED-GREEN-REFACTOR pattern validation via git history
2. **Coverage Validation:** Running coverage tools, checking thresholds, identifying gaps
3. **Test Quality Review:** Seven-dimension quality assessment beyond coverage metrics
4. **Quality Gates:** Three mandatory/advisory gates before code review
5. **TDD Workflow:** Six-step enforcement process from request to communication
6. **Rejection Criteria:** Automatic, conditional, and escalation scenarios
7. **Requirement Traceability:** Loading requirements, mapping to tests, gap detection
8. **Tools Usage:** Proper patterns for Read, Write, and Bash tools
9. **Troubleshooting:** Solutions for common test enforcement issues

These procedures form the operational knowledge base for the amia-test-engineer agent in the amia-tdd-enforcement skill.
