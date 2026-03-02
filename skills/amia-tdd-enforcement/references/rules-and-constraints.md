# TDD Rules and Constraints

## Use-Case TOC
- When you need absolute rules that cannot be broken → [The Iron Law](#the-iron-law-absolute)
- If you're in RED phase and unsure what's allowed → [Red Phase Rules](#red-phase-rules)
- If you're in GREEN phase and unsure what's allowed → [Green Phase Rules](#green-phase-rules)
- If you're in REFACTOR phase and unsure what's allowed → [Refactor Phase Rules](#refactor-phase-rules)
- When you need to know what actions are forbidden → [Forbidden Actions](#forbidden-actions)

## Table of Contents

- [The Iron Law (Absolute)](#the-iron-law-absolute)
  - [Rule 1: No Code Without a Failing Test](#rule-1-no-code-without-a-failing-test)
  - [Rule 2: Test Must Fail Before Implementation](#rule-2-test-must-fail-before-implementation)
  - [Rule 3: Only Modify Tests or Code, Never Both](#rule-3-only-modify-tests-or-code-never-both)
- [Red Phase Rules](#red-phase-rules)
  - [Allowed in RED Phase](#allowed-in-red-phase)
  - [Forbidden in RED Phase](#forbidden-in-red-phase)
  - [RED Phase Checklist](#red-phase-checklist)
- [Green Phase Rules](#green-phase-rules)
  - [Allowed in GREEN Phase](#allowed-in-green-phase)
  - [Forbidden in GREEN Phase](#forbidden-in-green-phase)
  - [GREEN Phase Checklist](#green-phase-checklist)
- [Refactor Phase Rules](#refactor-phase-rules)
  - [Allowed in REFACTOR Phase](#allowed-in-refactor-phase)
  - [Forbidden in REFACTOR Phase](#forbidden-in-refactor-phase)
  - [REFACTOR Phase Checklist](#refactor-phase-checklist)
- [Forbidden Actions](#forbidden-actions)
  - [Never Allowed (Any Phase)](#never-allowed-any-phase)
- [Violation Recovery Procedure](#violation-recovery-procedure)
  - [When You Realize You Violated TDD](#when-you-realize-you-violated-tdd)
- [Enforcement Scripts](#enforcement-scripts)
  - [Pre-Commit Hook](#pre-commit-hook)
  - [Test-First Verification](#test-first-verification)

---

## The Iron Law (Absolute)

These rules are **non-negotiable** and apply at all times:

### Rule 1: No Code Without a Failing Test

**Requirement:**
- Every line of production code must be justified by a failing test
- The test must exist **before** the code
- The test must actually fail when run

**Violation Examples:**
- Writing code without a test
- Writing code before the test
- Writing code when test already passes
- "I'll write the test later"

**Penalty for Violation:**
```bash
# Delete or revert the untested code
git revert <commit-sha>
# Or
git reset --hard HEAD~1

# Write the test first
# Then re-implement the code
```

### Rule 2: Test Must Fail Before Implementation

**Requirement:**
- Run the test before writing any production code
- Confirm the test fails
- The failure must be visible and measurable

**Violation Examples:**
- Not running the test before implementing
- Test passes on first run (suspicious - either code already exists or test is broken)
- Test is commented out or skipped

**Verification:**
```bash
# Run test before implementing
pytest tests/test_feature.py::test_new_feature
# Expected: FAIL

# After implementing
pytest tests/test_feature.py::test_new_feature
# Expected: PASS
```

### Rule 3: Only Modify Tests or Code, Never Both

**In RED phase:**
- ONLY write tests
- NO production code

**In GREEN phase:**
- ONLY write production code
- NO test modifications (except to fix typos/syntax errors)

**In REFACTOR phase:**
- ONLY modify production code structure
- NO test modifications (except to improve clarity without changing assertions)
- NO new functionality

**Violation Example:**
```python
# WRONG: Modifying test to make it pass
def test_user_can_login():
    result = service.login("alice@example.com", "password")
    # Changed assertion to make it pass - THIS IS WRONG
    assert result.authenticated == False  # Should be True
```

---

## Red Phase Rules

### Allowed in RED Phase

**✓ Write new tests**
- Create test file if needed
- Write test method/function
- Use Arrange-Act-Assert pattern
- Add test assertions

**✓ Run tests**
- Execute test to verify failure
- Check failure message
- Confirm test is actually failing

**✓ Commit test**
- Add test file to git
- Commit with "RED: ..." message
- Mark status as RED

### Forbidden in RED Phase

**✗ Write production code**
- No implementation
- No classes/methods/functions
- Not even empty methods

**✗ Modify existing production code**
- No changes to make test pass
- No refactoring
- No "quick fixes"

**✗ Skip running the test**
- Must verify test fails
- Must see failure message
- Cannot assume it fails

**✗ Write multiple tests at once**
- One test per RED phase
- One behavior per test
- Complete cycle before next test

### RED Phase Checklist

Before moving to GREEN:
- [ ] Test is written
- [ ] Test uses AAA pattern
- [ ] Test has been run
- [ ] Test fails (not pass, not skip)
- [ ] Failure message is clear
- [ ] Test is committed
- [ ] Status marked as RED

---

## Green Phase Rules

### Allowed in GREEN Phase

**✓ Write minimum production code**
- Create classes/methods/functions
- Add logic to make test pass
- Use simplest solution
- Hardcode if needed

**✓ Run tests repeatedly**
- Run after each change
- Verify new test passes
- Verify old tests still pass

**✓ Fix code if tests fail**
- Debug implementation
- Adjust logic
- Add missing code

**✓ Commit when test passes**
- Add production files to git
- Commit with "GREEN: ..." message
- Mark status as GREEN

### Forbidden in GREEN Phase

**✗ Refactor code**
- No code cleanup
- No design improvements
- No extracting methods
- Wait for REFACTOR phase

**✗ Add extra features**
- Only implement what test requires
- No "while I'm here" additions
- No future-proofing
- No edge cases not in test

**✗ Modify test to make it pass**
- Test assertions are sacred
- If test is wrong, revert and fix test first
- Cannot change expectations

**✗ Write new tests**
- One cycle at a time
- Complete current cycle first
- New tests wait for next RED phase

### GREEN Phase Checklist

Before moving to REFACTOR:
- [ ] Production code is written
- [ ] New test passes
- [ ] All old tests still pass
- [ ] No regressions introduced
- [ ] Code is committed
- [ ] Status marked as GREEN

---

## Refactor Phase Rules

### Allowed in REFACTOR Phase

**✓ Improve code structure**
- Extract methods
- Rename variables
- Simplify logic
- Remove duplication

**✓ Improve design**
- Apply patterns
- Reduce coupling
- Increase cohesion
- Improve encapsulation

**✓ Run tests after each change**
- Verify behavior unchanged
- Check all tests pass
- Confirm no regressions

**✓ Commit each refactoring**
- Small commits
- One refactoring per commit
- Clear commit messages

**✓ Revert if test fails**
- Immediately undo change
- Try different approach
- Keep tests passing

### Forbidden in REFACTOR Phase

**✗ Add new functionality**
- No new features
- No new behavior
- No new capabilities
- Only improve existing code

**✗ Change test assertions**
- Cannot modify what test expects
- Can only improve test clarity
- Cannot change behavior being tested

**✗ Skip running tests**
- Must run after each change
- Cannot assume tests pass
- Must verify behavior preserved

**✗ Make large changes**
- Small incremental refactorings
- One thing at a time
- Keep tests passing throughout

### REFACTOR Phase Checklist

Before moving to next RED:
- [ ] Code quality improved
- [ ] All tests still pass
- [ ] Behavior unchanged
- [ ] Refactorings committed
- [ ] Status marked as REFACTOR
- [ ] Ready for next feature

---

## Forbidden Actions

### Never Allowed (Any Phase)

**✗ Skip writing tests**
- Every feature needs tests
- Every bug fix needs tests
- Every change needs tests

**✗ Write tests after code**
- Test MUST come first
- Code MUST come second
- No exceptions

**✗ Modify tests to pass**
- Tests define requirements
- If test is wrong, start over
- Cannot adjust expectations to match code

**✗ Comment out failing tests**
- If test fails, fix code
- If test is wrong, fix test
- Never hide failures

**✗ Add untested code**
- No speculative code
- No "just in case" code
- No future features

**✗ Make multiple changes before running tests**
- Run tests after EACH change
- Immediate feedback
- Easier debugging

**✗ Work on multiple features simultaneously**
- One RED-GREEN-REFACTOR cycle at a time
- Complete current cycle
- Then start next cycle

---

## Violation Recovery Procedure

### When You Realize You Violated TDD

**1. Stop immediately**
- Cease current work
- Acknowledge the violation
- Do not try to fix it forward

**2. Identify what was violated**
- Code without test?
- Test without failing?
- Wrong phase?

**3. Revert to last valid state**
```bash
# Undo uncommitted changes
git checkout .

# Or revert last commit
git revert HEAD

# Or reset to before violation
git reset --hard <last-good-commit>
```

**4. Start over correctly**
- Begin with RED phase
- Write failing test
- Follow cycle properly

**5. Document the mistake**
```markdown
## Lessons Learned
- Date: 2025-01-01
- Violation: Wrote UserService.login() before writing test
- Recovery: Reverted commit abc1234, wrote test first, re-implemented
- Prevention: Always run test BEFORE implementing
```

---

## Enforcement Scripts

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Enforces TDD commit message format

COMMIT_MSG=$(git log -1 --pretty=%B)

if [[ ! $COMMIT_MSG =~ ^(RED|GREEN|REFACTOR): ]]; then
    echo "ERROR: Commit message must start with RED:, GREEN:, or REFACTOR:"
    echo "Current: $COMMIT_MSG"
    exit 1
fi

echo "✓ TDD commit format verified"
```

### Test-First Verification

```bash
#!/bin/bash
# scripts/verify-test-first.sh
# Checks if test was committed before implementation

TEST_COMMIT=$(git log --all --oneline --grep="RED:" -1 --format=%H)
IMPL_COMMIT=$(git log --all --oneline --grep="GREEN:" -1 --format=%H)

if [ -z "$TEST_COMMIT" ]; then
    echo "✗ No RED commit found"
    exit 1
fi

if [ -z "$IMPL_COMMIT" ]; then
    echo "✓ Only test exists (waiting for implementation)"
    exit 0
fi

TEST_DATE=$(git show -s --format=%ct $TEST_COMMIT)
IMPL_DATE=$(git show -s --format=%ct $IMPL_COMMIT)

if [ $TEST_DATE -lt $IMPL_DATE ]; then
    echo "✓ Test committed before implementation"
    exit 0
else
    echo "✗ Implementation committed before test!"
    echo "Test: $TEST_COMMIT at $(date -d @$TEST_DATE)"
    echo "Impl: $IMPL_COMMIT at $(date -d @$IMPL_DATE)"
    exit 1
fi
```
