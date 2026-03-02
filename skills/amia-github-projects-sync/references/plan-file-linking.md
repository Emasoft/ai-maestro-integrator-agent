# Plan File Linking

## Table of Contents

1. [When understanding plan files](#overview)
2. [When naming plan files](#naming-convention)
3. [When creating plan file content](#plan-file-structure)
4. [When linking plans to GitHub issues](#linking-procedures)
5. [When plan files integrate with workflow](#integration-with-workflow)
6. [When creating epic-level plans](#epic-plans)
7. [When following plan file best practices](#best-practices)
8. [When referencing related planning documentation](#related-files)

## Overview

Plan files are detailed implementation plans stored in the repository that link to GitHub issues. They provide the full context and strategy that doesn't fit in issue descriptions.

### Purpose of Plan Files

1. **Detailed strategy**: Full implementation approach with rationale
2. **Persistent memory**: Survives context resets, available to any agent
3. **Review reference**: Reviewers can check implementation against plan
4. **Knowledge preservation**: Captures decisions and trade-offs

### When Plans Are Required

| Issue Type | Plan Required? | Reason |
|------------|---------------|--------|
| `type:epic` | **ALWAYS** | Complex multi-issue coordination |
| `type:feature` (L/XL effort) | **ALWAYS** | Significant implementation |
| `type:feature` (S/M effort) | RECOMMENDED | Depends on complexity |
| `type:refactor` | RECOMMENDED | Documents before/after state |
| `type:bug` | OPTIONAL | Only if fix is complex |
| `type:docs` | OPTIONAL | Rarely needed |
| `type:test` | OPTIONAL | Rarely needed |
| `type:chore` | NEVER | Too simple |

## Naming Convention

### Format

```
plans/GH-{issue-number}-{short-slug}.md
```

### Examples

| Issue | Slug | Plan File |
|-------|------|-----------|
| #42 - Implement User Authentication | user-auth | `plans/GH-42-user-auth.md` |
| #57 - Refactor Database Layer | db-refactor | `plans/GH-57-db-refactor.md` |
| #103 - Epic: Payment System | payment-epic | `plans/GH-103-payment-epic.md` |

### Directory Structure

```
project-root/
├── plans/
│   ├── README.md                    # Plan directory overview
│   ├── GH-42-user-auth.md           # Active plan
│   ├── GH-57-db-refactor.md         # Active plan
│   ├── GH-103-payment-epic.md       # Epic plan (links sub-issues)
│   └── archive/
│       ├── GH-15-initial-setup.md   # Completed plan
│       └── GH-23-api-design.md      # Completed plan
├── src/
├── tests/
└── ...
```

## Plan File Structure

### Required Sections

```markdown
# Plan: GH-{number} - {Issue Title}

## Metadata

- **Issue**: [GH-{number}](https://github.com/owner/repo/issues/{number})
- **Created**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD
- **Status**: draft | active | completed | superseded
- **Author**: {agent-id or human name}

## Problem Statement

[What problem this issue solves - 2-3 sentences]

## Proposed Solution

[High-level approach - 1-2 paragraphs]

## Implementation Steps

### Step 1: [Name]

[Details, including files to modify, approach]

**Verification**: [How to verify this step is complete]

### Step 2: [Name]

[Continue for all steps...]

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [What was decided] | [What was chosen] | [Why] |

## Dependencies

- **Blocked by**: [List of blocking issues]
- **Blocks**: [List of issues this blocks]

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | Low/Medium/High | Low/Medium/High | [How to address] |

## Testing Strategy

[What tests will be written, coverage targets]

## Completion Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
- [ ] Tests pass with >80% coverage
- [ ] PR approved and merged
- [ ] Documentation updated

## Notes

[Any additional context, links to research, alternatives considered]
```

### Minimal Template (for smaller issues)

```markdown
# Plan: GH-{number} - {Issue Title}

**Issue**: GH-{number} (link to the GitHub issue) | **Status**: active | **Updated**: YYYY-MM-DD

## Approach

[Brief description of implementation approach]

## Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Completion Criteria

- [ ] [Main deliverable]
- [ ] Tests pass
- [ ] PR merged
```

## Linking Procedures

### Linking Plans to Issues

This section covers how to establish bidirectional links between plan files and GitHub issues.

### Adding Plan Reference to GitHub Issue

When creating plan file, add this to the issue body (edit first comment):

```markdown
## Implementation Plan

📋 **Plan File**: `plans/GH-42-user-auth.md`

[Rest of issue content...]
```

**OR** add a comment:

```markdown
📋 Implementation plan created: `plans/GH-42-user-auth.md`
```

### Updating Plan During Implementation

1. When making significant changes to approach:
   - Update plan file
   - Add comment to issue: "Plan updated: [brief description of change]"

2. When completing steps:
   - Check off completion criteria in plan
   - Update "Last Updated" date

3. When encountering blockers:
   - Document in plan under "Notes"
   - Update Dependencies section

### Archiving Completed Plans

When issue is closed and merged:

1. Update plan status to `completed`
2. Move to archive:
   ```bash
   git mv plans/GH-42-user-auth.md plans/archive/GH-42-user-auth.md
   git commit -m "Archive completed plan GH-42"
   ```
3. Update issue comment: "Plan archived: [link to archived plan]"

## Integration with Workflow

### Creating Plans (During Sprint Planning)

When issue moves from **Backlog** to **Todo**:

1. Assess if plan is required (see table above)
2. If required:
   - Create plan file using template
   - Add link to GitHub issue
   - Update issue labels if needed

### Updating Plans (During In Progress)

When issue is **In Progress**:

1. Agent references plan before starting work
2. Agent updates plan if approach changes
3. Agent checks off completed steps
4. Agent documents any discoveries or blockers

### Referencing Plans (During Review)

When issue is in **AI Review**:

1. Reviewer reads plan to understand intended approach
2. Reviewer verifies implementation matches plan
3. If implementation differs significantly:
   - Request plan update, OR
   - Discuss deviation with author

### Plan Verification (Before Done)

Before moving to **Done**:

- [ ] All completion criteria checked off
- [ ] Plan status updated to `completed`
- [ ] Plan moved to archive
- [ ] Issue comment updated with archive link

## Epic Plans

Epic plans are special because they coordinate multiple sub-issues.

### Epic Plan Structure

```markdown
# Epic Plan: GH-103 - Payment System

## Sub-Issues

| Issue | Title | Status | Plan |
|-------|-------|--------|------|
| GH-104 | Payment Gateway Integration | In Progress | `[Plan]\(GH-104-payment-gateway.md\)` |
| GH-105 | Invoice Generation | Todo | `[Plan]\(GH-105-invoices.md\)` |
| GH-106 | Refund Processing | Blocked | `[Plan]\(GH-106-refunds.md\)` |

## Dependency Graph

```
GH-104 (Gateway) ─┬─→ GH-105 (Invoices)
                  └─→ GH-106 (Refunds)
```

## Overall Progress

- [x] Phase 1: Gateway Integration (GH-104)
- [ ] Phase 2: Invoice System (GH-105)
- [ ] Phase 3: Refund Handling (GH-106)

[Rest of epic plan...]
```

## Best Practices

### DO

- Create plans early (before starting work)
- Update plans as understanding evolves
- Link plans bidirectionally (issue ↔ plan)
- Archive completed plans (don't delete)
- Reference plans in PR descriptions

### DON'T

- Skip plans for complex features
- Let plans become stale
- Duplicate plan content in issue
- Delete plans (archive instead)
- Ignore plan during review

## Related Files

- `status-management.md` - Workflow triggers for plan creation
- `iteration-cycle-rules.md` - Plan verification before approval
- `issue-templates.md` - Templates that reference plans
- `../planning-patterns/SKILL.md` - Full planning methodology
