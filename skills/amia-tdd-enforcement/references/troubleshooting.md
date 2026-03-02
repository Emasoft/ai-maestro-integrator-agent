# TDD Troubleshooting - Index

This document provides quick navigation to common TDD issues and their solutions.

---

## Use-Case TOC

### Part 1: Test Failures
See [troubleshooting-part1-test-failures.md](troubleshooting-part1-test-failures.md)

- If tests fail during refactoring → Test Fails During Refactoring
  - Symptoms: Test passed before refactoring, now fails
  - Solution: Revert, make smaller changes, run tests after each micro-change
  - Prevention: Tiny changes, commit each successful refactoring

- When you can't write a failing test → Cannot Write a Failing Test
  - Symptoms: Requirement clear but test is too complex
  - Solution: Break requirement into smaller behaviors
  - Prevention: Start with smallest possible behavior

---

### Part 2: Code Issues
See [troubleshooting-part2-code-issues.md](troubleshooting-part2-code-issues.md)

- If code passes test but seems wrong → Code Passes But Seems Wrong
  - Symptoms: Test passes but code seems incorrect/incomplete
  - Solution: Write NEW test that catches the issue (don't modify implementation)
  - Prevention: Write tests for negative and edge cases

- When refactoring takes too long → Refactoring Takes Too Long
  - Symptoms: 30+ minutes refactoring, many changes, afraid to commit
  - Solution: Commit current state, move to next feature, make smaller changes
  - Prevention: Set 10-15 minute timer, small frequent refactorings

---

### Part 3: Passing Tests
See [troubleshooting-part3-passing-tests.md](troubleshooting-part3-passing-tests.md)

- If test passes but code seems incomplete → Test Passes But Code Incomplete
  - Symptoms: Test passes but feels like not doing enough
  - Solution: This is TDD working correctly - write another test for next aspect
  - Prevention: Embrace incremental development, one test = one behavior

- When test passes immediately → Test Passes on First Run
  - Symptoms: New test passes on first run without failure
  - Solution: Verify test actually tests something by temporarily breaking code
  - Prevention: Always run test before implementing, confirm it fails

---

### Part 4: Workflow Issues
See [troubleshooting-part4-workflow.md](troubleshooting-part4-workflow.md)

- If you're not sure what to test next → Unsure What to Test Next
  - Symptoms: Completed cycle, many possible options
  - Solution: List remaining behaviors, prioritize by importance
  - Prevention: Maintain backlog, prioritize before starting

- When tests become slow → Tests Are Too Slow
  - Symptoms: Test suite takes minutes, hesitant to run frequently
  - Solution: Use test doubles, separate unit/integration tests
  - Prevention: Keep unit tests fast (<100ms), use in-memory databases

---

## Quick Reference

| Problem | Part File | Key Solution |
|---------|-----------|--------------|
| Test fails during refactoring | part1 | Revert, smaller changes |
| Can't write failing test | part1 | Break down requirement |
| Code passes but seems wrong | part2 | Write new test |
| Refactoring too long | part2 | Timer, commit often |
| Test passes but incomplete | part3 | Write next test |
| Test passes first run | part3 | Verify test works |
| Unsure what to test | part4 | Prioritized backlog |
| Tests too slow | part4 | Test doubles |
