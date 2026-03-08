---
name: amia-tdd-enforcement
description: "Use when enforcing TDD via RED-GREEN-REFACTOR. No production code without a failing test first. Trigger with /enforce-tdd."
license: Apache-2.0
compatibility: Requires understanding of TDD principles, RED-GREEN-REFACTOR cycle, test frameworks, and version control. Works with any programming language that supports automated testing. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 2.0.0
agent: test-engineer
context: fork
user-invocable: false
---

# TDD Enforcement Skill

## Overview

This skill enforces Test-Driven Development (TDD) discipline through the RED-GREEN-REFACTOR cycle. It implements the Iron Law: **no production code can be written without a failing test that justifies its existence**.

## Prerequisites

- Understanding of TDD principles and RED-GREEN-REFACTOR cycle
- Test framework for the target language (pytest, Jest, cargo test, etc.)
- Version control (Git) for tracking TDD commits
- AI Maestro for delegating to Remote Developer Agents

## Instructions

1. **Write a failing test (RED)** - Create a test that documents the intended behavior. Run it to confirm it fails.
2. **Make the test pass (GREEN)** - Write the minimum code needed to make the test pass. Run all tests to confirm.
3. **Refactor the code (REFACTOR)** - Improve code quality while keeping all tests passing. Run tests after each refactoring step.
4. **Commit after each phase** - Use git commits with RED:/GREEN:/REFACTOR: prefixes to track progress.
5. **Return to RED for next feature** - After completing one cycle, start the next feature with a new failing test.

**Critical Rule**: Never write production code without a failing test first.

## Output

| Output Type | Description |
|-------------|-------------|
| TDD Status Report | Current phase status (`pending`, `RED`, `GREEN`, `refactor`) for each feature being developed |
| Git Commit Messages | Structured commits following pattern: `RED: test for [feature]`, `GREEN: implement [feature]`, `REFACTOR: improve [aspect]` |
| Test Execution Results | Pass/fail status of test suites after each phase transition |
| Enforcement Decisions | Allow/deny decisions for code changes based on TDD compliance (tests must exist before code) |
| Phase Transition Validation | Verification reports confirming proper RED→GREEN→REFACTOR cycle progression |
| Violation Reports | Documentation of TDD discipline violations with recovery procedures |
| Progress Tracking Updates | Multi-feature TDD cycle tracking with phase completion status |

### The Coordinator's Role

**This skill enforces TDD discipline on remote agents. The coordinator delegates testing and coding to developer agents — it verifies compliance, not performs implementation.**

**Coordinator Responsibilities:**

- **VERIFY** remote agents follow TDD (tests before code)
- **REVIEW** PRs to ensure TDD was followed
- **REJECT** work that violates TDD principles
- **DELEGATE** all test writing and code implementation to Remote Developer Agents via AI Maestro

### The TDD Cycle

TDD operates through three phases in strict order:

1. **RED**: Write a failing test that documents intended behavior
2. **GREEN**: Write minimum code to make the test pass
3. **REFACTOR**: Improve code quality while maintaining behavior

After completing one cycle, return to RED for the next feature.

### How to Use This Skill

This SKILL.md is a **map** to detailed reference documents. Each section below shows **when to read** each reference file. Click the links to access the full content.

---

## Core Principles

### The Iron Law ([references/iron-law.md](references/iron-law.md))

- When you need to understand the fundamental TDD principle → The Iron Law
- If you're unsure whether to write code → Pre-Code Checklist
- When evaluating if a change violates TDD → Violation Detection
- If you need to enforce TDD on remote agents → Enforcement Role

---

## The TDD Cycle

### RED-GREEN-REFACTOR Cycle ([references/red-green-refactor-cycle.md](references/red-green-refactor-cycle.md))

