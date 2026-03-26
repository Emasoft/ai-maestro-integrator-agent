# Code Review Workflow Reference

## Table of Contents

- 1. When starting a code review task
  - 1.1 Receiving and parsing review requests
  - 1.2 Extracting PR metadata and specifications
- 1. When gathering context before review
  - 2.1 Loading specification documents
  - 2.2 Reading changed files and test files
  - 2.3 Collecting previous review comments
- 1. When executing Gate 1: Specification Compliance
  - 3.1 Verifying user requirements compliance
  - 3.2 Checking functional requirements match
  - 3.3 Validating architectural compliance
  - 3.4 Assessing interface contracts
  - 3.5 Determining Gate 1 outcome (PASS/FAIL/BLOCKED)
- 1. When executing Gate 2: Code Quality Evaluation
  - 4.1 Evaluating correctness and security
  - 4.2 Assessing performance and maintainability
  - 4.3 Checking reliability and style compliance
  - 4.4 Running automated analysis tools
  - 4.5 Determining Gate 2 outcome (PASS/FAIL/CONDITIONAL)
- 1. When generating review reports
  - 5.1 Creating structured review reports
  - 5.2 Documenting findings with 80%+ confidence
  - 5.3 Saving reports to correct locations
- 1. When creating fix instructions for developers
  - 6.1 Writing WHAT/WHY/WHERE descriptions
  - 6.2 Specifying verification criteria
  - 6.3 Avoiding code examples and implementations
- 1. When communicating findings via AI Maestro
  - 7.1 Formatting AI Maestro messages
  - 7.2 Including report file references
- 1. When updating GitHub Projects tracking
  - 8.1 Adding PR labels
  - 8.2 Updating project board status
  - 8.3 Posting PR summary comments
- 1. When archiving review artifacts
  - 9.1 Saving review reports and fix instructions
  - 9.2 Creating JSON log entries
  - 9.3 Preparing minimal orchestrator output

---

## 1. When Starting a Code Review Task

### 1.1 Receiving and Parsing Review Requests

**Step 1: Receive Review Request**

When the orchestrator assigns a code review task, extract:

- **PR number**: Unique identifier for the pull request
- **PR files**: List of changed files in the PR
- **Specification reference**: Path to requirement/design documents
- **Priority**: Review urgency (critical/high/normal/low)

**Example Request Format:**

```
Review PR #123 for the new authentication module against the security specifications
```

### 1.2 Extracting PR Metadata and Specifications

Use Bash tool to query GitHub API for PR details:

```bash
gh pr view 123 --json number,files,body,labels
```

Extract:

- Changed file paths
- PR description/body
- Existing labels
- Related issues

---

## 2. When Gathering Context Before Review

### 2.1 Loading Specification Documents

**Step 2: Gather Context**

**CRITICAL: ALWAYS load USER_REQUIREMENTS.md first**

1. Read `docs_dev/requirements/USER_REQUIREMENTS.md`
2. Understand original user specifications
3. Prepare requirement checklist (each requirement = review criterion)

**What to extract from specifications:**

- Technology choices specified by user
- Scope and features requested
- Architecture requirements
- Interface contracts
- Quality criteria

### 2.2 Reading Changed Files and Test Files

For each file in the PR:

1. Use Read tool to access file content
2. Understand code structure and logic
3. Identify dependencies and imports
4. Check for test coverage

### 2.3 Collecting Previous Review Comments

Check for prior review feedback:

```bash
gh pr view 123 --json comments
```

Review history helps identify:

- Recurring issues
- Already addressed concerns
- Developer response patterns

---

## 3. When Executing Gate 1: Specification Compliance

**Gate 1 must PASS before Gate 2 begins.**

### 3.1 Verifying User Requirements Compliance

**CRITICAL: Code reviews MUST verify requirement compliance**

For each PR/code change, verify:

- [ ] **Technology matches specification** - User said "Electron app", code IS Electron app
- [ ] **Scope matches specification** - All features user requested are implemented
- [ ] **No unauthorized substitutions** - CLI doesn't replace GUI unless user approved
- [ ] **No unauthorized scope reduction** - Features not removed to "simplify"

**If code deviates from user requirements:**

