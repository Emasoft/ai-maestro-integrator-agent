# Implementation Procedure

## Use-Case TOC
- When starting to implement a new feature → [Part 1: Writing Tests](implementation-procedure-part1-writing-tests.md)
- If you need to write a failing test → [Part 1: Writing Tests](implementation-procedure-part1-writing-tests.md)
- When you have a failing test and need to implement → [Part 2: Implementation and Refactoring](implementation-procedure-part2-implementation-refactor.md)
- If tests pass and code needs improvement → [Part 2: Implementation and Refactoring](implementation-procedure-part2-implementation-refactor.md)
- When you need a complete walkthrough → [Part 3: Complete Example](implementation-procedure-part3-complete-example.md)

---

## Part 1: Writing Tests

**File:** [implementation-procedure-part1-writing-tests.md](implementation-procedure-part1-writing-tests.md)

### Contents:
- Step 1: Understand the Requirement
  - Questions to answer before coding
  - Process for analyzing requirements
  - Example: User login feature decomposition
- Step 2: Write the Failing Test
  - Test Structure Pattern (Arrange-Act-Assert)
  - Test Naming Convention
  - Writing tests in Python, JavaScript, Java
  - Running the test to confirm failure
  - Committing the failing test (RED status)

---

## Part 2: Implementation and Refactoring

**File:** [implementation-procedure-part2-implementation-refactor.md](implementation-procedure-part2-implementation-refactor.md)

### Contents:
- Step 3: Make the Test Pass
  - Minimum Implementation Rules (Do's and Don'ts)
  - Implementation examples in Python, JavaScript, Java
  - Running all tests
  - Committing the implementation (GREEN status)
- Step 4: Refactor
  - Refactoring Targets (Code Quality, Design Quality)
  - Refactoring Process (small changes, test after each)
  - Refactored examples in Python, JavaScript
  - Committing each refactoring (REFACTOR status)

---

## Part 3: Complete Example

**File:** [implementation-procedure-part3-complete-example.md](implementation-procedure-part3-complete-example.md)

### Contents:
- Complete RED-GREEN-REFACTOR walkthrough
- Feature: User can login with valid credentials
- RED Phase: Write test, run test, commit
- GREEN Phase: Write minimum code, run tests, commit
- REFACTOR Phase: Improve code, run tests, commit
- Return to RED phase for next behavior
