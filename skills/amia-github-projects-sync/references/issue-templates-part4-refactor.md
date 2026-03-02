# Issue Templates - Part 4: Refactor Template

## Table of Contents

- 4.1 [Refactoring request YAML template structure](#refactor-template)
- 4.2 [Current state vs proposed change format](#current-state-vs-proposed-change)
- 4.3 [Motivation section](#motivation)
- 4.4 [Files affected listing](#files-affected)
- 4.5 [Verification requirements](#verification)

---

## Refactor Template

### refactor.yml

This YAML file defines the structure for refactoring requests. Place it in `.github/ISSUE_TEMPLATE/refactor.yml`.

Refactoring improves code structure without changing external behavior. This template ensures changes are well-planned and verifiable.

```yaml
name: Refactoring
description: Code improvement without behavior change
labels: ["type:refactor", "status:backlog"]
body:
  - type: markdown
    attributes:
      value: |
        ## Refactoring Request
        Refactoring improves code without changing its behavior.

  - type: input
    id: title
    attributes:
      label: Refactoring Title
      placeholder: "Extract authentication logic into service class"
    validations:
      required: true

  - type: textarea
    id: current-state
    attributes:
      label: Current State
      description: What does the code look like now?
      placeholder: |
        Authentication logic is scattered across multiple controllers:
        - src/controllers/login.js (50 lines)
        - src/controllers/register.js (40 lines)
        - src/controllers/reset-password.js (60 lines)
    validations:
      required: true

  - type: textarea
    id: proposed-change
    attributes:
      label: Proposed Change
      description: What should the code look like after?
      placeholder: |
        Extract all auth logic into AuthService:
        - src/services/AuthService.js (new)
        - Controllers become thin wrappers
        - Shared validation in one place
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      description: Why is this refactoring needed?
      placeholder: |
        - Reduce code duplication
        - Make testing easier
        - Single point of change for auth logic
        - Prepare for adding OAuth support
    validations:
      required: true

  - type: textarea
    id: files-affected
    attributes:
      label: Files Affected
      description: Which files will change?
      placeholder: |
        - src/services/AuthService.js (new)
        - src/controllers/login.js (modify)
        - src/controllers/register.js (modify)
        - tests/services/AuthService.test.js (new)
    validations:
      required: true

  - type: textarea
    id: verification
    attributes:
      label: Verification
      description: How to verify behavior is unchanged?
      placeholder: |
        - All existing auth tests pass
        - Manual testing of login/register/reset flows
        - No changes to API contracts
    validations:
      required: true
```

---

## Section Details

### Current State vs Proposed Change

**Current State** describes the problem:
```markdown
Authentication logic is scattered across multiple controllers:
- src/controllers/login.js (50 lines of auth logic)
- src/controllers/register.js (40 lines duplicated)
- src/controllers/reset-password.js (60 lines similar)

Issues:
- Code duplication across files
- Inconsistent validation rules
- Difficult to unit test
- Changes require updates in multiple places
```

**Proposed Change** describes the solution:
```markdown
Extract all auth logic into AuthService:
- src/services/AuthService.js (new, ~100 lines)
- Controllers become thin wrappers (~15 lines each)
- Shared validation in one place
- Clear separation of concerns

Benefits:
- Single source of truth for auth logic
- Easy to unit test in isolation
- Prepare for adding OAuth support
```

### Motivation

Explain WHY the refactoring is needed:

```markdown
Technical debt:
- Reduce code duplication (currently 3x)
- Make testing easier (currently 20% coverage)

Future-proofing:
- Single point of change for auth logic
- Prepare for adding OAuth support

Maintenance:
- Easier onboarding for new developers
- Reduced bug surface area
```

### Files Affected

List all files with the type of change:
```markdown
New files:
- src/services/AuthService.js
- tests/services/AuthService.test.js

Modified files:
- src/controllers/login.js
- src/controllers/register.js
- src/controllers/reset-password.js

Deleted files:
- src/utils/auth-helpers.js (merged into AuthService)
```

**Include line count estimates** when available to help scope the work.

### Verification

Ensure behavior remains unchanged:

```markdown
Automated verification:
- All existing auth tests pass
- No new TypeScript/ESLint errors
- Coverage remains >=80%

Manual verification:
- Login flow works as before
- Registration flow works as before
- Password reset flow works as before

API contract verification:
- No changes to request/response formats
- No changes to HTTP status codes
- No changes to error messages
```

**Important**: Refactoring should NEVER require changes to tests that verify external behavior. If tests need updating, the scope may include behavior changes.
