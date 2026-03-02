# Board Queries - Part 2: Filtered Queries

This part covers filtered queries: blocked items, review status, and column summaries.

## Table of Contents

- [7.4 Blocked Items](#74-blocked-items)
  - [Query Blocked Status](#query-blocked-status)
  - [Parse Blocker Reason](#parse-blocker-reason)
- [7.5 Items in Review Pipeline (AI Review / Human Review / Merge/Release)](#75-items-in-review-pipeline)
  - [Query Review Pipeline Status](#query-review-pipeline-status)
  - [Check Review Status](#check-review-status)
- [7.6 Column Summary](#76-column-summary)
  - [GraphQL Query](#graphql-query)
  - [Expected Output](#expected-output)
  - [Progress Percentage](#progress-percentage)

---

## 7.4 Blocked Items

Get all blocked items with their blocker information.

### Query Blocked Status

```bash
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
                body
                assignees(first: 3) { nodes { login } }
                labels(first: 10) { nodes { name } }
                timelineItems(last: 10, itemTypes: [ISSUE_COMMENT]) {
                  nodes {
                    ... on IssueComment {
                      body
                      createdAt
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | select(.fieldValues.nodes[] | select(.field.name == "Status" and .name == "Blocked"))
  | {
      issue: .content.number,
      title: .content.title,
      assignees: [.content.assignees.nodes[].login],
      labels: [.content.labels.nodes[].name],
      recent_comments: [.content.timelineItems.nodes[].body]
    }
'
```

### Parse Blocker Reason

The blocker reason is typically in the most recent comment. Look for "## Blocked" section.

```bash
# Get last comment from blocked issue
gh issue view 42 --json body,comments --jq '.comments[-1].body'
```

---

## 7.5 Items in Review Pipeline

Get items that have PRs awaiting review.

### Query Review Pipeline Status

```bash
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
                assignees(first: 3) { nodes { login } }
                timelineItems(last: 20, itemTypes: [CROSS_REFERENCED_EVENT]) {
                  nodes {
                    ... on CrossReferencedEvent {
                      source {
                        ... on PullRequest {
                          number
                          title
                          state
                          merged
                          url
                          reviewDecision
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | select(.fieldValues.nodes[] | select(.field.name == "Status" and (.name == "AI Review" or .name == "Human Review" or .name == "Merge/Release")))
  | {
      issue: .content.number,
      title: .content.title,
      pr: (.content.timelineItems.nodes[] | select(.source.state == "OPEN") | {
        number: .source.number,
        url: .source.url,
        review_status: .source.reviewDecision
      })
    }
'
```

### Check Review Status

```bash
# Get PRs linked to issue
gh pr list --search "closes:#42" --json number,title,state,reviewDecision
```

---

## 7.6 Column Summary

Get count of items per status column.

### GraphQL Query

```bash
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
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  [.data.node.items.nodes[].fieldValues.nodes[] | select(.field.name == "Status") | .name]
  | group_by(.)
  | map({status: .[0], count: length})
  | sort_by(.status)
'
```

### Expected Output

```json
[
  {"status": "Backlog", "count": 5},
  {"status": "Blocked", "count": 1},
  {"status": "Done", "count": 12},
  {"status": "In Progress", "count": 3},
  {"status": "AI Review", "count": 1},
  {"status": "Human Review", "count": 0},
  {"status": "Merge/Release", "count": 1},
  {"status": "Todo", "count": 4}
]
```

### Progress Percentage

```bash
# Calculate completion percentage
gh api graphql -f query='...' | jq '
  . as $all |
  ($all | map(select(.status == "Done")) | length) as $done |
  ($all | length) as $total |
  {
    done: $done,
    total: $total,
    percentage: (($done / $total) * 100 | floor)
  }
'
```
