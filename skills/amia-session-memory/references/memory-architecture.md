# Memory Architecture

## Contents

- [Storage Locations](#storage-locations)
  - [PR Comments](#pr-comments)
  - [Issue Comments](#issue-comments)
  - [Handoff Documents](#handoff-documents)
- [Memory File Structure](#memory-file-structure)
- [Current State](#current-state)
- [Context](#context)
- [Next Steps](#next-steps)
- [Data Persistence Patterns](#data-persistence-patterns)
  - [Write-Through](#write-through)
  - [Read-On-Demand](#read-on-demand)
- [Retention Policy](#retention-policy)

## Storage Locations

AMIA session memory is stored in **three persistent locations**:

| Location | Scope | Use Case |
|----------|-------|----------|
| **GitHub PR Comments** | Single PR | Review state, feedback, patterns specific to that PR |
| **GitHub Issue Comments** | Single issue | Integration problem diagnosis, CI failures, blockers |
| **Handoff Documents** | Cross-session | Patterns learned, release history, incomplete work handoff |

### PR Comments

- Stored as markdown comments on the PR
- Include HTML state markers for machine parsing
- Updated after each review round
- Archived when PR merged

**Path**: Via `gh pr comment <PR_NUMBER>` or GitHub API

### Issue Comments

- Stored as markdown comments on issues
- Used for integration and CI/CD troubleshooting
- Link to related PRs and workflow runs

**Path**: Via `gh issue comment <ISSUE_NUMBER>` or GitHub API

### Handoff Documents

- Stored in `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`
- Persist across sessions
- Multiple files for different memory types

**Files**:

- `current.md` - Active work state
- `patterns-learned.md` - Accumulated review patterns
- `release-history.md` - Release log with decisions
- `ci-states.md` - CI/CD pipeline states

## Memory File Structure

All memory files follow this structure:

```markdown
# [Memory Type]

**Last Updated**: [ISO 8601 timestamp]
**Session**: [Session ID if applicable]

## Current State

[State description]

## Context

[Relevant context for future sessions]

## Next Steps

- [ ] Action 1
- [ ] Action 2
```

## Data Persistence Patterns

### Write-Through

Memory is **written immediately** after state changes:

- PR review completed → Write PR comment
- Pattern observed → Append to patterns-learned.md
- Release approved → Update release-history.md

### Read-On-Demand

Memory is **read only when needed**:

- User says "continue PR review" → Load PR comments
- User asks "what patterns have we seen" → Read patterns-learned.md
- User says "last release info" → Read release-history.md

**DO NOT** load all memory at session start. Only load what's relevant to current task.

## Retention Policy

| Memory Type | Retention |
|-------------|-----------|
| PR comments | Indefinite (GitHub history) |
| Issue comments | Indefinite (GitHub history) |
| Active handoffs | 30 days after PR merged |
| Release history | 1 year |
| Patterns learned | Indefinite |

Clean up old handoffs with:

```bash
find $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/ -name "*.md" -mtime +30 -delete
```