- When starting a new feature → Phase 1: RED
- If you have a failing test and need to implement → Phase 2: GREEN
- When all tests pass and code needs improvement → Phase 3: REFACTOR
- If you need to understand the complete cycle flow → Cycle Flow
- When completing one cycle and starting the next → Cycle Completion

### Status Tracking ([references/status-tracking.md](references/status-tracking.md))

- When you need to track TDD cycle progress → Status States
- If you need to document current phase → Status Tracking Format
- When managing multiple features → Multi-Feature Tracking
- If you need to verify phase transitions → Phase Transition Rules

---

## Implementation Guidance

### Step-by-Step Implementation ([references/implementation-procedure.md](references/implementation-procedure.md))

- When starting to implement a new feature → Step 1: Understand the Requirement
- If you need to write a failing test → Step 2: Write the Failing Test
- When you have a failing test and need to implement → Step 3: Make the Test Pass
- If tests pass and code needs improvement → Step 4: Refactor
- When you need test structure guidance → Test Structure Pattern

### Common Patterns ([references/common-patterns.md](references/common-patterns.md))

- When you need to understand what to test → Testing Behavior Not Implementation
- If your test has multiple assertions → One Assertion Per Test
- When structuring test code → Arrange-Act-Assert Pattern
- If you need to test edge cases → Edge Case Testing
- When dealing with dependencies → Dependency Isolation

---

## Rules and Enforcement

### Strict Rules ([references/rules-and-constraints.md](references/rules-and-constraints.md))

- When you need absolute rules that cannot be broken → The Iron Law (Absolute)
- If you're in RED phase and unsure what's allowed → Red Phase Rules
- If you're in GREEN phase and unsure what's allowed → Green Phase Rules
- If you're in REFACTOR phase and unsure what's allowed → Refactor Phase Rules
- When you need to know what actions are forbidden → Forbidden Actions

**Contents:**

- The Iron Law (Absolute)
- Rule 1: No Code Without a Failing Test
- Rule 2: Test Must Fail Before Implementation
- Rule 3: Only Modify Tests or Code, Never Both
- Red Phase Rules
- Allowed in RED Phase
- Forbidden in RED Phase
- RED Phase Checklist
- Green Phase Rules
- Allowed in GREEN Phase
- Forbidden in GREEN Phase
- GREEN Phase Checklist
- Refactor Phase Rules
- Allowed in REFACTOR Phase
- Forbidden in REFACTOR Phase
- REFACTOR Phase Checklist
- Forbidden Actions
- Never Allowed (Any Phase)
- Violation Recovery Procedure
- When You Realize You Violated TDD
- Enforcement Scripts
- Pre-Commit Hook
- Test-First Verification

---

## Problem Solving

### Troubleshooting ([references/troubleshooting.md](references/troubleshooting.md))

- If tests fail during refactoring → Test Fails During Refactoring
- When you can't write a failing test → Cannot Write a Failing Test
- If code passes test but seems wrong → Code Passes But Seems Wrong
- When refactoring takes too long → Refactoring Takes Too Long
- If test passes but code seems incomplete → Test Passes But Code Incomplete
- When test passes immediately → Test Passes on First Run
- If you're not sure what to test next → Unsure What to Test Next
- When tests become slow → Tests Are Too Slow

---

## Quick Reference

### Essential Checklist

Copy this checklist and track your progress:

**Before Writing ANY Production Code:**

- [ ] A failing test exists for this specific behavior
- [ ] The test has been run and actually fails
- [ ] The failure message is clear and measurable
- [ ] The test is committed with "RED: ..." message
- [ ] Status is marked as `RED`

**TDD Cycle Summary:**

1. **RED**: Write failing test → Commit → Mark as RED
2. **GREEN**: Write minimum code → All tests pass → Commit → Mark as GREEN
3. **REFACTOR**: Improve code → Tests still pass → Commit → Mark as REFACTOR
4. **Repeat**: Return to RED for next feature

**Git Commit Pattern:**

