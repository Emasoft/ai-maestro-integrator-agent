# Issue-to-Module Mapping

## Table of Contents

- 3.1 [The 1:1 principle: every module is exactly one issue](#31-the-11-principle)
- 3.2 [Module issue template structure](#32-template-structure)
- 3.3 [Required fields for module issues](#33-required-fields)
- 3.4 [Naming conventions for module issues](#34-naming-conventions)
- 3.5 [Linking module issues to parent epics](#35-linking-to-epics)
- 3.6 [Creating module issues from plan files](#36-from-plan-files)
- 3.7 [Bulk module issue creation workflow](#37-bulk-creation)
- 3.8 [Module issue lifecycle from creation to closure](#38-lifecycle)

---

## 3.1 The 1:1 Principle

**Every module is exactly one GitHub issue. No exceptions.**

This means:
- One module = One issue = One work item on the board
- If work requires multiple issues, it's multiple modules
- If work is too big for one issue, break it into sub-modules

### Why 1:1 Mapping?

| Benefit | Explanation |
|---------|-------------|
| Clear ownership | One assignee per module |
| Trackable progress | Issue state = module state |
| Simple queries | Count issues = count modules |
| Clean board | One card per work unit |
| PR linking | One PR per issue per module |

### What Is a Module?

A module is a self-contained unit of work that:
- Has clear inputs and outputs
- Can be assigned to one agent
- Can be completed in a bounded time
- Has testable acceptance criteria
- Results in one PR (typically)

### Module Size Guidelines

| Size | Description | Typical Duration |
|------|-------------|------------------|
| Small | Single function or small feature | 1-4 hours |
| Medium | Component or subsystem | 4-16 hours |
| Large | Major feature (should consider splitting) | 16-40 hours |
| Epic | Too big - must be split into modules | N/A |

---

## 3.2 Template Structure

Every module issue MUST follow this template:

```markdown
## Description

[One paragraph describing what this module does and why it's needed]

## Acceptance Criteria

- [ ] [Criterion 1 - specific, testable]
- [ ] [Criterion 2 - specific, testable]
- [ ] [Criterion 3 - specific, testable]

## Technical Notes

- [Implementation guidance]
- [Dependencies]
- [Constraints]

## Test Requirements

- [ ] Unit tests cover [specific functionality]
- [ ] Integration tests cover [specific scenarios]

## Files to Create/Modify

- `path/to/file1.py` - [what to do]
- `path/to/file2.py` - [what to do]

## Parent Issue

Relates to #[EPIC_NUMBER]
```

---

## 3.3 Required Fields

Every module issue MUST have these fields populated:

### Issue Fields

| Field | Required | Example |
|-------|----------|---------|
| Title | Yes | "[MODULE] auth-core: Implement JWT validation" |
| Body | Yes | Template above |
| Labels | Yes | `type:feature`, `module:auth-core` |
| Assignee | When in Todo+ | `agent-1` |
| Milestone | Recommended | `Sprint 3` |
| Project | Yes | Added to Kanban board |

### Project Fields (on board)

| Field | Required | Example |
|-------|----------|---------|
| Status | Yes | `Todo`, `In Progress`, etc. |
| Priority | Recommended | `High`, `Medium`, `Low` |
| Effort | Recommended | `S`, `M`, `L` |
| Iteration | If using sprints | `Sprint 3` |

---

## 3.4 Naming Conventions

### Issue Title Format

```
[MODULE] <module-name>: <brief description>
```

**Examples:**
- `[MODULE] auth-core: Implement JWT token validation`
- `[MODULE] data-pipeline: Add batch processing`
- `[MODULE] ui-components: Create login form`

### Module Name Rules

| Rule | Good | Bad |
|------|------|-----|
| Lowercase with hyphens | `auth-core` | `AuthCore`, `auth_core` |
| 2-4 words max | `data-pipeline` | `data-transformation-and-processing-service` |
| Descriptive | `user-service` | `module-1` |
| No special chars | `api-gateway` | `api/gateway` |

### Label Conventions

Always include:
- `type:feature` or `type:bug` or `type:chore`
- `module:<module-name>` - custom label for filtering

Optional:
- `priority:high`, `priority:medium`, `priority:low`
- `effort:S`, `effort:M`, `effort:L`

---

## 3.5 Linking to Epics

Large features are broken into multiple modules. The parent feature is an "Epic" issue.

### Epic Issue

```markdown
# [EPIC] User Authentication System

## Overview
Complete user authentication with login, logout, JWT tokens, and password reset.

## Modules

- [ ] #42 [MODULE] auth-core: Implement JWT validation
- [ ] #43 [MODULE] auth-api: Create login/logout endpoints
- [ ] #44 [MODULE] auth-ui: Build login form component
- [ ] #45 [MODULE] auth-tests: Integration test suite

## Progress
<!-- Updated automatically -->
2/4 modules complete
```

### Module Issue Reference

In each module issue body:
```markdown
## Parent Issue

Relates to #41 ([EPIC] User Authentication System)
```

### Tracking Epic Progress

Query all modules for an epic:
```bash
gh issue list --label "epic:auth-system" --json number,title,state
```

Or use GitHub's task list checkbox feature for automatic progress tracking.

---

## 3.6 From Plan Files

When the orchestrator creates a plan file, modules should be extracted and converted to issues.

### Plan File Format

```markdown
# Implementation Plan: Feature X

## Modules

### Module 1: auth-core
- Description: JWT validation middleware
- Files: src/auth/jwt.py, tests/test_jwt.py
- Acceptance: Validates tokens, rejects expired tokens

### Module 2: auth-api
- Description: Login and logout REST endpoints
- Files: src/api/auth.py, tests/test_auth_api.py
- Acceptance: POST /login returns token, POST /logout invalidates
```

### Conversion Process

1. Read plan file
2. Extract each module section
3. Create issue with template
4. Add to project board
5. Update plan file with issue links

### Script: Plan to Issues

```bash
# Use the github-projects-sync script
python3 ../github-projects-sync/scripts/sync_tasks.py \
  --plan-file docs/plan-feature-x.md \
  --project-number 1 \
  --owner OWNER \
  --repo REPO
```

---

## 3.7 Bulk Creation

When creating many module issues at once (e.g., project kickoff):

### Step 1: Prepare Module List

Create a JSON file with all modules:

```json
{
  "modules": [
    {
      "name": "auth-core",
      "title": "Implement JWT validation",
      "description": "...",
      "acceptance": ["Validates tokens", "Rejects expired"],
      "labels": ["type:feature", "priority:high"]
    },
    {
      "name": "auth-api",
      "title": "Create login/logout endpoints",
      "description": "...",
      "acceptance": ["POST /login works", "POST /logout works"],
      "labels": ["type:feature", "priority:high"]
    }
  ]
}
```

### Step 2: Create Issues

```bash
for module in $(jq -r '.modules[].name' modules.json); do
  TITLE=$(jq -r --arg m "$module" '.modules[] | select(.name == $m) | .title' modules.json)
  BODY=$(jq -r --arg m "$module" '.modules[] | select(.name == $m) | .description' modules.json)
  LABELS=$(jq -r --arg m "$module" '.modules[] | select(.name == $m) | .labels | join(",")' modules.json)

  gh issue create \
    --title "[MODULE] $module: $TITLE" \
    --body "$BODY" \
    --label "$LABELS,module:$module"
done
```

### Step 3: Add to Project

```bash
PROJECT_NUMBER=1
OWNER=Emasoft

for url in $(gh issue list --label "module:" --json url --jq '.[].url'); do
  gh project item-add $PROJECT_NUMBER --owner $OWNER --url "$url"
done
```

---

## 3.8 Lifecycle

A module issue moves through these stages:

### Stage 1: Creation

```
[Created] -> [Backlog]
- Issue created with template
- Added to project board
- Status: Backlog
- Assignee: None
```

### Stage 2: Scheduling

```
[Backlog] -> [Todo]
- Prioritized for current iteration
- Assignee: Set to responsible agent
- Status: Todo
```

### Stage 3: Development

```
[Todo] -> [In Progress]
- Agent starts work
- Feature branch created
- Status: In Progress
```

### Stage 4: Review

```
[In Progress] -> [AI Review]
- PR created (Closes #N)
- Tests passing
- Status: AI Review
```

### Stage 5: Completion

```
[AI Review] -> [Merge/Release] -> [Done]
- PR merged
- Issue auto-closed
- Status: Done
```

### Lifecycle Diagram

```
                          ┌─────────┐
                          │ Blocked │
                          └────┬────┘
                               │
     ┌────────┐  ┌──────┐  ┌───┴───────┐  ┌─────────┐  ┌─────────┐  ┌──────┐
     │Backlog ├─►│ Todo ├─►│In Progress├─►│AI Review├─►│Merge/Rel├─►│ Done │
     └────────┘  └──────┘  └───────────┘  └─────────┘  └─────────┘  └──────┘
         │                       │               │
         │                       │               │
         ▼                       ▼               ▼
    Orchestrator           Agent moves      Auto on merge
    moves here             when starts      (PR closes issue)
```
