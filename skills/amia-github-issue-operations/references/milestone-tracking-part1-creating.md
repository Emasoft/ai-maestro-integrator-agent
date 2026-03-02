# Milestone Tracking - Part 1: Creating Milestones

## Table of Contents

- [3.1 Creating Milestones](#31-creating-milestones)
  - [3.1.1 Milestone Title Conventions](#311-milestone-title-conventions)
  - [3.1.2 Setting Due Dates](#312-setting-due-dates)
  - [3.1.3 Milestone Descriptions](#313-milestone-descriptions)

---

## 3.1 Creating Milestones

### 3.1.1 Milestone Title Conventions

Milestone titles should be clear, consistent, and sortable.

**Recommended naming patterns:**

| Pattern | Example | Use Case |
|---------|---------|----------|
| Semantic Version | `v2.1.0` | Software releases |
| Date-based | `2024-Q1` | Quarterly planning |
| Sprint-based | `Sprint 23` | Agile teams |
| Feature-based | `User Authentication` | Feature-driven development |

**Creating a milestone via gh CLI:**
```bash
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  -f title="v2.1.0" \
  -f state="open"
```

**Naming best practices:**
1. Use consistent format across all milestones
2. Make titles sortable (use leading zeros: `Sprint 01` not `Sprint 1`)
3. Include version numbers for release milestones
4. Avoid special characters that complicate CLI usage

### 3.1.2 Setting Due Dates

Due dates help track milestone progress and identify delays.

**Creating milestone with due date:**
```bash
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  -f title="v2.1.0" \
  -f due_on="2024-03-15T23:59:59Z"
```

**Date format:** ISO 8601 format with timezone (`YYYY-MM-DDTHH:MM:SSZ`)

**Python helper for due date:**
```python
from datetime import datetime, timedelta

def get_milestone_due_date(weeks_from_now: int = 2) -> str:
    """Calculate due date in ISO format."""
    due_date = datetime.utcnow() + timedelta(weeks=weeks_from_now)
    # Set to end of day
    due_date = due_date.replace(hour=23, minute=59, second=59)
    return due_date.strftime("%Y-%m-%dT%H:%M:%SZ")

# Example: 2 weeks from now
due_on = get_milestone_due_date(2)
# Returns: "2024-01-29T23:59:59Z"
```

**Updating due date:**
```bash
# First, get milestone number
milestone_number=$(gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | select(.title=="v2.1.0") | .number')

# Update due date
gh api repos/{owner}/{repo}/milestones/${milestone_number} \
  --method PATCH \
  -f due_on="2024-04-01T23:59:59Z"
```

### 3.1.3 Milestone Descriptions

Descriptions provide context about milestone goals and scope.

**Creating with description:**
```bash
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  -f title="v2.1.0" \
  -f description="## Goals

- Implement user authentication
- Add dashboard analytics
- Performance improvements

## Out of Scope

- Mobile app changes
- Breaking API changes"
```

**Description template:**
```markdown
## Goals

Brief list of what this milestone will accomplish.

- Goal 1
- Goal 2
- Goal 3

## Success Criteria

How we know the milestone is complete.

## Out of Scope

What is explicitly NOT included in this milestone.

## Dependencies

External factors or other milestones this depends on.
```

---

[Back to Milestone Tracking Index](milestone-tracking.md)
