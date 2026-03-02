# Python Review Patterns Reference

## Overview

This reference covers Python-specific code review patterns, organized into detailed part files for efficient progressive disclosure.

---

## Table of Contents

### Part 1: Style, Types, and Documentation
**File**: [python-review-patterns-part1-style-types-docstrings.md](python-review-patterns-part1-style-types-docstrings.md)

- 2.1 Python code style and formatting checklist
  - 2.1.1 Essential style rules table (PEP 8)
  - 2.1.2 Formatting checklist (whitespace, blank lines, operators)
  - 2.1.3 Example: Proper Python formatting
- 2.2 Type hints verification and mypy compliance
  - 2.2.1 Type hint syntax for Python 3.10+
  - 2.2.2 mypy configuration in pyproject.toml
  - 2.2.3 Type hint review checklist
  - 2.2.4 Common mypy errors and fixes
- 2.3 Docstring standards (Google, NumPy, Sphinx)
  - 2.3.1 Google style docstrings (recommended)
  - 2.3.2 NumPy style docstrings
  - 2.3.3 Docstring review checklist

---

### Part 2: Imports, Tests, and Linting
**File**: [python-review-patterns-part2-imports-tests-linting.md](python-review-patterns-part2-imports-tests-linting.md)

- 2.4 Import organization and dependency management
  - 2.4.1 Import grouping order (stdlib, third-party, local)
  - 2.4.2 Import style rules table
  - 2.4.3 Circular import prevention strategies
  - 2.4.4 Dependency management with pyproject.toml
- 2.5 Test framework patterns with pytest
  - 2.5.1 pytest project structure
  - 2.5.2 Essential pytest patterns (fixtures, conftest)
  - 2.5.3 pytest configuration in pyproject.toml
  - 2.5.4 Test review checklist
- 2.6 Linting with ruff, mypy, and bandit
  - 2.6.1 ruff configuration
  - 2.6.2 Running linters (ruff, mypy, bandit commands)
  - 2.6.3 bandit configuration
  - 2.6.4 Common security issues bandit detects
  - 2.6.5 Linting review checklist

---

## Quick Reference: When to Read Each Part

| If reviewing... | Read |
|-----------------|------|
| Code formatting, naming, style | Part 1, Section 2.1 |
| Type annotations, mypy errors | Part 1, Section 2.2 |
| Docstrings, documentation | Part 1, Section 2.3 |
| Import statements, dependencies | Part 2, Section 2.4 |
| Test code, pytest fixtures | Part 2, Section 2.5 |
| Linter configuration, security | Part 2, Section 2.6 |

---

## Summary Checklists

### Style Quick Check
- [ ] PEP 8 naming conventions followed
- [ ] Consistent 4-space indentation
- [ ] Line length under 88 characters
- [ ] Proper import organization

### Type Hints Quick Check
- [ ] All public functions have type annotations
- [ ] Using `X | None` not `Optional[X]` (Python 3.10+)
- [ ] mypy passes without errors

### Documentation Quick Check
- [ ] All public APIs have docstrings
- [ ] Consistent docstring style (Google/NumPy)
- [ ] Args, Returns, Raises documented

### Testing Quick Check
- [ ] Descriptive test names
- [ ] Proper use of fixtures
- [ ] Edge cases covered with parametrize

### Linting Quick Check
- [ ] ruff check passes
- [ ] mypy strict mode passes
- [ ] No high-severity bandit findings
