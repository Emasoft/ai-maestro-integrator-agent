# GitHub Projects V2 GraphQL Queries - Read Operations

## Table of Contents

1. [When starting with GitHub Projects API](#overview)
2. [When you need to find projects and their IDs](#project-discovery)
   - 2.1 List All Projects for Organization
   - 2.2 List All Projects for Repository
   - 2.3 Get Project Details by Number
3. [When working with project fields and options](#field-operations)
   - 3.1 Get All Project Fields
   - 3.2 Get Status Field Options
4. [When querying or filtering project items](#item-operations)
   - 4.1 Get All Project Items
   - 4.2 Get Items by Status
   - 4.3 Get Single Item Details

---

## Overview

This file contains **read-only GraphQL queries** for GitHub Projects V2 API operations. All queries use the `gh api graphql` command.

For **mutations** (creating, updating, deleting), see [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md).

---

## Project Discovery

### List All Projects for Organization

```bash
gh api graphql -f query='
  query($org: String!) {
    organization(login: $org) {
      projectsV2(first: 20) {
        nodes {
          id
          title
          number
          shortDescription
          closed
          url
        }
      }
    }
  }
' -f org="ORG_NAME"
```

### List All Projects for Repository

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      projectsV2(first: 20) {
        nodes {
          id
          title
          number
          shortDescription
          url
        }
      }
    }
  }
' -f owner="OWNER" -f repo="REPO"
```

### Get Project Details by Number

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      projectV2(number: $number) {
        id
        title
        shortDescription
        url
        closed
        createdAt
        updatedAt
        fields(first: 20) {
          nodes {
            ... on ProjectV2Field {
              id
              name
              dataType
            }
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
                color
              }
            }
            ... on ProjectV2IterationField {
              id
              name
              configuration {
                iterations {
                  id
                  title
                  startDate
                  duration
                }
              }
            }
          }
        }
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=1
```

---

## Field Operations

### Get All Project Fields

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        fields(first: 30) {
          nodes {
            ... on ProjectV2Field {
              id
              name
              dataType
            }
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
                color
                description
              }
            }
            ... on ProjectV2IterationField {
              id
              name
              configuration {
                duration
                startDay
                iterations {
                  id
                  title
                  startDate
                  duration
                }
                completedIterations {
                  id
                  title
                  startDate
                  duration
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID"
```

### Get Status Field Options

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
              color
            }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID"
```

---

## Item Operations

### Get All Project Items

```bash
gh api graphql -f query='
  query($projectId: ID!, $cursor: String) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100, after: $cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            type
            createdAt
            updatedAt
            isArchived
            fieldValues(first: 15) {
              nodes {
                ... on ProjectV2ItemFieldTextValue {
                  text
                  field { ... on ProjectV2Field { name } }
                }
                ... on ProjectV2ItemFieldNumberValue {
                  number
                  field { ... on ProjectV2Field { name } }
                }
                ... on ProjectV2ItemFieldDateValue {
                  date
                  field { ... on ProjectV2Field { name } }
                }
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  optionId
                  field { ... on ProjectV2SingleSelectField { name } }
                }
                ... on ProjectV2ItemFieldIterationValue {
                  title
                  startDate
                  duration
                  field { ... on ProjectV2IterationField { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                state
                url
                body
                createdAt
                closedAt
                author { login }
                assignees(first: 5) {
                  nodes { login }
                }
                labels(first: 10) {
                  nodes { name color }
                }
              }
              ... on PullRequest {
                number
                title
                state
                url
                body
                createdAt
                mergedAt
                author { login }
                assignees(first: 5) {
                  nodes { login }
                }
              }
              ... on DraftIssue {
                title
                body
                createdAt
              }
            }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID"
```

### Get Items by Status

```bash
gh api graphql -f query='
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
' -f projectId="PROJECT_NODE_ID" | jq '.data.node.items.nodes[] | select(.fieldValues.nodes[].name == "In Progress")'
```

### Get Single Item Details

```bash
gh api graphql -f query='
  query($itemId: ID!) {
    node(id: $itemId) {
      ... on ProjectV2Item {
        id
        type
        createdAt
        updatedAt
        fieldValues(first: 15) {
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
            body
            state
            url
          }
        }
      }
    }
  }
' -f itemId="ITEM_NODE_ID"
```

---

## Related Files

- [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md) - Item mutations, Issue/PR operations, Utility queries, Pagination, Error handling
