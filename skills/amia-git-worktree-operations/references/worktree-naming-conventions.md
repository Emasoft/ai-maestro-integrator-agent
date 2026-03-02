# Worktree Naming Conventions

Comprehensive naming standard for all worktree types.

## Table of Contents

1. [When you need to understand naming rules → General Principles](#general-principles)
2. [If you need purpose-specific patterns → Naming Patterns by Purpose](#naming-patterns-by-purpose)
   - [When creating review worktrees → Review Worktrees](#review-worktrees)
   - [If you're building features → Feature Worktrees](#feature-worktrees)
   - [When fixing bugs → Bugfix Worktrees](#bugfix-worktrees)
   - [If you're running tests → Testing Worktrees](#testing-worktrees)
   - [When experimenting → Experimental Worktrees](#experimental-worktrees)
3. [If you need to understand ID vs path → Registry ID vs Path](#registry-id-vs-path)
4. [When converting branch names to paths → Branch Name Mapping](#branch-name-mapping)
5. [If you need to validate names → Validation Rules](#validation-rules)
6. [When you need practical examples → Examples by Scenario](#examples-by-scenario)
7. [If you want to avoid errors → Common Mistakes to Avoid](#common-mistakes-to-avoid)
8. [When you need command templates → Quick Reference](#quick-reference)

## General Principles

1. **Parent directory convention**: All worktrees use `../` prefix to place them alongside the main repository
2. **Descriptive but concise**: Names should be clear but not overly long
3. **Issue linking**: Include issue numbers where applicable (GH-{number}, JIRA-{key}, etc.)
4. **No spaces or special characters**: Use hyphens for word separation

## Naming Patterns by Purpose

### Review Worktrees

**Pattern**: `../review-{ISSUE_NUMBER}`

Used for code review and PR verification.

**Examples**:
```
../review-GH-42
../review-GH-123
../review-JIRA-ABC-456
```

**When to use**: Reviewing pull requests, verifying bug fixes, checking feature implementations

---

### Feature Worktrees

**Pattern**: `../feature-{FEATURE_NAME}`

Used for developing new features.

**Examples**:
```
../feature-user-auth
../feature-api-v2
../feature-payment-gateway
```

**When to use**: Building new functionality, adding capabilities, developing enhancements

---

### Bugfix Worktrees

**Pattern**: `../bugfix-{ISSUE_NUMBER}-{SHORT_DESC}`

Used for fixing bugs.

**Examples**:
```
../bugfix-GH-55-memory-leak
../bugfix-GH-88-crash-on-login
../bugfix-GH-101-null-pointer
```

**When to use**: Addressing reported bugs, fixing crashes, resolving defects

---

### Testing Worktrees

**Pattern**: `../test-{TEST_TYPE}-{TARGET}`

Used for running tests and experiments.

**Examples**:
```
../test-integration-api
../test-perf-database
../test-e2e-checkout
```

**Test types**: integration, unit, perf, e2e, regression, stress

**When to use**: Running test suites, performance benchmarking, QA verification

---

### Experimental Worktrees

**Pattern**: `../exp-{EXPERIMENT_NAME}`

Used for proof-of-concepts and experiments.

**Examples**:
```
../exp-new-parser
../exp-gpu-rendering
../exp-alternative-db
```

**When to use**: Trying new approaches, testing hypotheses, prototyping alternatives

---

## Registry ID vs Path

**Important distinction**:

- **Registry ID**: `review-GH-42` (no `../` prefix) - used in worktree registry JSON
- **Worktree Path**: `../review-GH-42` (with `../` prefix) - actual filesystem location

**Example**:
```json
{
  "id": "review-GH-42",
  "path": "../review-GH-42",
  "branch": "fix/memory-leak"
}
```

## Branch Name Mapping

Common patterns for deriving worktree names from branch names:

| Branch Name | Worktree Name | Notes |
|-------------|---------------|-------|
| `feature/user-auth` | `../feature-user-auth` | Replace `/` with `-` |
| `bugfix/GH-55-memory` | `../bugfix-GH-55-memory` | Keep issue number |
| `fix/crash` | `../bugfix-crash` | Add purpose prefix |
| `test/integration` | `../test-integration` | Keep test prefix |
| `exp/new-parser` | `../exp-new-parser` | Keep experiment prefix |

## Validation Rules

All worktree names must follow these rules:

1. **Max length**: 50 characters (excluding `../` prefix)
2. **Allowed characters**:
   - Alphanumeric: `a-z`, `A-Z`, `0-9`
   - Separators: `-` (hyphen), `_` (underscore)
3. **Must start with purpose prefix**: `review-`, `feature-`, `bugfix-`, `test-`, `exp-`, etc.
4. **No trailing hyphens**: Names must not end with `-` or `_`
5. **Lowercase preferred**: Use lowercase for consistency (except in issue numbers)

## Examples by Scenario

### Scenario 1: Reviewing a PR
```
Issue: GH-42
PR: #42 - Fix memory leak in parser
Worktree: ../review-GH-42
Branch: fix/memory-leak
```

### Scenario 2: Developing a new feature
```
Feature: User authentication system
Worktree: ../feature-user-auth
Branch: feature/user-auth
```

### Scenario 3: Fixing a critical bug
```
Issue: GH-88 - App crashes on login
Worktree: ../bugfix-GH-88-crash-on-login
Branch: bugfix/crash-on-login
```

### Scenario 4: Running integration tests
```
Test suite: API integration tests
Worktree: ../test-integration-api
Branch: main (or develop)
```

### Scenario 5: Experimenting with new approach
```
Experiment: New parsing algorithm
Worktree: ../exp-new-parser
Branch: exp/new-parser
```

## Common Mistakes to Avoid

❌ **Don't use spaces**: `../review GH-42` → Use `../review-GH-42`

❌ **Don't omit prefix**: `../GH-42` → Use `../review-GH-42`

❌ **Don't use deep paths**: `../reviews/2024/GH-42` → Use `../review-GH-42`

❌ **Don't use vague names**: `../testing` → Use `../test-integration-api`

❌ **Don't mix conventions**: `../review_GH.42` → Use `../review-GH-42`

## Quick Reference

```bash
# Review worktrees
git worktree add ../review-GH-{N} {branch}

# Feature worktrees
git worktree add ../feature-{name} {branch}

# Bugfix worktrees
git worktree add ../bugfix-GH-{N}-{desc} {branch}

# Testing worktrees
git worktree add ../test-{type}-{target} {branch}

# Experimental worktrees
git worktree add ../exp-{name} {branch}
```