```
RED: test for [feature]
GREEN: implement [feature]
REFACTOR: improve [aspect] in [feature]
```

**Status States:**

- `pending` → Test being written
- `RED` → Test fails, needs implementation
- `GREEN` → Test passes, implementation complete
- `refactor` → Code improved, ready for next cycle

---

## Progressive Learning Path

**New to TDD? Read in this order:**

1. Start with [The Iron Law](references/iron-law.md) - understand the fundamental principle
   <!-- TOC: iron-law.md -->
   - Use-Case TOC
   - The Iron Law
   - Pre-Code Checklist
   <!-- /TOC -->
2. Read [RED-GREEN-REFACTOR Cycle](references/red-green-refactor-cycle.md) - understand the three phases
   <!-- TOC: red-green-refactor-cycle.md -->
   - Use-Case TOC
   - Phase 1: RED (Write Failing Test)
   - Phase 2: GREEN (Write Minimum Implementation)
   <!-- /TOC -->
3. Study [Implementation Procedure](references/implementation-procedure.md) - learn step-by-step process
   <!-- TOC: implementation-procedure.md -->
   - Use-Case TOC
   - Part 1: Writing Tests
   - Contents:
   <!-- /TOC -->
4. Review [Common Patterns](references/common-patterns.md) - learn good practices
   <!-- TOC: common-patterns.md -->
   - Use-Case TOC
   - Testing Behavior, Not Implementation
   - The Rule
   <!-- /TOC -->
5. Memorize [Rules and Constraints](references/rules-and-constraints.md) - know what's allowed
   <!-- TOC: rules-and-constraints.md -->
   - The Iron Law (Absolute)
   - Rule 1: No Code Without a Failing Test
   - Rule 2: Test Must Fail Before Implementation
   <!-- /TOC -->
6. Bookmark [Troubleshooting](references/troubleshooting.md) - for when things go wrong
   <!-- TOC: troubleshooting.md -->
   - Use-Case TOC
   - Part 1: Test Failures
   - Part 2: Code Issues
   <!-- /TOC -->
7. Use [Status Tracking](references/status-tracking.md) - track your progress
   <!-- TOC: status-tracking.md -->
   - Use-Case TOC
   - Status States
   - State Descriptions
   <!-- /TOC -->

**Enforcing TDD on Remote Agents?**

