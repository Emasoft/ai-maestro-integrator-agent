# Agent Assignment via Board

## Table of Contents

- 4.1 [Assignment principle: issue assignee = responsible agent](#41-assignment-principle)
- 4.2 [How to assign issues via CLI](#42-assign-via-cli)
- 4.3 [How to assign issues via GraphQL](#43-assign-via-graphql)
- 4.4 [Agent naming conventions for GitHub](#44-naming-conventions)
- 4.5 [Verifying current assignments](#45-verify-assignments)
- 4.6 [Reassigning work between agents](#46-reassigning)
- 4.7 [Multi-agent collaboration on single issue](#47-multi-agent-collaboration)
- 4.8 [Assignment notifications via AI Maestro](#48-notifications)

---

## 4.1 Assignment Principle

## Assignment Methods

The system supports TWO assignment methods:

### Method A: Multi-Account (GitHub Assignees)

- Each AI agent has a GitHub account
- GitHub issue assignee = responsible agent
- See: [multi-user-workflow.md](../../amia-github-integration/references/multi-user-workflow.md)

### Method B: Single-Account (Labels)

- One GitHub account (repository owner)
- `assign:*` labels = responsible agent
- See: [single-account-workflow.md](../../amia-github-integration/references/single-account-workflow.md)

**Choose ONE method per project and use consistently.**

For help deciding, see: [account-strategy-decision-guide.md](../../amia-github-integration/references/account-strategy-decision-guide.md)

### Why Assignees/Labels as Source of Truth?

| Alternative | Problem |
|-------------|---------|
| Memory tracking | Lost on session restart |
| Claude Tasks files | Not visible to other agents |
| Comments | Hard to parse programmatically |
| Separate tracking system | Syncing overhead |

### Assignment Rules

1. **One primary assignee/label per module** - The first assignee (or agent label) is the owner
2. **Assignment moves with status** - Assignment persists across status changes
3. **Unassigned = Available** - Items without assignee/agent label can be picked up
4. **Orchestrator assigns** - Only orchestrator should assign from Todo

---

## 4.2 Assign via CLI

### Single Assignee

```bash
# Assign issue #42 to agent-1
gh issue edit 42 --add-assignee agent-1
```

### Multiple Assignees (Collaboration)

```bash
# Assign issue #42 to agent-1 and agent-2
gh issue edit 42 --add-assignee agent-1 --add-assignee agent-2
```

### Remove Assignee

```bash
# Remove agent-1 from issue #42
gh issue edit 42 --remove-assignee agent-1
```

### Assign Self

```bash
# Agent assigns themselves
gh issue edit 42 --add-assignee @me
```

### Combined: Create and Assign

```bash
gh issue create \
  --title "[MODULE] auth-core: Implement JWT validation" \
  --body "..." \
  --assignee agent-1 \
  --label "type:feature,module:auth-core"
```

---

## 4.3 Assign via GraphQL

### Get Issue Node ID

```bash
ISSUE_ID=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        id
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=42 | jq -r '.data.repository.issue.id')
```

### Get User Node ID

```bash
USER_ID=$(gh api graphql -f query='
  query($login: String!) {
    user(login: $login) {
      id
    }
  }
' -f login="agent-1" | jq -r '.data.user.id')
```

### Add Assignee

```bash
gh api graphql -f query='
  mutation($issueId: ID!, $assigneeIds: [ID!]!) {
    addAssigneesToAssignable(input: {
      assignableId: $issueId
      assigneeIds: $assigneeIds
    }) {
      assignable {
        ... on Issue {
          assignees(first: 5) {
            nodes { login }
          }
        }
      }
    }
  }
' -f issueId="$ISSUE_ID" -f assigneeIds="[\"$USER_ID\"]"
```

### Remove Assignee

```bash
gh api graphql -f query='
  mutation($issueId: ID!, $assigneeIds: [ID!]!) {
    removeAssigneesFromAssignable(input: {
      assignableId: $issueId
      assigneeIds: $assigneeIds
    }) {
      assignable {
        ... on Issue {
          assignees(first: 5) {
            nodes { login }
          }
        }
      }
    }
  }
' -f issueId="$ISSUE_ID" -f assigneeIds="[\"$USER_ID\"]"
```

---

## 4.4 Naming Conventions

### AI Agent GitHub Usernames

AI agents should have GitHub accounts with recognizable naming:

| Pattern | Example | Use Case |
|---------|---------|----------|
| `agent-{role}` | `agent-implementer` | Role-based |
| `agent-{number}` | `agent-1`, `agent-2` | Numbered agents |
| `{project}-agent-{n}` | `alpha-agent-1` | Project-specific |
| `ai-{name}` | `ai-developer` | AI-prefix convention |

### Mapping AI Maestro Sessions to GitHub

| AI Maestro Session | GitHub Username |
|--------------------|-----------------|
| `implementer-1` | `implementer-1` |
| `helper-agent-generic` | `helper-generic` |
| `code-reviewer` | `code-reviewer` |

**Best Practice:** Use the same name for AI Maestro session and GitHub username where possible.

### Human Developer Usernames

Human developers use their normal GitHub usernames. No special convention needed.

---

## 4.5 Verify Assignments

### List All Assignments for Project

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            content {
              ... on Issue {
                number
                title
                assignees(first: 5) {
                  nodes { login }
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | {
      issue: .content.number,
      title: .content.title,
      assignees: [.content.assignees.nodes[].login]
    }
'
```

### Find Items Assigned to Specific Agent

```bash
gh issue list --assignee agent-1 --json number,title,state
```

### Find Unassigned Items

```bash
gh issue list --search "no:assignee is:open" --json number,title
```

### Check Specific Issue Assignment

```bash
gh issue view 42 --json assignees --jq '.assignees[].login'
```

---

## 4.6 Reassigning

### When to Reassign

| Scenario | Action |
|----------|--------|
| Agent blocked | Reassign to available agent |
| Agent overloaded | Move to less busy agent |
| Agent session ended | Reassign to new session |
| Specialization needed | Reassign to expert agent |
| Handoff requested | Transfer to requesting agent |

### Reassignment Process

1. **Notify current assignee** (if active)
2. **Remove current assignee**
3. **Add new assignee**
4. **Comment on issue** explaining reassignment
5. **Notify new assignee** via AI Maestro

### CLI Commands

```bash
# Reassign from agent-1 to agent-2
gh issue edit 42 --remove-assignee agent-1
gh issue edit 42 --add-assignee agent-2
gh issue comment 42 --body "Reassigned from @agent-1 to @agent-2. Reason: [reason]"
```

### Reassignment Comment Template

```markdown
## Reassignment

**From:** @agent-1
**To:** @agent-2
**Reason:** Agent-1 session ended, work needs to continue
**Context:** PR draft exists at #123, tests in progress
```

---

## 4.7 Multi-Agent Collaboration

Sometimes multiple agents need to work on a single issue. GitHub supports multiple assignees.

### Collaboration Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| Primary + Reviewer | One implements, one reviews | Code review workflow |
| Pair Programming | Two agents work together | Complex problem |
| Specialist Support | Main agent + domain expert | Need expertise |
| Handoff Chain | Sequential ownership | Phase-based work |

### Adding Collaborators

```bash
# Primary owner + collaborator
gh issue edit 42 --add-assignee agent-1 --add-assignee agent-2
```

### Collaboration Rules

1. **First assignee is primary owner** - Responsible for completion
2. **Additional assignees are collaborators** - Supporting role
3. **Primary drives status changes** - Others can comment
4. **Clear communication required** - Avoid duplicate work

### Collaboration Comment Template

```markdown
## Collaboration Setup

**Primary:** @agent-1 (owns implementation)
**Collaborator:** @agent-2 (code review support)

### Division of Work
- agent-1: Implement feature, write tests
- agent-2: Review code, suggest improvements
```

---

## 4.8 Notifications

### AI Maestro Notification on Assignment

When assigning an issue, notify the agent via AI Maestro. Send a message using the `agent-messaging` skill with:

- **Recipient**: `implementer-1`
- **Subject**: `New Assignment: Issue #42`
- **Priority**: `high`
- **Content**: `{"type": "assignment", "message": "You have been assigned to issue #42: [MODULE] auth-core. Please move to In Progress when you start work."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Notification Template

```json
{
  "type": "assignment",
  "message": "You have been assigned to issue #42: [title]. Please move to In Progress when you start.",
  "data": {
    "issue_number": 42,
    "title": "[MODULE] auth-core: Implement JWT validation",
    "url": "https://github.com/owner/repo/issues/42",
    "priority": "high"
  }
}
```

### Reassignment Notification

**Notify old assignee:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `agent-1` (the old assignee)
- **Subject**: `Issue #42 Reassigned`
- **Priority**: `normal`
- **Content**: `{"type": "reassignment", "message": "Issue #42 has been reassigned from you to agent-2. Please hand off any work in progress."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Notify new assignee:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `agent-2` (the new assignee)
- **Subject**: `New Assignment: Issue #42 (Reassigned)`
- **Priority**: `high`
- **Content**: `{"type": "assignment", "message": "Issue #42 has been reassigned to you from agent-1. Context: [context]. Please continue work."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.
