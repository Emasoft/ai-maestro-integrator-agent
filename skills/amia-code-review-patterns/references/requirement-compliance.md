# Requirement Compliance (Gate 0)

## Table of Contents

- 5.1 Gate 0: Requirement Compliance Overview
- 5.2 Gate 0 Checklist Template
- 5.3 Review Checklist Additions
  - 5.3.1 Requirement Traceability
  - 5.3.2 Technology Compliance
  - 5.3.3 Scope Compliance
- 5.4 Forbidden Review Approvals
- 5.5 Correct Review Approach

---

## 5.1 Gate 0: Requirement Compliance Overview

**CRITICAL RULE**: User Requirements Are Immutable

BEFORE evaluating code quality, security, or tests, you MUST first verify that the PR implements what the user requested.

Gate 0 ensures:
- The PR implements user-specified features
- The PR uses user-specified technologies
- No unauthorized scope changes occurred
- No technology substitutions were made

---

## 5.2 Gate 0 Checklist Template

```markdown
## Gate 0: Requirement Compliance

| Check | Status |
|-------|--------|
| PR implements user-specified features | [YES/NO] |
| PR uses user-specified technologies | [YES/NO] |
| No unauthorized scope changes | [YES/NO] |
| No technology substitutions | [YES/NO] |

Gate 0 Verdict: [PASS/FAIL]
```

**If Gate 0 FAILS:**
1. STOP review immediately
2. Generate Requirement Issue Report
3. PR cannot proceed until user decides

---

## 5.3 Review Checklist Additions

### 5.3.1 Requirement Traceability

For every PR, verify:

- Does every code change trace to a documented requirement?
- Are there changes without requirement backing?
- Can you identify which requirement each file change addresses?

**Red flags:**
- Changes that do not map to any requirement
- Requirements marked as complete but not fully implemented
- Extra features not in the original specification

### 5.3.2 Technology Compliance

For every PR, verify:

- Does the PR use the technologies specified by the user?
- Were any libraries or frameworks substituted without approval?
- Are dependency choices consistent with project requirements?

**Red flags:**
- Different language or framework than specified
- Unauthorized library substitutions (e.g., axios instead of specified fetch)
- Technology choices made for developer convenience vs. user requirements

### 5.3.3 Scope Compliance

For every PR, verify:

- Does the PR implement exactly what was requested?
- Is there scope creep (extra features not requested)?
- Is there scope reduction (features removed or incomplete)?

**Red flags:**
- Features added without user request
- Requested features missing or incomplete
- Scope changes without documented approval

---

## 5.4 Forbidden Review Approvals

NEVER approve a PR that:

- Uses different technology than user specified
- Reduces scope from requirements
- "Improves" beyond user request without approval
- Has unresolved requirement issues
- Contains undocumented scope changes
- Substitutes requested functionality with alternatives

---

## 5.5 Correct Review Approach

The correct review approach ensures:

- Gate 0 passes before other gates are evaluated
- All changes trace to documented requirements
- Technology matches specification exactly
- Scope matches exactly (no additions, no reductions)

**Review Order:**
1. Gate 0: Requirement Compliance (MUST PASS FIRST)
2. Stage One: Quick Scan
3. Stage Two: Deep Dive
4. Final Decision

If Gate 0 fails, do NOT proceed to Quick Scan. The fundamental contract with the user must be satisfied before code quality matters.
