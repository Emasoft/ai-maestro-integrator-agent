# Operation: Create Module Issue


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [The 1:1 Principle](#the-11-principle)
- [Preconditions](#preconditions)
- [Input](#input)
- [Module Issue Template](#module-issue-template)
- [Module: <module-name>](#module-module-name)
  - [Description](#description)
  - [Requirements](#requirements)
  - [Dependencies](#dependencies)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Technical Notes](#technical-notes)
- [Procedure](#procedure)
- [Command](#command)
- [Module: authentication-service](#module-authentication-service)
  - [Description](#description)
  - [Requirements](#requirements)
  - [Dependencies](#dependencies)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Technical Notes](#technical-notes)
- [Output](#output)
- [Naming Conventions](#naming-conventions)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-create-module-issue |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Kanban Orchestration |
| **Agent** | api-coordinator |

## Purpose

Create a GitHub Issue for a module following the 1:1 principle: every module = exactly one issue.

## The 1:1 Principle

- Every module in the work breakdown is exactly ONE GitHub Issue
- Every agent assignment is ONE issue assignee
- Every status change is ONE board column move
- If it's not on the board, it doesn't exist

## Preconditions

- Module has been defined in the work breakdown
- Repository has write access
- Required labels exist (or will be auto-created)

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |
| `title` | string | Yes | Module title (descriptive) |
| `body` | string | Yes | Module description and requirements |
| `labels` | array | No | Labels to apply |
| `milestone` | string | No | Milestone to assign |
| `parent_issue` | int | No | Parent epic issue number |

## Module Issue Template

```markdown
## Module: <module-name>

### Description
<What this module does>

### Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Dependencies
blockedBy: [<issue-numbers>]
blocks: [<issue-numbers>]

### Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

### Technical Notes
<Implementation hints, constraints, etc.>
```

## Procedure

1. Format the issue body using the module template
2. Determine appropriate labels (type, priority, component)
3. Create the issue using gh CLI
4. Add to parent epic if specified
5. Return issue number and URL

## Command

```bash
# Create module issue
gh issue create \
  --repo "owner/repo" \
  --title "Module: Authentication Service" \
  --body "$(cat <<'EOF'
## Module: authentication-service

### Description
Implement JWT-based authentication for the API.

### Requirements
- [ ] Login endpoint with email/password
- [ ] Token generation and validation
- [ ] Refresh token mechanism

### Dependencies
blockedBy: []
blocks: [45, 46]

### Acceptance Criteria
- [ ] Users can log in and receive JWT
- [ ] Protected routes validate tokens
- [ ] Tokens expire correctly

### Technical Notes
Use RS256 algorithm for token signing.
EOF
)" \
  --label "type:module,priority:high,component:api"
```

## Output

```json
{
  "issue_number": 42,
  "url": "https://github.com/owner/repo/issues/42",
  "title": "Module: Authentication Service",
  "labels": ["type:module", "priority:high", "component:api"]
}
```

## Naming Conventions

| Pattern | Example |
|---------|---------|
| Feature module | `Module: <Feature Name>` |
| Service module | `Module: <Service Name> Service` |
| Component module | `Module: <Component> Component` |
| Integration module | `Module: <System A> - <System B> Integration` |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Duplicate title | Issue with same title exists | Add version or date suffix |
| Label not found | Label doesn't exist | Use `--auto-create` or create labels first |
| Permission denied | No write access | Check repository permissions |

## Related Operations

- [op-add-issue-to-board.md](op-add-issue-to-board.md) - Add created issue to board
- [op-get-board-state.md](op-get-board-state.md) - Verify issue appears
