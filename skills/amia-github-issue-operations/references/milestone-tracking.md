# Milestone Tracking Reference

This document provides comprehensive guidance for working with GitHub milestones, including creation, assignment, progress tracking, and closure operations.

---

## Table of Contents

### Part 1: Creating Milestones
**File:** [milestone-tracking-part1-creating.md](milestone-tracking-part1-creating.md)

- 3.1 Creating milestones
  - 3.1.1 Milestone title conventions
    - Recommended naming patterns (semantic version, date-based, sprint-based, feature-based)
    - Creating a milestone via gh CLI
    - Naming best practices for sortable, consistent titles
  - 3.1.2 Setting due dates
    - Creating milestone with due date using ISO 8601 format
    - Python helper for calculating due dates
    - Updating due dates on existing milestones
  - 3.1.3 Milestone descriptions
    - Creating milestones with markdown descriptions
    - Description template (Goals, Success Criteria, Out of Scope, Dependencies)

---

### Part 2: Assigning Issues to Milestones
**File:** [milestone-tracking-part2-assigning.md](milestone-tracking-part2-assigning.md)

- 3.2 Assigning issues to milestones
  - 3.2.1 Single issue assignment
    - Using gh CLI for single issue assignment
    - Using GitHub API with milestone number lookup
    - Python implementation for assignment by title
  - 3.2.2 Bulk assignment
    - Assigning multiple issues in a loop
    - Assigning all issues with a specific label
    - Python bulk assignment with success/failure tracking
  - 3.2.3 Moving between milestones
    - Moving issue from one milestone to another
    - Removing from milestone (unassign to null)
    - Bulk move all open issues between milestones

---

### Part 3: Progress Tracking and Closing Milestones
**File:** [milestone-tracking-part3-progress-closing.md](milestone-tracking-part3-progress-closing.md)

- 3.3 Milestone progress tracking
  - 3.3.1 Querying completion percentage
    - Get milestone with progress using jq calculation
    - Python progress calculation with percentage
  - 3.3.2 Open vs closed issues count
    - List all milestones with counts
    - Detailed breakdown by milestone
  - 3.3.3 Overdue detection
    - Check if milestone is overdue using date comparison
    - Python overdue check with days calculation

- 3.4 Closing milestones
  - 3.4.1 When to close
    - Conditions for closing (all work complete, release shipped, sprint ended)
    - Close milestone via CLI
    - Close only if all issues are done (conditional)
  - 3.4.2 Handling incomplete issues
    - Option 1: Move to next milestone
    - Option 2: Remove from milestone (backlog)
    - Option 3: Add "deferred" label and close anyway
  - 3.4.3 Archive vs delete
    - Closing (archiving) - preserves history
    - Deleting - removes completely
    - Reopen a closed milestone
    - Python helper for safe milestone closure with options

---

## Quick Reference

| Operation | Command |
|-----------|---------|
| Create milestone | `gh api repos/{owner}/{repo}/milestones --method POST -f title="v2.1.0"` |
| Assign issue | `gh issue edit 123 --repo owner/repo --milestone "v2.1.0"` |
| Check progress | `gh api repos/{owner}/{repo}/milestones --jq '.[] \| select(.title=="v2.1.0")'` |
| Close milestone | `gh api repos/{owner}/{repo}/milestones/{number} --method PATCH -f state="closed"` |
| Delete milestone | `gh api repos/{owner}/{repo}/milestones/{number} --method DELETE` |

---

## Related References

- [Label Management Reference](label-management.md) - Organizing issues with labels
