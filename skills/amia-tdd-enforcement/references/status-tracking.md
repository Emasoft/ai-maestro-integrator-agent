# Status Tracking System

## Table of Contents
- [Use-Case TOC](#use-case-toc)
- [Status States](#status-states)
  - [State Descriptions](#state-descriptions)
- [Status Tracking Format](#status-tracking-format)
- [Multi-Feature Tracking](#multi-feature-tracking)
- [Phase Transition Rules](#phase-transition-rules)
  - [Transition: pending to RED](#transition-pending--red)
  - [Transition: RED to GREEN](#transition-red--green)
  - [Transition: GREEN to REFACTOR](#transition-green--refactor)
  - [Transition: REFACTOR to pending (next feature)](#transition-refactor--pending-next-feature)
- [Status Tracking in Git](#status-tracking-in-git)
  - [Git Log View](#git-log-view)
  - [Verification Script](#verification-script)
- [Status Tracking Best Practices](#status-tracking-best-practices)

---

## Use-Case TOC
- When you need to track TDD cycle progress → [Status States](#status-states)
- If you need to document current phase → [Status Tracking Format](#status-tracking-format)
- When managing multiple features → [Multi-Feature Tracking](#multi-feature-tracking)
- If you need to verify phase transitions → [Phase Transition Rules](#phase-transition-rules)

---

## Status States

Each piece of work is tracked through four states:

| Status | Meaning | Action | Git Marker |
|--------|---------|--------|------------|
| `pending` | Test written but not yet implemented | Move to RED phase | No commit yet |
| `RED` | Test written and fails, needs implementation | Move to GREEN phase | Commit: "RED: ..." |
| `GREEN` | Test passes, implementation complete | Move to REFACTOR phase | Commit: "GREEN: ..." |
| `refactor` | Code improved, all tests pass | Return to pending for next feature | Commit: "REFACTOR: ..." |

### State Descriptions

**pending:**
- Test is being written
- Not yet committed
- Preparing for RED phase
- No production code exists for this test

**RED:**
- Test is committed
- Test fails when run
- Failure is measurable and clear
- Ready for implementation

**GREEN:**
- Production code implemented
- Test now passes
- All other tests still pass
- Code works but may be messy

**refactor:**
- Code quality improved
- All tests still pass
- Behavior unchanged
- Ready for next cycle

---

## Status Tracking Format

Use a checklist in your development to track status:

```markdown
## Feature: User Authentication

### Task 1: User can create account with valid email
- [x] RED: test_create_account_with_valid_email
  - Commit: abc1234
  - Test fails: UserService.create_account not defined

- [x] GREEN: test_create_account_with_valid_email
  - Commit: def5678
  - Implementation: UserService.create_account()
  - All tests: PASS

- [x] REFACTOR: test_create_account_with_valid_email
  - Commit: ghi9012
  - Changes: Extracted email validation to separate method
  - All tests: PASS

### Task 2: User cannot create account with invalid email
- [x] RED: test_reject_invalid_email
  - Commit: jkl3456
  - Test fails: No validation logic exists

- [ ] GREEN: test_reject_invalid_email
  - Status: In progress
  - Next: Implement email validation

- [ ] REFACTOR: test_reject_invalid_email
  - Status: Pending
```

---

## Multi-Feature Tracking

When managing multiple features simultaneously:

```markdown
## Sprint: User Management

### Feature 1: User Registration [COMPLETE]
- [x] RED: test_user_can_register
- [x] GREEN: test_user_can_register
- [x] REFACTOR: test_user_can_register

### Feature 2: User Login [IN PROGRESS]
- [x] RED: test_user_can_login
- [x] GREEN: test_user_can_login
- [ ] REFACTOR: test_user_can_login ← CURRENT

### Feature 3: Password Reset [PENDING]
- [ ] RED: test_user_can_request_password_reset
- [ ] GREEN: test_user_can_request_password_reset
- [ ] REFACTOR: test_user_can_request_password_reset

### Feature 4: Email Verification [PLANNED]
- [ ] RED: test_user_receives_verification_email
- [ ] GREEN: test_user_receives_verification_email
- [ ] REFACTOR: test_user_receives_verification_email
```

**Rules for Multi-Feature:**
- Only ONE feature in GREEN or REFACTOR at a time
- Can have multiple features in RED (tests written, awaiting implementation)
- Complete one full cycle before starting another
- Never work on GREEN/REFACTOR for multiple features simultaneously

---

## Phase Transition Rules

### Transition: pending → RED

**Requirements:**
- [ ] Test is written
- [ ] Test uses Arrange-Act-Assert pattern
- [ ] Test is committed to version control
- [ ] Test has been run and fails
- [ ] Failure message is clear

**Action:**
```bash
git add tests/test_feature.py
git commit -m "RED: test for [feature]"
# Mark status as RED
```

### Transition: RED → GREEN

**Requirements:**
- [ ] Currently in RED state
- [ ] Test fails when run
- [ ] Production code is written
- [ ] Test now passes
- [ ] All other tests still pass
- [ ] No refactoring done yet

**Action:**
```bash
git add src/feature.py
git commit -m "GREEN: implement [feature]"
# Mark status as GREEN
```

### Transition: GREEN → REFACTOR

**Requirements:**
- [ ] Currently in GREEN state
- [ ] All tests pass
- [ ] Code improvements identified
- [ ] Refactoring does not change behavior
- [ ] Tests still pass after refactoring

**Action:**
```bash
git add src/feature.py
git commit -m "REFACTOR: improve [aspect]"
# Mark status as REFACTOR
```

### Transition: REFACTOR → pending (next feature)

**Requirements:**
- [ ] Currently in REFACTOR state
- [ ] All tests pass
- [ ] Code quality is acceptable
- [ ] Feature is complete
- [ ] Ready for next feature

**Action:**
```markdown
# Update tracking
- Mark current feature as complete
- Create new pending item for next feature
- Return to RED phase for new feature
```

---

## Status Tracking in Git

### Git Log View

A properly followed TDD process produces this git history:

```
* ghi9012 REFACTOR: improve user login structure
* def5678 GREEN: implement user login
* abc1234 RED: test for user login
* previous commits...
```

### Verification Script

```bash
#!/bin/bash
# verify-tdd-sequence.sh
# Checks last 3 commits follow RED-GREEN-REFACTOR pattern

RED=$(git log -1 --skip=2 --pretty=format:%s | grep "^RED:")
GREEN=$(git log -1 --skip=1 --pretty=format:%s | grep "^GREEN:")
REFACTOR=$(git log -1 --pretty=format:%s | grep "^REFACTOR:")

if [ -n "$RED" ] && [ -n "$GREEN" ] && [ -n "$REFACTOR" ]; then
    echo "✓ TDD sequence verified"
    exit 0
else
    echo "✗ TDD sequence broken"
    echo "Last 3 commits should be RED → GREEN → REFACTOR"
    git log -3 --oneline
    exit 1
fi
```

---

## Status Tracking Best Practices

**Do:**
- Update status immediately after each phase
- Include commit SHAs in tracking
- Keep tracking document in version control
- Use consistent status labels
- Track test names explicitly

**Don't:**
- Skip status updates
- Use ambiguous status labels
- Track implementation details instead of status
- Mix multiple features in one status entry
- Forget to update when reverting
