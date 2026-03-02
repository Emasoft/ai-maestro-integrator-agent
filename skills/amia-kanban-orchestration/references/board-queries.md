# Board Queries

This document provides GraphQL and CLI queries for retrieving board state and item information from GitHub Projects V2.

---

## Table of Contents

### Part 1: Basic Queries
See [board-queries-part1-basic.md](board-queries-part1-basic.md)

- 7.1 Full Board State - Get complete board with all items and field values
  - 7.1.1 GraphQL query for full project state
  - 7.1.2 Parse to summary format with jq
- 7.2 Items by Status - Get all items in a specific column
  - 7.2.1 GraphQL filter by status field
  - 7.2.2 Quick status queries with gh CLI
- 7.3 Items by Assignee - Get items assigned to specific agent
  - 7.3.1 CLI assignee filter
  - 7.3.2 GraphQL assignee filter
  - 7.3.3 Workload summary per assignee

### Part 2: Filtered Queries
See [board-queries-part2-filtered.md](board-queries-part2-filtered.md)

- 7.4 Blocked Items - Get blocked items with blocker info
  - 7.4.1 Query blocked status with comments
  - 7.4.2 Parse blocker reason from comments
- 7.5 Items in AI Review / Human Review / Merge/Release - Get items in review pipeline
  - 7.5.1 Query review pipeline status with linked PRs
  - 7.5.2 Check review decision status
- 7.6 Column Summary - Count items per status column
  - 7.6.1 GraphQL count query
  - 7.6.2 Expected output format
  - 7.6.3 Calculate progress percentage

### Part 3: History and Completion
See [board-queries-part3-history.md](board-queries-part3-history.md)

- 7.7 Item History - Get timeline and transitions
  - 7.7.1 Issue timeline query
  - 7.7.2 Project item history limitations
  - 7.7.3 Suggested comment logging format
- 7.8 Check Completion - Check if all items are Done
  - 7.8.1 Completion check query
  - 7.8.2 Check logic with status counts
  - 7.8.3 Exit codes for stop hook

---

## Quick Reference

| Query Type | Use Case | Part |
|------------|----------|------|
| Full State | Dashboard display, initial load | Part 1 |
| By Status | Find items in specific column | Part 1 |
| By Assignee | Agent workload view | Part 1 |
| Blocked Items | Identify blockers | Part 2 |
| AI Review / Human Review / Merge/Release | Track review pipeline | Part 2 |
| Column Summary | Progress metrics | Part 2 |
| Item History | Audit trail | Part 3 |
| Completion Check | Stop hook validation | Part 3 |

---

## Common Patterns

### Project ID Required

All GraphQL queries require the project node ID:

```bash
# Get project node ID
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    organization(login: $owner) {
      projectV2(number: $number) {
        id
      }
    }
  }
' -f owner="OWNER" -F number=1 --jq '.data.organization.projectV2.id'
```

### Status Field Name

The status field is typically named "Status" but may vary. Query field names:

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              name
              options { name }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID"
```

### Pagination

For projects with more than 100 items, use cursor-based pagination:

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
            # ... fields
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" -f cursor="$CURSOR"
```
