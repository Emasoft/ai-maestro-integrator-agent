# Thread Conversation Tracking

This document explains how to track conversations within GitHub PR review threads, including getting thread history and finding unaddressed comments.

## Table of Contents

- 2.1 Getting thread history via GraphQL
  - 2.1.1 Query structure for review threads
  - 2.1.2 Pagination for threads with many comments
- 2.2 Tracking addressed vs unaddressed comments
  - 2.2.1 Definition of "addressed"
  - 2.2.2 Finding comments without replies
- 2.3 GitHub's comment threading model
  - 2.3.1 Root comments vs reply comments
  - 2.3.2 Outdated comments (when code changes)
- 2.4 Minimized comments handling
  - 2.4.1 What minimized means
  - 2.4.2 When to consider minimized comments

---

## 2.1 Getting Thread History via GraphQL

### 2.1.1 Query Structure for Review Threads

To get complete thread information including all comments:

```graphql
query GetThreadDetails($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          diffSide
          comments(first: 100) {
            totalCount
            nodes {
              id
              body
              createdAt
              author {
                login
              }
              replyTo {
                id
              }
              isMinimized
              minimizedReason
            }
          }
        }
      }
    }
  }
}
```

**Key fields explained:**

| Field | Description |
|-------|-------------|
| `id` | Thread's GraphQL node ID (PRRT_xxx) |
| `isResolved` | Whether the thread is marked resolved |
| `isOutdated` | Whether the code has changed since comment |
| `path` | File path the comment is on |
| `line` | Line number in the diff |
| `startLine` | Start line for multi-line comments |
| `diffSide` | LEFT (old code) or RIGHT (new code) |
| `comments.nodes` | Array of all comments in the thread |
| `replyTo` | If set, this comment is a reply to another |

**Using gh CLI:**

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: 123) {
        reviewThreads(first: 50) {
          nodes {
            id
            isResolved
            path
            line
            comments(first: 50) {
              nodes {
                id
                body
                author { login }
                replyTo { id }
              }
            }
          }
        }
      }
    }
  }
'
```

### 2.1.2 Pagination for Threads with Many Comments

For PRs with many threads or threads with many comments, use cursor-based pagination:

**Paginating threads:**

```graphql
query GetThreadsPaginated($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 50, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          path
        }
      }
    }
  }
}
```

**Pagination workflow:**

1. First call: omit `$cursor` (or set to `null`)
2. Check `pageInfo.hasNextPage`
3. If `true`, make another call with `$cursor` = `pageInfo.endCursor`
4. Repeat until `hasNextPage` is `false`

**Paginating comments within a thread:**

```graphql
query GetThreadComments($threadId: ID!, $cursor: String) {
  node(id: $threadId) {
    ... on PullRequestReviewThread {
      comments(first: 50, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          body
          author { login }
        }
      }
    }
  }
}
```

---

## 2.2 Tracking Addressed vs Unaddressed Comments

### 2.2.1 Definition of "Addressed"

A comment is considered "addressed" when one of these conditions is met:

| Condition | How to Detect |
|-----------|---------------|
| Thread is resolved | `isResolved: true` on the thread |
| Author received a reply | Comment has a reply from another user |
| Comment is minimized | `isMinimized: true` on the comment |
| Comment is outdated AND thread resolved | `isOutdated: true` + `isResolved: true` |

**Unaddressed comments are:**
- In unresolved threads
- Have no replies from the PR author
- Are not minimized
- Are the root comment or a question/request

### 2.2.2 Finding Comments Without Replies

To find unaddressed comments, you need to:

1. Get all unresolved threads
2. For each thread, identify root comments (first comment)
3. Check if the PR author has replied to each root comment

**Algorithm:**

```
For each thread where isResolved = false:
    Get all comments in the thread
    Get the first comment (root comment)

    If root comment author != PR author:
        Check if any reply in the thread is from PR author
        If no reply from PR author exists:
            Mark root comment as "unaddressed"
```

**Query to get data needed:**

```graphql
query GetUnaddressedData($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      author {
        login
      }
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          path
          line
          comments(first: 100) {
            nodes {
              id
              body
              author {
                login
              }
              replyTo {
                id
              }
            }
          }
        }
      }
    }
  }
}
```

**Logic to determine unaddressed:**

```python
def find_unaddressed_comments(pr_author: str, threads: list) -> list:
    unaddressed = []

    for thread in threads:
        if thread['isResolved']:
            continue

        comments = thread['comments']['nodes']
        if not comments:
            continue

        # Get root comment (first in thread)
        root_comment = comments[0]

        # Skip if PR author made the root comment (self-review)
        if root_comment['author']['login'] == pr_author:
            continue

        # Check if PR author has replied anywhere in thread
        pr_author_replied = any(
            c['author']['login'] == pr_author
            for c in comments[1:]  # Skip root comment
        )

        if not pr_author_replied:
            unaddressed.append({
                'threadId': thread['id'],
                'commentId': root_comment['id'],
                'author': root_comment['author']['login'],
                'body': root_comment['body'],
                'path': thread['path'],
                'line': thread['line']
            })

    return unaddressed