```
[REVIEW BLOCKED] Requirement Violation Detected

User Requirement: [exact quote]
Code Implementation: [what was actually done]
Violation Type: [Technology Change / Scope Reduction / Feature Omission]

This PR cannot be approved until user reviews the deviation.
See: docs_dev/requirement-issues/{timestamp}-violation.md
```

### 3.2 Checking Functional Requirements Match

Verify:

- All user-requested features are implemented
- No features are missing or replaced
- Feature behavior matches specifications
- Edge cases are handled as specified

### 3.3 Validating Architectural Compliance

Check:

- Code structure follows specified architecture
- Design patterns match requirements
- Module boundaries are respected
- Dependencies align with specifications

### 3.4 Assessing Interface Contracts

Verify:

- API contracts match specifications
- Function signatures are correct
- Data structures match requirements
- Error handling follows specifications

### 3.5 Determining Gate 1 Outcome

**Gate 1 Outcomes:**

- **PASS:** All specification requirements met → Proceed to Gate 2
- **FAIL:** Specification violations found → Generate Fix Instructions, STOP (no Gate 2)
- **BLOCKED:** Cannot verify (missing specs) → Request clarification, STOP

**Pass Criteria:**

- All functional requirements implemented
- Architecture matches specifications
- No unauthorized technology changes
- No scope reductions without approval

**Fail Actions:**

- Generate Fix Instructions document
- STOP review (do NOT proceed to Gate 2)
- Notify developer via AI Maestro
- Update GitHub with "spec-violation" label

---

## 4. When Executing Gate 2: Code Quality Evaluation

**Only execute Gate 2 if Gate 1 PASSED.**

### 4.1 Evaluating Correctness and Security

**Correctness:**

- Logic errors or bugs
- Edge case handling
- Error propagation
- Data validation

**Security:**

- Input validation
- SQL injection risks
- XSS vulnerabilities
- Authentication/authorization
- Sensitive data exposure

### 4.2 Assessing Performance and Maintainability

**Performance:**

- Algorithmic efficiency
- Resource usage (memory, CPU)
- Database query optimization
- Unnecessary computations

**Maintainability:**

- Code readability
- Documentation quality
- Complexity (cyclomatic)
- Modularity and coupling

### 4.3 Checking Reliability and Style Compliance

**Reliability:**

- Error handling
- Logging practices
- Test coverage
- Fail-safe mechanisms

**Style Compliance:**

- Naming conventions
- Code formatting
- Comment quality
- Project patterns

### 4.4 Running Automated Analysis Tools

Use Bash tool to execute:

**Python:**

```bash
ruff check path/to/file.py
mypy path/to/file.py
bandit -r path/to/
```

**JavaScript/TypeScript:**

```bash
eslint path/to/file.js
tsc --noEmit path/to/file.ts
```

**All findings must have 80%+ confidence to be included.**

### 4.5 Determining Gate 2 Outcome

**Gate 2 Outcomes:**

- **PASS:** No critical issues, quality standards met → Approve PR
- **FAIL:** Critical issues found → Generate Fix Instructions
- **CONDITIONAL:** Minor issues, recommendations only → Document for future
- **SKIPPED:** Gate 1 failed, Gate 2 not executed

**Pass Criteria:**

- No critical security vulnerabilities
- No correctness bugs
- Code meets quality standards
- Automated tools pass

**Fail Actions:**

- Generate Fix Instructions document
- Notify developer via AI Maestro
- Update GitHub with "needs-fixes" label
- Block PR approval

---

## 5. When Generating Review Reports

### 5.1 Creating Structured Review Reports

**Step 5: Generate Review Report**

Save report to: `reports/code-review-PR{number}-{timestamp}.md`

**Report Structure:**

```markdown
# Code Review Report - PR#{number}

**Date:** {timestamp}
**Reviewer:** amia-code-reviewer
**PR:** #{number}
**Files Reviewed:** {count}

## Review Outcome

**Gate 1 (Specification Compliance):** PASS/FAIL/BLOCKED
**Gate 2 (Code Quality):** PASS/FAIL/CONDITIONAL/SKIPPED
**Overall Status:** APPROVED/REJECTED/BLOCKED

## Gate 1 Findings

[Specification compliance issues, if any]

## Gate 2 Findings

### Critical Issues ({count})
[Issues blocking approval]

### Major Issues ({count})
[Issues requiring attention]

### Minor Issues ({count})
[Recommendations and improvements]

## Verification Criteria

[Criteria for confirming fixes]

## Approval Status

[APPROVED / REJECTED / BLOCKED with reasoning]
```