1. Read [Enforcement Role](references/iron-law.md#enforcement-role) - understand coordinator vs. agent responsibilities
2. Review [Phase Transition Rules](references/status-tracking.md#phase-transition-rules) - verify agent work
3. Use [Violation Recovery Procedure](references/rules-and-constraints.md#violation-recovery-procedure) - handle violations

---

## Summary

TDD Enforcement ensures quality through discipline:

- **Tests document behavior** - Every test is executable specification
- **Tests drive design** - Write test first, code second
- **Tests enable refactoring** - Change code confidently
- **Tests prevent regressions** - Old features keep working

**The Iron Law is absolute:** No code without a failing test.

**This skill enforces discipline**, remote agents execute the work.

Follow the cycle: **RED → GREEN → REFACTOR → Repeat**

---

## RULE 14: User Requirements Are Immutable

### TDD and Requirement Compliance

TDD enforcement MUST align with RULE 14:

1. **Tests Must Match Requirements**
   - Tests verify user-specified behavior
   - Tests use user-specified technologies
   - Tests validate requirement compliance

2. **Forbidden TDD Pivots**
   - ❌ "Requirement too complex, testing simpler version"
   - ❌ "Technology X hard to test, using Y instead"
   - ❌ "Skipping test for user-requested feature"

3. **Correct TDD Approach**
   - ✅ Test exactly what user specified
   - ✅ If feature hard to test, escalate (don't skip)
   - ✅ Tests trace to specific requirements

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

## Examples

### Example 1: TDD Cycle for New Feature

```bash
# Phase 1: RED - Write failing test
git add tests/test_user_auth.py
git commit -m "RED: test for user authentication"
# Run tests - should FAIL

# Phase 2: GREEN - Implement minimum code
git add src/auth.py
git commit -m "GREEN: implement user authentication"
# Run tests - should PASS

# Phase 3: REFACTOR - Improve code quality
git add src/auth.py
git commit -m "REFACTOR: extract password validation to separate function"
# Run tests - should still PASS
```

### Example 2: Verify TDD Compliance in PR

```bash
# Check commit history follows TDD pattern
git log --oneline | grep -E "^[a-f0-9]+ (RED|GREEN|REFACTOR):"

# Expected output:
# abc1234 REFACTOR: improve error messages
# def5678 GREEN: implement login endpoint
# 789abcd RED: test for login endpoint
```

## Error Handling

### Issue: Test passes on first run (RED phase failed)

**Cause**: Test is not testing the right thing or code already exists.

**Solution**: Ensure the test fails before writing implementation. If test passes immediately, either the test is wrong or you're not in a true RED state.

### Issue: Production code written without failing test

**Cause**: TDD discipline violation.

**Solution**: Revert the production code, write the failing test first, then reimplement. Use the Violation Recovery Procedure in [references/rules-and-constraints.md](references/rules-and-constraints.md).

**Contents:** The Iron Law (Absolute) · Rule 1: No Code Without a Failing Test · Rule 2: Test Must Fail Before Implementation · Violation Recovery Procedure · Forbidden Actions

### Issue: Refactoring breaks tests

**Cause**: Behavior changed during refactoring.

**Solution**: Refactoring must preserve behavior. Revert to GREEN state and try smaller refactoring steps.

## Resources

- [references/iron-law.md](references/iron-law.md) - The fundamental TDD principle
  <!-- TOC: iron-law.md -->
  - Use-Case TOC
  - The Iron Law
  - Pre-Code Checklist
  <!-- /TOC -->
- [references/red-green-refactor-cycle.md](references/red-green-refactor-cycle.md) - Cycle details
  <!-- TOC: red-green-refactor-cycle.md -->
  - Use-Case TOC
  - Phase 1: RED (Write Failing Test)
  - Phase 2: GREEN (Write Minimum Implementation)
  <!-- /TOC -->
- [references/implementation-procedure.md](references/implementation-procedure.md) - Step-by-step guide
  <!-- TOC: implementation-procedure.md -->
  - Use-Case TOC
  - Part 1: Writing Tests
  - Contents:
  <!-- /TOC -->
- [references/common-patterns.md](references/common-patterns.md) - TDD best practices
  <!-- TOC: common-patterns.md -->
  - Use-Case TOC
  - Testing Behavior, Not Implementation
  - The Rule
  <!-- /TOC -->
- [references/rules-and-constraints.md](references/rules-and-constraints.md) - Strict rules
  <!-- TOC: rules-and-constraints.md -->
  - The Iron Law (Absolute)
  - Rule 1: No Code Without a Failing Test
  - Rule 2: Test Must Fail Before Implementation
  <!-- /TOC -->
- [references/troubleshooting.md](references/troubleshooting.md) - Problem solving
  <!-- TOC: troubleshooting.md -->
  - Use-Case TOC
  - Part 1: Test Failures
  - Part 2: Code Issues
  <!-- /TOC -->
- [references/status-tracking.md](references/status-tracking.md) - Progress tracking
  <!-- TOC: status-tracking.md -->
  - Use-Case TOC
  - Status States
  - State Descriptions
  <!-- /TOC -->
- [references/test-engineering.md](references/test-engineering.md) - Test engineering procedures from AMIA Test Engineer
  <!-- TOC: test-engineering.md -->
  - 1 When verifying TDD cycle compliance (RED-GREEN-REFACTOR pattern)
  - 1 RED Phase verification checklist
  - 2 GREEN Phase verification checklist
  <!-- /TOC -->
