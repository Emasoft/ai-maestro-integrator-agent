# Core Operations

## Table of Contents

1. [When starting with GitHub Projects operations](#overview)
2. [When creating issues with project items](#create-issue-with-project-item)
3. [When updating project item status](#update-item-status)
4. [When querying all project items](#query-project-items)
5. [When linking PRs to issues](#link-pr-to-issue)
6. [When adding comments to issues](#add-comments)
7. [When managing assignees](#manage-assignees)

## Overview

This document covers the essential day-to-day operations for managing GitHub Projects V2 via CLI. For complete GraphQL query reference, see [graphql-queries.md](./graphql-queries.md).

## Create Issue with Project Item

Create an issue and add it to a project in two steps.

### Step 1: Create the Issue

```bash
gh issue create \
  --title "Implement User Authentication" \
  --body "$(cat <<'EOF'
## Description
Implement user authentication with JWT tokens.

## Acceptance Criteria
- [ ] Login endpoint working
- [ ] JWT token generation
- [ ] Token validation middleware
- [ ] Logout endpoint

## Technical Notes
Use existing bcrypt for password hashing.
EOF
)" \
  --label "type:feature,priority:high" \
  --assignee "@me"
```

### Step 2: Add to Project

```bash
# Add issue to project by URL
gh project item-add PROJECT_NUMBER --owner OWNER --url ISSUE_URL
```

### Combined Script

```bash
#!/bin/bash
# create-and-add-issue.sh

TITLE="$1"
BODY="$2"
LABELS="$3"
PROJECT_NUMBER="$4"
OWNER="$5"
REPO="$6"

# Create issue and capture URL
ISSUE_URL=$(gh issue create \
  --title "$TITLE" \
  --body "$BODY" \
  --label "$LABELS" \
  --repo "$OWNER/$REPO" \
  --json url --jq '.url')

# Add to project
gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$ISSUE_URL"

echo "Created: $ISSUE_URL"
```

## Update Item Status

Move a project item to a different status column.

### Using GraphQL Mutation

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: "PROJECT_ID"
        itemId: "ITEM_ID"
        fieldId: "STATUS_FIELD_ID"
        value: { singleSelectOptionId: "IN_PROGRESS_OPTION_ID" }
      }
    ) {
      projectV2Item {
        id
      }
    }
  }
'
```

### Finding Required IDs

Before updating status, you need the project ID, item ID, field ID, and option IDs.

**Get Project ID:**
```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      projectV2(number: $number) {
        id
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=1
```

**Get Status Field and Option IDs:**
```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            options { id name }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID"
```

### Status Update Script

```bash
#!/bin/bash
# update-status.sh PROJECT_ID ITEM_ID NEW_STATUS

PROJECT_ID="$1"
ITEM_ID="$2"
NEW_STATUS="$3"

# Get field info
STATUS_INFO=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            options { id name }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID")

FIELD_ID=$(echo "$STATUS_INFO" | jq -r '.data.node.field.id')
OPTION_ID=$(echo "$STATUS_INFO" | jq -r --arg status "$NEW_STATUS" '.data.node.field.options[] | select(.name == $status) | .id')

# Update status
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item { id }
    }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID"

echo "Updated item to: $NEW_STATUS"
```

## Query Project Items

Retrieve all items from a project with their status and content.

### Basic Query

```bash
gh api graphql -f query='
  query {
    node(id: "PROJECT_ID") {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
                ... on ProjectV2ItemFieldTextValue {
                  text
                  field { ... on ProjectV2Field { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                state
                assignees(first: 5) {
                  nodes { login }
                }
              }
              ... on PullRequest {
                number
                title
                state
              }
            }
          }
        }
      }
    }
  }
'
```

### Filter by Status

```bash
# Get all "In Progress" items
gh api graphql -f query='...' | jq '.data.node.items.nodes[] | select(.fieldValues.nodes[].name == "In Progress")'
```

### Query Script with Output Formatting

```bash
#!/bin/bash
# list-project-items.sh PROJECT_ID [STATUS]

PROJECT_ID="$1"
STATUS_FILTER="$2"

RESULT=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                state
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID")

if [ -n "$STATUS_FILTER" ]; then
  echo "$RESULT" | jq --arg status "$STATUS_FILTER" '
    .data.node.items.nodes[]
    | select(.fieldValues.nodes[] | .name == $status)
    | {id: .id, issue: .content.number, title: .content.title}
  '
else
  echo "$RESULT" | jq '.data.node.items.nodes[] | {id: .id, issue: .content.number, title: .content.title}'
fi
```

## Link PR to Issue

Link a pull request to an issue for automatic closing on merge.

### Via PR Body (Recommended)

Use closing keywords in the PR body:

```bash
gh pr create \
  --title "feat: implement user authentication" \
  --body "Closes #42

## Changes
- Added login endpoint
- Added JWT token generation
- Added validation middleware" \
  --base main \
  --head feature/user-auth
```

**Closing Keywords**: `Closes`, `Fixes`, `Resolves` (+ issue reference)

### Add PR to Same Project

```bash
# Get PR node ID
PR_ID=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        id
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=123 | jq -r '.data.repository.pullRequest.id')

# Add to project
gh api graphql -f query='
  mutation($projectId: ID!, $contentId: ID!) {
    addProjectV2ItemById(input: {
      projectId: $projectId
      contentId: $contentId
    }) {
      item { id }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f contentId="$PR_ID"
```

## Add Comments

Add comments to issues for status updates and documentation.

### Simple Comment

```bash
gh issue comment ISSUE_NUMBER --body "Status changed to **In Progress**. Agent dev-1 assigned."
```

### Formatted Comment

```bash
gh issue comment ISSUE_NUMBER --body "$(cat <<'EOF'
## Progress Update

**Status**: In Progress → AI Review
**Agent**: dev-agent-1
**Time**: 2024-01-15 14:30 UTC

### Changes Made
- Implemented login endpoint
- Added JWT token generation
- All tests passing

### Next Steps
- Awaiting code review
- Merge pending approval
EOF
)"
```

## Manage Assignees

### Add Assignee to Issue

```bash
gh issue edit ISSUE_NUMBER --add-assignee USERNAME
```

### Remove Assignee

```bash
gh issue edit ISSUE_NUMBER --remove-assignee USERNAME
```

### Via GraphQL

```bash
# Get user node ID first
USER_ID=$(gh api graphql -f query='
  query($login: String!) {
    user(login: $login) { id }
  }
' -f login="USERNAME" | jq -r '.data.user.id')

# Assign to issue
gh api graphql -f query='
  mutation($assignableId: ID!, $assigneeIds: [ID!]!) {
    addAssigneesToAssignable(input: {
      assignableId: $assignableId
      assigneeIds: $assigneeIds
    }) {
      assignable {
        ... on Issue {
          assignees(first: 5) { nodes { login } }
        }
      }
    }
  }
' -f assignableId="ISSUE_NODE_ID" -f assigneeIds="[\"$USER_ID\"]"
```