### 5.2 Documenting Findings with 80%+ Confidence

**Each finding must include:**

- **What:** Precise description of the issue
- **Where:** File, line number, function name
- **Why:** Explanation of why it's wrong
- **Confidence:** 80%+ or do NOT include
- **Severity:** Critical/Major/Minor
- **Reference:** Specification or standard violated

**Example Finding:**

```
Issue: Missing input validation in user authentication
Location: src/auth.py, line 45, function authenticate_user()
Severity: CRITICAL
Confidence: 95%
Why: User input is directly used in SQL query without sanitization,
     creating SQL injection vulnerability (OWASP Top 10).
Reference: Security Specification section 3.2
```

### 5.3 Saving Reports to Correct Locations

**Artifact Locations:**

| Artifact | Location |
|----------|----------|
| Review Report | `reports/code-review-PR{number}-{timestamp}.md` |
| Fix Instructions | `fix-instructions/fix-instructions-PR{number}-{timestamp}.md` |
| JSON Log | `logs/review-log-PR{number}-{timestamp}.json` |

---

## 6. When Creating Fix Instructions for Developers

### 6.1 Writing WHAT/WHY/WHERE Descriptions

**Step 6: Create Fix Instructions**

Save to: `fix-instructions/fix-instructions-PR{number}-{timestamp}.md`

**DO Include:**

- **WHAT is wrong:** Clear description of the issue
- **WHY it's wrong:** Explanation and reasoning
- **WHERE:** File path, line number, function name
- **REFERENCE:** Specification section violated
- **VERIFICATION:** How to confirm the fix is correct
- **CONFIDENCE:** 80%+ confidence level

**Example Good Fix Instruction:**

```
Issue: Missing input validation in authentication

What: User input from the login form is not validated before use
Why: This creates SQL injection vulnerability (OWASP Top 10 #1)
Where: src/auth.py, line 45, authenticate_user() function
Reference: Security Specification section 3.2 "Input Validation"
Verification: After fix, run security tests in tests/test_auth_security.py
             All tests must pass. Run bandit scan - zero SQL injection warnings.
Confidence: 95%
```

### 6.2 Specifying Verification Criteria

For each fix instruction, state HOW to verify the fix:

- **Test command:** Specific test to run
- **Expected result:** What passing looks like
- **Tool verification:** Static analysis checks
- **Manual verification:** Review steps if needed

### 6.3 Avoiding Code Examples and Implementations

**DO NOT Include:**

- Code examples showing how to fix
- Pseudocode implementations
- Specific function signatures
- Algorithm suggestions
- Library recommendations
- Coding patterns

**Why:** The reviewer NEVER writes code. Remote developers implement fixes based on WHAT/WHY/WHERE descriptions only.

**Bad Example (Avoid):**

```python
# Add input validation like this:
def authenticate_user(username, password):
    if not validate_username(username):  # DON'T DO THIS
        raise ValueError("Invalid username")
```

**Good Example:**

```
Issue: Missing username validation

What: Username input is not validated before database query
Why: Allows special characters that could enable SQL injection
Where: src/auth.py, line 45, authenticate_user() function
Verification: After fix, run tests/test_auth_security.py::test_username_validation
```

---

## 7. When Communicating Findings via AI Maestro

### 7.1 Formatting AI Maestro Messages

**Step 7: Communicate with Developer**

Send a message to the remote developer agent using the `agent-messaging` skill with:

- **Recipient**: `developer-agent-name`
- **Subject**: `PR#123 Review Complete - Fixes Required`
- **Priority**: `high`
- **Content**: `{"type": "code-review", "message": "PR#123 review complete. Gate 1: PASS, Gate 2: FAIL\n5 issues found (2 critical)\nFix instructions: fix-instructions/fix-instructions-PR123-{timestamp}.md"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 7.2 Including Report File References

**Message Content Guidelines:**

- Include PR number
- State Gate 1 and Gate 2 outcomes
- Summarize issue count and severity
- Provide file path to fix instructions
- Set appropriate priority (critical/high/normal)

---

## 8. When Updating GitHub Projects Tracking

### 8.1 Adding PR Labels

**Step 8: Update GitHub Projects**

Add appropriate labels based on review outcome:

```bash
# Gate 1 FAIL
gh pr edit 123 --add-label "spec-violation"

