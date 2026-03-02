# Issue Templates Reference

This document provides templates for creating different types of GitHub issues: bug reports, feature requests, and tasks. It also covers programmatic template population.

---

## Table of Contents

### Part 1: Bug Report Templates
See [issue-templates-part1-bug-reports.md](issue-templates-part1-bug-reports.md)

- 2.1 Bug report template
  - 2.1.1 Required sections (description, steps, expected/actual behavior)
  - 2.1.2 Environment information (web, CLI, mobile formats)
  - 2.1.3 Reproduction steps format (numbered steps, prerequisites)

### Part 2: Feature Request Templates
See [issue-templates-part2-feature-requests.md](issue-templates-part2-feature-requests.md)

- 2.2 Feature request template
  - 2.2.1 Problem statement (pain point description, current workaround)
  - 2.2.2 Proposed solution (ideal solution, alternatives considered)
  - 2.2.3 Acceptance criteria (checkbox format, measurable requirements)

### Part 3: Task Templates
See [issue-templates-part3-tasks.md](issue-templates-part3-tasks.md)

- 2.3 Task template
  - 2.3.1 Task description format (summary, details, definition of done)
  - 2.3.2 Checklist syntax (basic, nested, with assignees)
  - 2.3.3 Dependencies section (blocked by, blocks, table format)

### Part 4: Programmatic Template Population
See [issue-templates-part4-programmatic.md](issue-templates-part4-programmatic.md)

- 2.4 Populating templates programmatically
  - 2.4.1 Variable substitution (placeholder syntax, Python substitution)
  - 2.4.2 Dynamic content injection (system info, git info)
  - 2.4.3 Template selection logic (type detection, combining selection with population)

---

## Quick Reference

### When to Use Each Template

| Situation | Template | Key Sections |
|-----------|----------|--------------|
| Something is broken | Bug Report | Steps to reproduce, Expected vs Actual |
| New capability needed | Feature Request | Problem statement, Acceptance criteria |
| Work item to complete | Task | Checklist, Dependencies |

### Minimal Required Sections by Type

**Bug Report:**
1. Description - What is broken
2. Steps to Reproduce - How to trigger it
3. Expected vs Actual - What should happen vs what does

**Feature Request:**
1. Problem Statement - Why this is needed
2. Proposed Solution - What to build
3. Acceptance Criteria - When it's done

**Task:**
1. Summary - What to do
2. Checklist - Step-by-step items
3. Definition of Done - Completion criteria

---

## Template Selection Guide

Choose the right template based on keywords in the issue:

| Keywords | Suggested Template |
|----------|-------------------|
| bug, crash, error, broken, fix | Bug Report |
| feature, add, implement, support, request | Feature Request |
| doc, readme, typo, comment | Documentation (variant of Task) |
| update, refactor, migrate, cleanup | Task |

---

## Related References

- [label-management.md](label-management.md) - Organizing issues with labels
- [milestone-tracking.md](milestone-tracking.md) - Grouping issues into milestones
