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

## Reference Documents

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

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

See `references/detailed-guide.md` for usage examples.

## Resources

See `references/` directory for all reference documents.
