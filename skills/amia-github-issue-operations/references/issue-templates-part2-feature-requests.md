# Issue Templates Part 2: Feature Request Templates

This document covers the structure and format for creating effective feature requests.

Back to index: [issue-templates.md](issue-templates.md)

---

## Table of Contents

- 2.2.1 Problem statement (pain point description, current workaround)
- 2.2.2 Proposed solution (ideal solution, alternatives considered)
- 2.2.3 Acceptance criteria (checkbox format, measurable requirements)

---

## 2.2 Feature Request Template

### 2.2.1 Problem Statement

Start with the problem, not the solution.

```markdown
## Problem Statement

### What problem are you trying to solve?

Describe the pain point or limitation you're experiencing. Be specific about:
- Who is affected (role, user type)
- How often this occurs
- What is the impact (time lost, errors, frustration)

### Current Workaround

If you have a workaround, describe it here. This helps prioritize based on urgency.
```

**Good problem statement:**
```markdown
## Problem Statement

As a project manager, I need to export issue data to CSV format for stakeholder reporting. Currently, I have to manually copy data from each issue page into a spreadsheet, which takes approximately 2 hours per weekly report. This is error-prone and unsustainable as our issue count grows.

### Current Workaround

I use the GitHub API directly with a custom script, but this requires technical knowledge that other PMs on my team don't have.
```

---

### 2.2.2 Proposed Solution

Describe your ideal solution clearly.

```markdown
## Proposed Solution

### Describe your preferred solution

Explain what you would like to see implemented. Include:
- User interface mockups (if applicable)
- Workflow description
- Key features

### Alternatives Considered

List other solutions you've thought about and why they don't fully address the problem.
```

**Example:**
```markdown
## Proposed Solution

Add an "Export to CSV" button on the Issues list page that:
1. Exports all visible issues (respecting current filters)
2. Includes columns: Number, Title, State, Labels, Assignees, Created, Updated
3. Downloads immediately without requiring email

### Alternatives Considered

1. **Third-party integration**: Tools like Zapier could export data, but adds cost and complexity
2. **API documentation**: Improving API docs helps technical users but not all PMs
3. **Built-in reports**: Full reporting system is overkill for this use case
```

---

### 2.2.3 Acceptance Criteria

Define what "done" looks like.

```markdown
## Acceptance Criteria

A checklist of requirements that must be met for this feature to be considered complete:

- [ ] User can click "Export CSV" button on Issues list page
- [ ] Export respects current search filters and sorting
- [ ] CSV includes columns: Number, Title, State, Labels, Assignees, Milestone, Created, Updated
- [ ] Export works for up to 10,000 issues
- [ ] Download starts within 5 seconds for typical exports (< 1000 issues)
- [ ] Button is only visible to users with read access to the repository
- [ ] Export filename includes repository name and date
```

**Acceptance criteria best practices:**
- Use checkbox syntax `- [ ]` for easy tracking
- Be specific and measurable
- Include edge cases and limits
- Consider permissions and access control
- Include performance expectations

---

## Complete Feature Request Example

```markdown
# Add CSV export for Issues list

## Problem Statement

As a project manager, I need to export issue data to CSV format for stakeholder reporting. Currently, I have to manually copy data from each issue page into a spreadsheet, which takes approximately 2 hours per weekly report.

### Who is affected
- Project managers creating status reports
- Team leads tracking sprint progress
- Stakeholders reviewing project health

### Impact
- 2+ hours per week per PM spent on manual data entry
- Risk of data entry errors
- Outdated reports due to time constraints

### Current Workaround

Using GitHub API with a custom Python script, but this requires technical knowledge that other team members don't have.

## Proposed Solution

Add an "Export to CSV" button on the Issues list page that:
1. Exports all visible issues (respecting current filters)
2. Includes configurable columns
3. Downloads immediately to browser

### User Flow
1. User navigates to Issues list
2. User applies desired filters (labels, assignee, milestone)
3. User clicks "Export CSV" dropdown
4. User selects columns to include
5. Browser downloads CSV file

### Alternatives Considered

1. **Zapier integration** - Adds monthly cost, requires setup
2. **Improved API docs** - Doesn't help non-technical users
3. **Full reporting dashboard** - Overkill, longer development time

## Acceptance Criteria

- [ ] "Export CSV" button visible on Issues list page
- [ ] Export respects current filters and search
- [ ] Default columns: Number, Title, State, Labels, Assignees, Created, Updated
- [ ] Optional columns: Body, Milestone, Comments count
- [ ] Works for up to 10,000 issues
- [ ] Download starts within 5 seconds for < 1000 issues
- [ ] Button requires read access to repository
- [ ] Filename format: `{repo}-issues-{date}.csv`
- [ ] UTF-8 encoding with BOM for Excel compatibility

## Priority Justification

- Affects 15+ team members weekly
- Saves estimated 30+ hours/month team-wide
- Low development complexity
- High user satisfaction impact
```