```

---

## 2.3 GitHub's Comment Threading Model

### 2.3.1 Root Comments vs Reply Comments

GitHub review threads have a hierarchical structure:

```
Thread (PRRT_xxx)
├── Root Comment (first comment that created the thread)
│   └── Reply Comment 1
│       └── Reply Comment 2
│           └── Reply Comment 3
```

**Root comment characteristics:**
- Always the first comment in `comments.nodes` array
- `replyTo` field is `null`
- Creates the thread when submitted

**Reply comment characteristics:**
- Has `replyTo.id` pointing to the comment it replies to
- Position in array indicates chronological order

**Example response structure:**

```json
{
  "comments": {
    "nodes": [
      {
        "id": "PRRC_aaa",
        "body": "This should use const",
        "replyTo": null
      },
      {
        "id": "PRRC_bbb",
        "body": "Fixed in commit abc123",
        "replyTo": { "id": "PRRC_aaa" }
      },
      {
        "id": "PRRC_ccc",
        "body": "Thanks!",
        "replyTo": { "id": "PRRC_bbb" }
      }
    ]
  }
}
```

### 2.3.2 Outdated Comments (When Code Changes)

When the code at a comment's location changes (file modified, line changed), the thread becomes "outdated":

```graphql
{
  "isOutdated": true,
  "line": 42,
  "originalLine": 38
}
```

**What outdated means:**
- The comment was on line 38 in the original diff
- Code changes have shifted or modified that line
- The comment now shows at line 42 (best-effort placement)
- Or the comment may not be visible in the current diff

**Handling outdated threads:**

| Scenario | Recommended Action |
|----------|-------------------|
| Code change addressed the comment | Resolve the thread with a reply explaining |
| Code change unrelated to comment | Comment still needs addressing |
| Comment no longer applicable | Resolve with note that code was refactored |

**Query to get outdated status:**

```graphql
{
  reviewThreads(first: 100) {
    nodes {
      id
      isOutdated
      line
      originalLine
      isResolved
    }
  }
}
```

---

## 2.4 Minimized Comments Handling

### 2.4.1 What Minimized Means

Minimized comments are hidden by default in the GitHub UI. They're collapsed and require explicit expansion to view.

**Minimization reasons:**

| Reason | Meaning |
|--------|---------|
| `SPAM` | Flagged as spam |
| `ABUSE` | Flagged as abusive |
| `OFF_TOPIC` | Not relevant to the PR |
| `OUTDATED` | No longer applies |
| `RESOLVED` | Issue was addressed |
| `DUPLICATE` | Same as another comment |

**Query to get minimization info:**

```graphql
{
  comments(first: 100) {
    nodes {
      id
      body
      isMinimized
      minimizedReason
    }
  }
}
```

### 2.4.2 When to Consider Minimized Comments

**Generally ignore minimized comments when:**
- Finding unaddressed comments (they're intentionally hidden)
- Counting active discussion threads
- Generating review summaries

**Include minimized comments when:**
- Auditing all PR activity
- Investigating flagged content
- Building complete thread history

**Filtering out minimized:**

```python
active_comments = [
    c for c in comments
    if not c.get('isMinimized', False)
]
```

**Checking minimization reason:**

```python
# Only exclude if minimized for resolution/outdated
skip_reasons = {'OUTDATED', 'RESOLVED', 'DUPLICATE'}

relevant_comments = [
    c for c in comments
    if not c.get('isMinimized', False)
    or c.get('minimizedReason') not in skip_reasons
]
```

---

## Practical Examples

### Example: Get Summary of Thread Activity

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: 123) {
        reviewThreads(first: 100) {
          totalCount
          nodes {
            isResolved
            comments {
              totalCount
            }
          }
        }
      }
    }
  }
' | jq '{
  total_threads: .data.repository.pullRequest.reviewThreads.totalCount,
  resolved: [.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved)] | length,
  unresolved: [.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved | not)] | length,
  total_comments: [.data.repository.pullRequest.reviewThreads.nodes[].comments.totalCount] | add
}'
```

### Example: Find Threads Needing PR Author Response

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: 123) {
        author { login }
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            path
            line
            comments(first: 50) {
              nodes {
                author { login }
                body
              }
            }
          }
        }
      }
    }
  }
'
```

Then process in Python to find threads where PR author hasn't replied.
