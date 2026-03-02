# PR Operations, Utilities & Helpers for GitHub Projects V2

This section covers pull request operations, utility queries, pagination, and error handling.

**Parent document**: [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md)

---

## Table of Contents

- 3.1 [Get PR Node ID](#get-pr-node-id)
- 3.2 [Link PR to Issue via Project](#link-pr-to-issue-via-project)
- 4.1 [Get Repository Node ID](#get-repository-node-id)
- 4.2 [Get User Node ID](#get-user-node-id)
- 4.3 [Get Label Node ID](#get-label-node-id)
- 4.4 [List All Labels](#list-all-labels)
- 5.0 [Pagination Helper](#pagination-helper)
- 6.0 [Error Handling](#error-handling)

---

## Pull Request Operations

### Get PR Node ID

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        id
        number
        title
        state
        mergeable
        projectItems(first: 10) {
          nodes {
            id
            project { title }
          }
        }
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=123
```

### Link PR to Issue via Project

```bash
# First add PR to project
gh api graphql -f query='
  mutation($projectId: ID!, $contentId: ID!) {
    addProjectV2ItemById(input: {
      projectId: $projectId
      contentId: $contentId
    }) {
      item {
        id
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f contentId="PR_NODE_ID"
```

---

## Utility Queries

### Get Repository Node ID

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      id
      name
      url
    }
  }
' -f owner="OWNER" -f repo="REPO"
```

### Get User Node ID

```bash
gh api graphql -f query='
  query($login: String!) {
    user(login: $login) {
      id
      login
      name
    }
  }
' -f login="USERNAME"
```

### Get Label Node ID

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $name: String!) {
    repository(owner: $owner, name: $repo) {
      label(name: $name) {
        id
        name
        color
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -f name="bug"
```

### List All Labels

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      labels(first: 100) {
        nodes {
          id
          name
          color
          description
        }
      }
    }
  }
' -f owner="OWNER" -f repo="REPO"
```

---

## Pagination Helper

For queries that may return many results, use pagination:

```bash
# First page
CURSOR=""
while true; do
  RESULT=$(gh api graphql -f query='
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
              content {
                ... on Issue { number title }
              }
            }
          }
        }
      }
    }
  ' -f projectId="PROJECT_NODE_ID" -f cursor="$CURSOR")

  echo "$RESULT"

  HAS_NEXT=$(echo "$RESULT" | jq -r '.data.node.items.pageInfo.hasNextPage')
  if [ "$HAS_NEXT" != "true" ]; then
    break
  fi

  CURSOR=$(echo "$RESULT" | jq -r '.data.node.items.pageInfo.endCursor')
done
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `NOT_FOUND` | Invalid node ID | Verify ID exists and is correct type |
| `FORBIDDEN` | Insufficient permissions | Check auth scopes |
| `UNPROCESSABLE` | Invalid field value | Check field type and allowed values |
| `RATE_LIMITED` | Too many requests | Wait and retry with backoff |

### Check Rate Limit

```bash
gh api rate_limit | jq '.resources.graphql'
```

---

## Related Sections

- [Item Mutations](./graphql-queries-part2-mutations-section1-item-mutations.md)
- [Issue Operations](./graphql-queries-part2-mutations-section2-issue-operations.md)
- [Read Operations (Part 1)](./graphql-queries-part1-read-operations.md)
