# GitHub Projects V2 Operations

## Use-Case TOC

- When you need to create a new project board → [Creating Projects V2 Board](#creating-projects-v2-board)
- When you need to add issues to a project → [Adding Issues to Projects](#adding-issues-to-projects)
- When you need to update issue status → [Updating Issue Status](#updating-issue-status)
- When you need to configure project fields → [Configuring Custom Fields](#configuring-custom-fields)
- When you need to set up automation → [Setting Up Automation Rules](#setting-up-automation-rules)
- When you need to sync agent tasks with GitHub → [Bidirectional Sync Workflow](#bidirectional-sync-workflow)

## Table of Contents

- [Creating Projects V2 Board](#creating-projects-v2-board)
  - [Create New Project](#create-new-project)
  - [List Existing Projects](#list-existing-projects)
  - [View Project Details](#view-project-details)
- [Adding Issues to Projects](#adding-issues-to-projects)
  - [Add Single Issue](#add-single-issue)
  - [Add Issues in Bulk](#add-issues-in-bulk)
  - [Verify Issue Was Added](#verify-issue-was-added)
- [Updating Issue Status](#updating-issue-status)
  - [Understanding Status Fields](#understanding-status-fields)
  - [Get Field IDs](#get-field-ids)
  - [Update Issue Status](#update-issue-status)
  - [Automated Status Update Script](#automated-status-update-script)
- [Configuring Custom Fields](#configuring-custom-fields)
  - [Create Custom Field](#create-custom-field)
  - [Common Custom Fields](#common-custom-fields)
  - [Update Custom Fields via API](#update-custom-fields-via-api)
- [Setting Up Automation Rules](#setting-up-automation-rules)
  - [Built-in Automation Options](#built-in-automation-options)
  - [Configuring Auto-add Workflow](#configuring-auto-add-workflow)
  - [Configuring Auto-archive Workflow](#configuring-auto-archive-workflow)
  - [Custom Automation with GitHub Actions](#custom-automation-with-github-actions)
- [Bidirectional Sync Workflow](#bidirectional-sync-workflow)
  - [Sync Direction 1: Agent → GitHub](#sync-direction-1-agent--github)
  - [Sync Direction 2: GitHub → Agent](#sync-direction-2-github--agent)
  - [Monitoring Sync Health](#monitoring-sync-health)
  - [Conflict Resolution](#conflict-resolution)
- [Best Practices](#best-practices)

## Creating Projects V2 Board

GitHub Projects V2 provides a table-based project management interface.

### Create New Project

```bash
gh project create \
  --title "Project Name" \
  --owner "@username"
```

**Parameters:**

- `--title`: Name of the project (required)
- `--owner`: Owner of the project (username or organization)

**Example:**

```bash
gh project create \
  --title "Backend Development Q1 2024" \
  --owner "@backend-team"
```

### List Existing Projects

```bash
# List your projects
gh project list --owner "@me"

# List organization projects
gh project list --owner "@org-name"
```

**Example Output:**

```
NUMBER  TITLE                          STATE  ITEMS
1       Backend Development Q1 2024    OPEN   42
2       Frontend Redesign              OPEN   28
3       Infrastructure Improvements    OPEN   15
```

### View Project Details

```bash
gh project view <project_number> --owner "@username"
```

## Adding Issues to Projects

After creating a project, add issues to it.

### Add Single Issue

```bash
gh project item-add <project_number> \
  --owner "@username" \
  --url "https://github.com/owner/repo/issues/123"
```

**Alternative using issue ID:**

```bash
# Get issue ID first
ISSUE_ID=$(gh issue view 123 --json id --jq '.id')

# Add to project
gh project item-add <project_number> \
  --owner "@username" \
  --id "$ISSUE_ID"
```

### Add Issues in Bulk

```bash
#!/bin/bash
# add-issues-to-project.sh

PROJECT_ID=1
OWNER="@me"
REPO="owner/repo"

# Get all open issues
gh issue list --repo "$REPO" --limit 100 --json number --jq '.[].number' | while read ISSUE_NUM; do
  echo "Adding issue #$ISSUE_NUM to project $PROJECT_ID"

  gh project item-add "$PROJECT_ID" \
    --owner "$OWNER" \
    --url "https://github.com/$REPO/issues/$ISSUE_NUM"

  sleep 1  # Rate limiting
done
```

### Verify Issue Was Added

```bash
gh project item-list <project_number> --owner "@username" --limit 100
```

## Updating Issue Status

Update issue status within Projects V2 board.

### Understanding Status Fields

Projects V2 uses custom fields for status. The canonical 8-column system uses these status values:

- **Backlog** - Not yet scheduled for work
- **Todo** - Ready to start, prioritized
- **In Progress** - Active work by assigned agent
- **AI Review** - Integrator (AMIA) reviews the PR
- **Human Review** - User reviews (big tasks only)
- **Merge/Release** - Approved and ready to merge
- **Done** - Completed and merged
- **Blocked** - Cannot proceed at any stage

### Get Field IDs

Before updating status, you need the field ID:

```bash
gh project field-list <project_number> --owner "@username"
```

**Example Output:**

```
ID                      NAME        TYPE
PVTF_lADOAA...         Status      SINGLE_SELECT
PVTF_lADOAB...         Priority    SINGLE_SELECT
PVTF_lADOAC...         Assignee    TEXT
```

Save the Status field ID for use in updates.

### Update Issue Status

```bash
gh project item-edit <project_number> \
  --id "<item_id>" \
  --field-id "<status_field_id>" \
  --single-select-option-id "<option_id>"
```

**Alternative using field name:**

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "FIELD_ID"
      value: {
        singleSelectOptionId: "OPTION_ID"
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}'
```

### Automated Status Update Script

```bash
#!/bin/bash
# update-status.sh - Update issue status in Projects V2

PROJECT_ID=$1
ISSUE_URL=$2
NEW_STATUS=$3

if [ -z "$PROJECT_ID" ] || [ -z "$ISSUE_URL" ] || [ -z "$NEW_STATUS" ]; then
  echo "Usage: ./update-status.sh <project_id> <issue_url> <status>"
  echo "Status values: Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked"
  exit 1
fi

# Get item ID for this issue in the project
ITEM_ID=$(gh api graphql -f query="
query {
  resource(url: \"$ISSUE_URL\") {
    ... on Issue {
      projectItems(first: 10) {
        nodes {
          id
          project {
            number
          }
        }
      }
    }
  }
}" --jq ".data.resource.projectItems.nodes[] | select(.project.number == $PROJECT_ID) | .id")

if [ -z "$ITEM_ID" ]; then
  echo "Error: Issue not found in project"
  exit 1
fi

# Update status (requires field ID and option ID - see script comments)
echo "Would update item $ITEM_ID to status: $NEW_STATUS"
# Add actual update command here with proper field/option IDs
```

## Configuring Custom Fields

Projects V2 supports custom fields beyond the default fields.

### Create Custom Field

Custom fields must be created through the GitHub web interface:

1. Go to your project
2. Click "+ New field" in the table header
3. Choose field type (Text, Number, Date, Single select, Iteration)
4. Configure field options

### Common Custom Fields

**Priority Field (Single Select):**

- High
- Medium
- Low

**Due Date Field (Date):**

- NOT USED per RULE 13 (no deadlines allowed)

**Effort Field (Number):**

- Complexity points (NOT time estimates per RULE 13)

**Team Field (Single Select):**

- Backend
- Frontend
- DevOps
- QA

### Update Custom Fields via API

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "PRIORITY_FIELD_ID"
      value: {
        singleSelectOptionId: "HIGH_OPTION_ID"
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}'
```

## Setting Up Automation Rules

Projects V2 supports built-in automation for status transitions.

### Built-in Automation Options

**Auto-add to project:**

- Automatically add new issues to the project
- Configuration: Project settings → Workflows → Auto-add

**Auto-archive:**

- Automatically archive closed issues
- Configuration: Project settings → Workflows → Auto-archive

**Status auto-update:**

- Update status when issue/PR state changes
- Configuration: Project settings → Workflows → Item closed

### Configuring Auto-add Workflow

1. Navigate to project settings
2. Click "Workflows"
3. Enable "Auto-add to project"
4. Configure filters:
   - Repository: Select repositories
   - Issue type: Issues, Pull requests, or both
   - Labels: Only add issues with specific labels

**Example Configuration:**

```
Auto-add to project: ON
Repositories: backend-api, frontend-app
Issue type: Issues and pull requests
Labels: feature, bug (from 9-label system)
Default status: Backlog (or Todo for pre-prioritized items)
```

### Configuring Auto-archive Workflow

1. Navigate to project settings
2. Click "Workflows"
3. Enable "Auto-archive"
4. Configure when to archive:
   - When issue is closed
   - When PR is merged

### Custom Automation with GitHub Actions

For more complex automation, use GitHub Actions:

```yaml
# .github/workflows/sync-project-status.yml
name: Sync Project Status

on:
  issues:
    types: [opened, closed, reopened]
  pull_request:
    types: [opened, closed, reopened, ready_for_review]

jobs:
  update-project:
    runs-on: ubuntu-latest
    steps:
      - name: Update project status
        uses: actions/github-script@v7
        with:
          script: |
            const projectId = 'PROJECT_ID';
            const itemId = 'ITEM_ID';
            const statusFieldId = 'STATUS_FIELD_ID';

            // Update status based on event (canonical 8-column system)
            let newStatus = 'Backlog';
            if (context.payload.action === 'opened') {
              newStatus = 'Todo';
            } else if (context.payload.pull_request?.draft === false) {
              newStatus = 'AI Review';
            } else if (context.payload.action === 'closed') {
              newStatus = 'Done';
            }

            // Execute GraphQL mutation to update status
            // ... implementation details ...
```

## Bidirectional Sync Workflow

Keep agent tasks and GitHub Projects V2 synchronized in both directions.

### Sync Direction 1: Agent → GitHub

When agent creates or updates tasks, sync to GitHub:

**Phase 1: Detect Agent Changes**

- Monitor agent task creation
- Monitor agent task status updates
- Monitor agent task assignments

**Phase 2: Translate to GitHub Operations**

- New task → Create GitHub issue
- Status update → Update Projects V2 status
- Assignment → Update issue assignee

**Phase 3: Execute Sync**

```bash
python3 scripts/sync-agent-to-github.py \
  --agent-db "agent-tasks.db" \
  --github-owner "username" \
  --github-repo "repository" \
  --project-id "1"
```

### Sync Direction 2: GitHub → Agent

When GitHub issues are updated, sync to agent:

**Phase 1: Detect GitHub Changes**

- Use webhooks for real-time updates
- Or poll GitHub API for changes

**Phase 2: Translate to Agent Operations**

- Issue created → Create agent task
- Status changed → Update agent task status
- Issue closed → Mark agent task complete

**Phase 3: Execute Sync**

```bash
python3 scripts/sync-github-to-agent.py \
  --github-owner "username" \
  --github-repo "repository" \
  --project-id "1" \
  --agent-db "agent-tasks.db"
```

### Monitoring Sync Health

**Check Last Sync Time:**

```bash
# View last sync timestamp
cat .last-sync-timestamp

# View sync logs
tail -f sync-projects-v2.log
```

**Verify Sync Integrity:**

```bash
# Count issues in GitHub
GITHUB_COUNT=$(gh issue list --limit 1000 --json number | jq 'length')

# Count tasks in agent system
AGENT_COUNT=$(sqlite3 agent-tasks.db "SELECT COUNT(*) FROM tasks")

echo "GitHub issues: $GITHUB_COUNT"
echo "Agent tasks: $AGENT_COUNT"

if [ "$GITHUB_COUNT" != "$AGENT_COUNT" ]; then
  echo "WARNING: Sync mismatch detected"
fi
```

### Conflict Resolution

When both systems update simultaneously:

**Rule 1: GitHub Wins**

- GitHub is the source of truth
- Agent reconciles to match GitHub

**Rule 2: Audit Trail**

- Log all conflicts
- Report to monitoring system

**Rule 3: Manual Override**

- Agent can force-update with explicit flag
- Requires confirmation

**Example Conflict Resolution:**

```bash
# Detect conflict
if [ "$AGENT_STATUS" != "$GITHUB_STATUS" ]; then
  echo "Conflict detected: Agent says '$AGENT_STATUS', GitHub says '$GITHUB_STATUS'"
  echo "Resolving: GitHub wins"

  # Update agent to match GitHub
  update_agent_task "$TASK_ID" "$GITHUB_STATUS"

  # Log conflict
  echo "$(date): Conflict resolved - Task $TASK_ID updated to $GITHUB_STATUS" >> conflicts.log
fi
```

## Best Practices

1. **Create one project per major area** - Don't create too many projects
2. **Use consistent status values** - Standardize across all projects
3. **Configure automation early** - Set up auto-add and auto-archive from the start
4. **Link all PRs to issues** - Ensures proper project tracking
5. **Run sync regularly** - Hourly for active projects, daily for stable projects
6. **Monitor sync logs** - Check for errors and conflicts
7. **Use custom fields sparingly** - Only add fields that will be actively used
8. **Archive completed items** - Keep project board focused on active work
