# TDD Enforcement Skill — Detailed Guide

## Table of Contents

- [Coordinator Role](#coordinator-role)
- [TDD Cycle Details](#tdd-cycle-details)
- [Core Principles Navigation](#core-principles-navigation)
- [Implementation Guidance Navigation](#implementation-guidance-navigation)
- [Rules and Enforcement Navigation](#rules-and-enforcement-navigation)
- [Problem Solving Navigation](#problem-solving-navigation)
- [Progressive Learning Path](#progressive-learning-path)
- [RULE 14 Requirement Compliance](#rule-14-requirement-compliance)
- [Error Handling](#error-handling)

## Coordinator Role

**This skill enforces TDD discipline on remote agents. The coordinator delegates testing and coding to developer agents — it verifies compliance, not performs implementation.**

**Coordinator Responsibilities:**

- **VERIFY** remote agents follow TDD (tests before code)
- **REVIEW** PRs to ensure TDD was followed
- **REJECT** work that violates TDD principles
- **DELEGATE** all test writing and code implementation to Remote Developer Agents via AI Maestro

## TDD Cycle Details

TDD operates through three phases in strict order:

1. **RED**: Write a failing test that documents intended behavior
2. **GREEN**: Write minimum code to make the test pass
3. **REFACTOR**: Improve code quality while maintaining behavior

After completing one cycle, return to RED for the next feature.

## Core Principles Navigation

### The Iron Law (`references/iron-law.md`)

- When you need to understand the fundamental TDD principle -> The Iron Law
- If you're unsure whether to write code -> Pre-Code Checklist
- When evaluating if a change violates TDD -> Violation Detection
- If you need to enforce TDD on remote agents -> Enforcement Role

## Implementation Guidance Navigation

### Step-by-Step Implementation (`references/implementation-procedure.md`)

- When starting to implement a new feature -> Step 1: Understand the Requirement
- If you need to write a failing test -> Step 2: Write the Failing Test
- When you have a failing test and need to implement -> Step 3: Make the Test Pass
- If tests pass and code needs improvement -> Step 4: Refactor
- When you need test structure guidance -> Test Structure Pattern

### Common Patterns (`references/common-patterns.md`)

- When you need to understand what to test -> Testing Behavior Not Implementation
- If your test has multiple assertions -> One Assertion Per Test
- When structuring test code -> Arrange-Act-Assert Pattern
- If you need to test edge cases -> Edge Case Testing
- When dealing with dependencies -> Dependency Isolation

## Rules and Enforcement Navigation

### Strict Rules (`references/rules-and-constraints.md`)

- When you need absolute rules that cannot be broken -> The Iron Law (Absolute)
- If you're in RED phase and unsure what's allowed -> Red Phase Rules
- If you're in GREEN phase and unsure what's allowed -> Green Phase Rules
- If you're in REFACTOR phase and unsure what's allowed -> Refactor Phase Rules
- When you need to know what actions are forbidden -> Forbidden Actions

**Contents:**

- The Iron Law (Absolute)
- Rule 1: No Code Without a Failing Test
- Rule 2: Test Must Fail Before Implementation
- Rule 3: Only Modify Tests or Code, Never Both
- Red Phase Rules (Allowed / Forbidden / Checklist)
- Green Phase Rules (Allowed / Forbidden / Checklist)
- Refactor Phase Rules (Allowed / Forbidden / Checklist)
- Forbidden Actions (Never Allowed in Any Phase)
- Violation Recovery Procedure
- Enforcement Scripts (Pre-Commit Hook, Test-First Verification)

## Problem Solving Navigation

### Troubleshooting (`references/troubleshooting.md`)

- If tests fail during refactoring -> Test Fails During Refactoring
- When you can't write a failing test -> Cannot Write a Failing Test
- If code passes test but seems wrong -> Code Passes But Seems Wrong
- When refactoring takes too long -> Refactoring Takes Too Long
- If test passes but code seems incomplete -> Test Passes But Code Incomplete
- When test passes immediately -> Test Passes on First Run
- If you're not sure what to test next -> Unsure What to Test Next
- When tests become slow -> Tests Are Too Slow

## Progressive Learning Path

**New to TDD? Read in this order:**

1. `references/iron-law.md` — understand the fundamental principle
2. `references/red-green-refactor-cycle.md` — understand the three phases
3. `references/implementation-procedure.md` — learn step-by-step process
4. `references/common-patterns.md` — learn good practices
5. `references/rules-and-constraints.md` — know what's allowed
6. `references/troubleshooting.md` — for when things go wrong
7. `references/status-tracking.md` — track your progress

**Enforcing TDD on Remote Agents?**

1. Read Enforcement Role in `references/iron-law.md` — understand coordinator vs. agent responsibilities
2. Review Phase Transition Rules in `references/status-tracking.md` — verify agent work
3. Use Violation Recovery Procedure in `references/rules-and-constraints.md` — handle violations

## RULE 14 Requirement Compliance

### TDD and Requirement Compliance

TDD enforcement MUST align with RULE 14:

1. **Tests Must Match Requirements**
   - Tests verify user-specified behavior
   - Tests use user-specified technologies
   - Tests validate requirement compliance

2. **Forbidden TDD Pivots**
   - "Requirement too complex, testing simpler version"
   - "Technology X hard to test, using Y instead"
   - "Skipping test for user-requested feature"

3. **Correct TDD Approach**
   - Test exactly what user specified
   - If feature hard to test, escalate (don't skip)
   - Tests trace to specific requirements

### Test-Requirement Traceability

Every test file SHOULD include:

```python
# Tests for REQ-003: "User specified exact output format"
def test_output_format_matches_requirement():
    # Verifies: REQ-003
    ...
```

### When Tests Reveal Requirement Issues

If writing tests reveals a requirement problem:

1. STOP test writing
2. Document the issue
3. Generate Requirement Issue Report
4. WAIT for user decision
5. Resume with user's chosen direction

### TDD Phase Requirement Checks

| TDD Phase | Requirement Check |
|-----------|-------------------|
| RED | Is this testing what user actually asked for? |
| GREEN | Does implementation match user's specification? |
| REFACTOR | Does refactoring preserve user's requirements? |

## Error Handling

### Issue: Test passes on first run (RED phase failed)

**Cause**: Test is not testing the right thing or code already exists.

**Solution**: Ensure the test fails before writing implementation. If test passes immediately, either the test is wrong or you're not in a true RED state.

### Issue: Production code written without failing test

**Cause**: TDD discipline violation.

**Solution**: Revert the production code, write the failing test first, then reimplement. Use the Violation Recovery Procedure in `references/rules-and-constraints.md`.

### Issue: Refactoring breaks tests

**Cause**: Behavior changed during refactoring.

**Solution**: Refactoring must preserve behavior. Revert to GREEN state and try smaller refactoring steps.

## Complete Reference Document Index

**Core Principles:**

- `references/iron-law.md` — Fundamental TDD principle, pre-code checklist
- `references/red-green-refactor-cycle.md` — RED-GREEN-REFACTOR cycle phases

**Implementation:**

- `references/implementation-procedure.md` — Step-by-step TDD guide
- `references/implementation-procedure-part1-writing-tests.md` — Writing tests
- `references/implementation-procedure-part1-test-creation.md` — Test creation
- `references/implementation-procedure-part2-implementation-refactor.md` — Implementation and refactor
- `references/implementation-procedure-part3-complete-example.md` — Worked example
- `references/common-patterns.md` — Best practices (AAA, edge cases, isolation)

**Rules and Enforcement:**

- `references/rules-and-constraints.md` — Phase rules, forbidden actions, violation recovery
- `references/status-tracking.md` — Status states, phase transitions, multi-feature tracking

**Operations:**

- `references/op-write-failing-test.md` — Write a failing test
- `references/op-implement-minimum-code.md` — Implement minimum code
- `references/op-refactor-code.md` — Refactor code
- `references/op-verify-tdd-compliance.md` — Verify TDD compliance
- `references/op-handle-tdd-violation.md` — Handle TDD violations

**Troubleshooting:**

- `references/troubleshooting.md` — Problem solving index
- `references/troubleshooting-part1-test-failures.md` — Test failure issues
- `references/troubleshooting-part2-code-issues.md` — Code-level issues
- `references/troubleshooting-part3-passing-tests.md` — Unexpected passes
- `references/troubleshooting-part4-workflow.md` — Workflow issues

**Other:**

- `references/test-engineering.md` — Test engineering procedures from AMIA Test Engineer
- `references/detailed-guide.md` — Extended guidance, learning paths, RULE 14 compliance
