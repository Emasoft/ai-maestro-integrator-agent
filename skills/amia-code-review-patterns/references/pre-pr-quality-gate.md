# Pre-PR Quality Gate

## Overview

Before creating a PR, verify all 4 validation steps pass locally.

## The 4 Validation Steps

### Step 1: All Tests Pass Locally
- Run full test suite: `npm test` / `pytest` / equivalent
- No skipped tests unless documented
- Coverage threshold met (if configured)

### Step 2: No Linting Errors
- Run linter: `npm run lint` / `ruff check` / equivalent
- Zero errors (warnings acceptable if documented)
- Formatting applied: `npm run format` / `ruff format`

### Step 3: Documentation Updated
- README updated if public API changed
- Docstrings added for new functions
- Changelog entry drafted

### Step 4: Changelog Entry Added
- Entry describes change from user perspective
- Follows project's changelog format
- Links to issue number if applicable

## Checklist Template

```markdown
## Pre-PR Checklist
- [ ] All tests pass locally
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Changelog entry added
```

## Automation

Run this before every PR:
```bash
# Example for Python project
ruff check . && ruff format . && pytest && echo "Ready for PR"
```
