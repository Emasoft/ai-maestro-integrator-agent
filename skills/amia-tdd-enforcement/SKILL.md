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

Enforces Test-Driven Development discipline through the RED-GREEN-REFACTOR cycle. The Iron Law: **no production code without a failing test first**. The coordinator verifies compliance on remote agents — it delegates, not implements.

## Prerequisites

- Test framework for the target language (pytest, Jest, cargo test, etc.)
- Version control (Git) for tracking TDD commits
- AI Maestro for delegating to Remote Developer Agents

## Instructions

1. **Write a failing test (RED)** — Create a test documenting intended behavior. Run it to confirm it fails.
2. **Make the test pass (GREEN)** — Write minimum code to pass the test. Run all tests.
3. **Refactor (REFACTOR)** — Improve code quality, keep all tests passing.
4. **Commit after each phase** — Use `RED:`/`GREEN:`/`REFACTOR:` prefixes.
5. **Return to RED** — Start the next feature with a new failing test.

**Critical Rule**: Never write production code without a failing test first.

### Checklist

Copy this checklist and track your progress:

- [ ] A failing test exists for this behavior
- [ ] The test has been run and actually fails
- [ ] The failure message is clear and measurable
- [ ] The test is committed with `RED: ...` message
- [ ] Status is marked as `RED`
- [ ] Minimum code written to pass (GREEN)
- [ ] All tests pass after implementation
- [ ] Refactoring preserves all test behavior
- [ ] Each phase has its own commit

## Output

| Output Type | Description |
|-------------|-------------|
| TDD Status Report | Phase status (`pending`/`RED`/`GREEN`/`refactor`) per feature |
| Git Commits | Pattern: `RED: test for [feature]`, `GREEN: implement [feature]`, `REFACTOR: improve [aspect]` |
| Test Results | Pass/fail status after each phase transition |
| Enforcement Decisions | Allow/deny based on TDD compliance |
| Violation Reports | TDD violations with recovery procedures |

> **Output discipline:** All scripts support `--output-file <path>`.

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See the detailed guide in Resources for common error scenarios.

## Examples

### RED-GREEN-REFACTOR Cycle

```bash
# Red phase: write failing test
python -m pytest tests/test_auth.py::test_login -x
# Output: FAILED (1 error) — test_login not implemented

# Green phase: implement minimum code, run tests
python -m pytest tests/test_auth.py::test_login -x
# Output: PASSED (1 passed)

# Refactor phase: improve code, verify tests still pass
python -m pytest tests/ -x
# Output: PASSED (12 passed)
```

See the detailed guide in Resources for extended examples.

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Coordinator Role
  - TDD Cycle Details
  - Core Principles Navigation
    - The Iron Law
  - Implementation Guidance Navigation
    - Step-by-Step Implementation
    - Common Patterns
  - Rules and Enforcement Navigation
    - Strict Rules
  - Problem Solving Navigation
    - Troubleshooting
  - Progressive Learning Path
  - RULE 14 Requirement Compliance
    - TDD and Requirement Compliance
    - Test-Requirement Traceability
    - When Tests Reveal Requirement Issues
    - TDD Phase Requirement Checks
  - Error Handling
    - Issue: Test passes on first run (RED phase failed)
    - Issue: Production code written without failing test
    - Issue: Refactoring breaks tests
  - Complete Reference Document Index
