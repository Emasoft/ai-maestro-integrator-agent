# Board Queries - Part 1: Basic Queries

This part covers fundamental board queries: full state, status filtering, and assignee filtering.

## Table of Contents

- [7.1 Full Board State](#71-full-board-state)
  - [GraphQL Query](#graphql-query)
  - [Parse Full State](#parse-full-state)
- [7.2 Items by Status](#72-items-by-status)
  - [Query with Filter](#query-with-filter)
  - [Quick Status Queries](#quick-status-queries)
- [7.3 Items by Assignee](#73-items-by-assignee)
  - [Using CLI](#using-cli)
  - [Using GraphQL](#using-graphql)
  - [Workload Summary](#workload-summary)

---

## 7.1 Full Board State

Get complete board state with all items and their field values.

### GraphQL Query

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        title
        items(first: 100) {
          totalCount
          nodes {
            id
            type
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
                url
                assignees(first: 5) {
                  nodes { login }
                }
                labels(first: 10) {
                  nodes { name }
                }
              }
              ... on PullRequest {
                number
                title
                state
                url
                merged
              }
            }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID"
```

### Parse Full State

```bash
# Parse to summary format
gh api graphql -f query='...' | jq '
  .data.node.items.nodes[] | {
    id: .id,
    issue: .content.number,
    title: .content.title,
    state: .content.state,
    status: (.fieldValues.nodes[] | select(.field.name == "Status") | .name),
    assignees: [.content.assignees.nodes[].login],
    labels: [.content.labels.nodes[].name]
  }
'
```

---

## 7.2 Items by Status

Get all items in a specific column.

### Query with Filter

```bash
STATUS="In Progress"

gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValues(first: 5) {
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
                assignees(first: 5) { nodes { login } }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq --arg status "$STATUS" '
  .data.node.items.nodes[]
  | select(.fieldValues.nodes[] | select(.field.name == "Status" and .name == $status))
  | {
      id: .id,
      issue: .content.number,
      title: .content.title,
      assignees: [.content.assignees.nodes[].login]
    }
'
```

### Quick Status Queries

```bash
# All Todo items
gh issue list --project "Project Name" --search "status:Todo" --json number,title,assignees

# All In Progress items
gh issue list --project "Project Name" --search "status:\"In Progress\"" --json number,title,assignees

# All Blocked items
gh issue list --label "blocked" --json number,title,assignees
```

---

## 7.3 Items by Assignee

Get all items assigned to a specific agent.

### Using CLI

```bash
# All issues assigned to agent-1
gh issue list --assignee agent-1 --json number,title,state,labels
```

### Using GraphQL

```bash
ASSIGNEE="agent-1"

gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            fieldValues(first: 5) {
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
                assignees(first: 5) { nodes { login } }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq --arg assignee "$ASSIGNEE" '
  .data.node.items.nodes[]
  | select(.content.assignees.nodes[] | .login == $assignee)
  | {
      issue: .content.number,
      title: .content.title,
      status: (.fieldValues.nodes[] | select(.field.name == "Status") | .name)
    }
'
```

### Workload Summary

```bash
# Count items per assignee
gh api graphql -f query='...' | jq '
  [.data.node.items.nodes[].content.assignees.nodes[].login]
  | group_by(.)
  | map({assignee: .[0], count: length})
  | sort_by(.count) | reverse
'
```
