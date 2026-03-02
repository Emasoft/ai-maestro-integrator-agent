# The Iron Law of TDD

## Table of Contents
- [Use-Case TOC](#use-case-toc)
- [The Iron Law](#the-iron-law)
- [Pre-Code Checklist](#pre-code-checklist)
- [Violation Detection](#violation-detection)
  - [Signs of Iron Law Violation](#signs-of-iron-law-violation)
- [Enforcement Role](#enforcement-role)
  - [Orchestrator Responsibilities](#orchestrator-responsibilities)
  - [Remote Agent Instructions](#remote-agent-instructions)
  - [Verification Checklist](#verification-checklist)

---

## Use-Case TOC
- When you need to understand the fundamental TDD principle → [The Iron Law](#the-iron-law)
- If you're unsure whether to write code → [Pre-Code Checklist](#pre-code-checklist)
- When evaluating if a change violates TDD → [Violation Detection](#violation-detection)
- If you need to enforce TDD on remote agents → [Enforcement Role](#enforcement-role)

---

## The Iron Law

**No code without a failing test.**

This is the fundamental principle that governs all development under TDD enforcement. Before writing any production code:

1. A test must exist that currently fails
2. That test must document the intended behavior
3. The test failure must be visible and measurable
4. Only then can production code be written to make it pass

Violating this law means reverting the code and starting the cycle over.

## Pre-Code Checklist

Before writing ANY production code, verify:

- [ ] A test exists for this specific behavior
- [ ] The test has been run and actually fails
- [ ] The failure message is clear and measurable
- [ ] The test is committed to version control
- [ ] Status is marked as `RED`

If ANY item is unchecked, **STOP**. Do not write production code.

## Violation Detection

### Signs of Iron Law Violation

**Code written without a test:**
- Production methods/functions exist with no corresponding test
- Code changes made without a new failing test
- Speculative code added "for future use"
- Edge cases handled without tests

**Test written after code:**
- Git history shows production code committed before test
- Test passes immediately upon first run (suspicious)
- Developer admits "I'll write the test later"

**Action on Violation:**
1. Identify the untested code
2. Delete or revert the code
3. Write the failing test first
4. Re-implement the code following TDD cycle

## Enforcement Role

**The orchestrator ENFORCES TDD discipline on remote agents. The orchestrator NEVER writes tests or code itself.**

### Orchestrator Responsibilities

**Verify remote agents follow TDD:**
- Check git history for RED-GREEN-REFACTOR commits
- Ensure tests were committed before implementation
- Verify test failures before code changes

**Review PRs to ensure TDD was followed:**
- Examine commit sequence
- Check for test-first pattern
- Look for RED → GREEN → REFACTOR progression

**Reject work that violates TDD principles:**
- Request revert of code-first commits
- Require proper test-first cycle
- Do not merge PRs without TDD evidence

**NEVER write tests or production code itself:**
- All actual test writing → Remote Developer Agents via AI Maestro
- All code implementation → Remote Developer Agents via AI Maestro
- Orchestrator only enforces, reviews, and directs

### Remote Agent Instructions

When delegating to remote developer agents via AI Maestro:

```markdown
Task: Implement feature X following TDD

Requirements:
1. Write failing test first (RED phase)
2. Commit test with message: "RED: test for feature X"
3. Run test and verify it fails
4. Implement minimum code to pass test (GREEN phase)
5. Commit code with message: "GREEN: implement feature X"
6. Refactor if needed (REFACTOR phase)
7. Commit refactoring with message: "REFACTOR: improve feature X"
8. Report back with commit SHAs for verification

Do NOT write code before test. Do NOT skip any phase.
```

### Verification Checklist

After remote agent completes work:

- [ ] Test commit exists before implementation commit
- [ ] Test actually fails in RED commit
- [ ] Implementation commit makes test pass
- [ ] All existing tests still pass
- [ ] Refactor commits maintain passing tests
- [ ] Git history shows proper TDD sequence
