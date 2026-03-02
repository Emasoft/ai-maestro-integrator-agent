# Issue Templates Part 3: Task Templates

This document covers the structure and format for creating effective task issues.

Back to index: [issue-templates.md](issue-templates.md)

---

## Table of Contents

- 2.3.1 Task description format (summary, details, definition of done)
- 2.3.2 Checklist syntax (basic, nested, with assignees)
- 2.3.3 Dependencies section (blocked by, blocks, table format)

---

## 2.3 Task Template

### 2.3.1 Task Description Format

Tasks are actionable work items that aren't bugs or features.

```markdown
## Task Description

### Summary

Brief one-line summary of the task.

### Details

Detailed description of what needs to be done. Include:
- Context and background
- Specific requirements
- Out of scope items

### Definition of Done

How do we know this task is complete?
```

**Example:**
```markdown
## Task Description

### Summary

Update all dependencies to latest stable versions

### Details

Our dependencies haven't been updated in 6 months. We need to:
- Update all npm packages to latest stable versions
- Run the test suite to verify nothing breaks
- Update lock files
- Document any breaking changes encountered

**Out of scope:**
- Major version upgrades that require code changes (create separate issues)
- Updating dev dependencies only used in CI

### Definition of Done

- [ ] All runtime dependencies updated
- [ ] All tests passing
- [ ] No security vulnerabilities in `npm audit`
- [ ] CHANGELOG.md updated with dependency changes
```

---

### 2.3.2 Checklist Syntax

GitHub supports task lists with special checkbox syntax.

**Basic syntax:**
```markdown
- [ ] Unchecked item
- [x] Checked item
```

**Nested checklists:**
```markdown
- [ ] Main task
  - [ ] Subtask 1
  - [ ] Subtask 2
  - [x] Subtask 3 (completed)
```

**With assignees (informal):**
```markdown
## Checklist

- [ ] Design review (@designer)
- [ ] Backend implementation (@backend-dev)
- [ ] Frontend implementation (@frontend-dev)
- [ ] QA testing (@qa-engineer)
- [ ] Documentation (@tech-writer)
```

**Progress tracking:**
GitHub automatically shows progress percentage in issue lists when checklists are present.

**Checklist with time estimates:**
```markdown
## Checklist

- [ ] Set up development environment (~30 min)
- [ ] Implement database schema (~2 hours)
- [ ] Write unit tests (~1 hour)
- [ ] Code review and fixes (~1 hour)
- [ ] Deploy to staging (~30 min)
```

**Checklist with priority markers:**
```markdown
## Checklist

- [ ] 🔴 Critical: Fix security vulnerability
- [ ] 🟡 High: Update API endpoints
- [ ] 🟢 Normal: Improve error messages
- [ ] ⚪ Low: Add code comments
```

---

### 2.3.3 Dependencies Section

Document what blocks this task and what this task blocks.

```markdown
## Dependencies

### Blocked By

Issues that must be completed before this task can start:

- #123 - API endpoint design
- #124 - Database schema migration

### Blocks

Issues waiting on this task to complete:

- #130 - Feature launch
- #131 - Documentation update
```

**Alternative format with status:**
```markdown
## Dependencies

| Issue | Title | Status | Relationship |
|-------|-------|--------|--------------|
| #123 | API design | In Progress | Blocks this |
| #124 | DB migration | Done | Blocks this |
| #130 | Feature launch | Waiting | Blocked by this |
```

**Dependency visualization:**
```markdown
## Dependencies

### Dependency Chain

```
#120 (Done) → #123 (In Progress) → THIS ISSUE → #130 (Waiting)
                ↓
              #124 (Done) ────────────────────↗
```

---

## Complete Task Example

```markdown
# Migrate user database to new schema

## Task Description

### Summary

Migrate the users table from legacy schema to the new normalized structure as defined in RFC-2024-03.

### Details

The current users table combines profile and authentication data. We need to:
- Split into `users` and `user_profiles` tables
- Migrate existing data preserving relationships
- Update all queries in the application
- Maintain backward compatibility during transition

**Context:**
- RFC-2024-03 approved on January 5th
- Estimated 50,000 user records to migrate
- Zero-downtime migration required

**Out of scope:**
- Changes to the authentication flow (separate issue #145)
- User-facing changes (no UI updates needed)

### Definition of Done

- [ ] New tables created in production
- [ ] Data migration completed with verification
- [ ] All application queries updated
- [ ] Performance benchmarks meet SLA
- [ ] Rollback procedure documented and tested

## Checklist

- [ ] Create migration script (@backend-dev)
- [ ] Test migration on staging with production data copy
- [ ] Update ORM models
- [ ] Update repository layer queries
- [ ] Update API endpoints
- [ ] Run full test suite
- [ ] Performance testing
- [ ] Deploy migration to production
- [ ] Verify data integrity
- [ ] Archive old table (after 30-day validation)

## Dependencies

### Blocked By

- #140 - Database connection pooling update (Done)
- #142 - Staging environment refresh (In Progress)

### Blocks

- #145 - New authentication flow
- #150 - User profile API v2
- #155 - Admin dashboard redesign

## Technical Notes

Migration will use blue-green deployment:
1. Create new tables alongside old
2. Dual-write to both during transition
3. Migrate historical data in batches
4. Switch reads to new tables
5. Stop writes to old tables
6. Archive old tables after validation period
```