# Gate 2 FAIL
gh pr edit 123 --add-label "needs-fixes"

# PASS both gates
gh pr edit 123 --add-label "approved"
```

### 8.2 Updating Project Board Status

Move PR card on GitHub Projects board:

```bash
gh project item-edit --project-id PROJECT_ID \
  --field "Status" --value "AI Review"
```

### 8.3 Posting PR Summary Comments

Post review summary to PR:

```bash
gh pr comment 123 --body "Code Review Complete

**Gate 1 (Spec Compliance):** PASS
**Gate 2 (Code Quality):** FAIL
**Issues Found:** 5 (2 critical)

See full report: reports/code-review-PR123-{timestamp}.md
Fix instructions: fix-instructions/fix-instructions-PR123-{timestamp}.md"
```

---

## 9. When Archiving Review Artifacts

### 9.1 Saving Review Reports and Fix Instructions

**Step 9: Archive and Log**

Ensure all artifacts are saved:

- Review report in `reports/`
- Fix instructions in `fix-instructions/`
- JSON log in `logs/`

### 9.2 Creating JSON Log Entries

Create structured log:

```json
{
  "timestamp": "2025-12-30T14:00:00Z",
  "pr_number": 123,
  "reviewer": "amia-code-reviewer",
  "gate1_outcome": "PASS",
  "gate2_outcome": "FAIL",
  "issues_found": 5,
  "critical_issues": 2,
  "report_path": "reports/code-review-PR123-20251230140000.md",
  "fix_instructions_path": "fix-instructions/fix-instructions-PR123-20251230140000.md"
}
```

### 9.3 Preparing Minimal Orchestrator Output

**Return to orchestrator with minimal report:**

```
[DONE/FAILED] code-reviewer - PR#{number} {GATE1_STATUS}/{GATE2_STATUS}
Key finding: {total_issues} issues ({critical_issues} critical)
Details: reports/code-review-PR{number}-{timestamp}.md
```

**Example Outputs:**

**Approved:**

```
[DONE] code-reviewer - PR#123 PASS/PASS
Key finding: 0 issues, approved
Details: reports/code-review-PR123-20251230103000.md
```

**Rejected:**

```
[DONE] code-reviewer - PR#456 FAIL/SKIPPED
Key finding: 5 issues (2 critical), spec violations
Details: reports/code-review-PR456-20251230140000.md
```

**Blocked:**

```
[FAILED] code-reviewer - PR#789 BLOCKED/SKIPPED
Key finding: Missing specification document
Details: reports/code-review-PR789-20251230160000.md
```

**NEVER include:**

- Full review report content
- Code snippets
- Detailed findings
- Multi-paragraph explanations

**Keep output under 3 lines. Orchestrator will read full report from file if needed.**

---

## Review Completion Checklist

Before returning to orchestrator, verify ALL items complete:

- [ ] Review request metadata extracted (PR number, files, spec, priority)
- [ ] All specification documents read
- [ ] All changed files read
- [ ] Gate 1 checklist executed and scored
- [ ] Gate 1 outcome determined (PASS/FAIL/BLOCKED)
- [ ] Gate 2 executed (if Gate 1 passed) or skipped (if Gate 1 failed)
- [ ] Gate 2 outcome determined (PASS/FAIL/CONDITIONAL/SKIPPED)
- [ ] All findings have 80%+ confidence
- [ ] Review report generated and saved
- [ ] Fix instructions document created (if needed)
- [ ] AI Maestro message sent to developer
- [ ] GitHub PR labels updated
- [ ] GitHub Projects board status updated
- [ ] GitHub PR summary comment posted
- [ ] Review artifacts archived
- [ ] JSON log entry created
- [ ] Minimal output report prepared for orchestrator

**If ANY item is incomplete, do NOT return to orchestrator.**

---

## Approval Criteria Summary

**Code-reviewer CANNOT approve PRs that:**

- Change user-specified technology
- Reduce user-specified scope
- Omit user-requested features
- Implement "simpler alternatives" without user approval

**These MUST be escalated to user for decision.**

**Code-reviewer CAN approve PRs when:**

- Gate 1: All specification requirements met
- Gate 2: All quality standards met
- All critical issues resolved
- Automated tools pass
- 80%+ confidence in approval decision
